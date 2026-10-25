"""Regression and end-to-end checks for the actual assignment workflow."""

import csv
from contextlib import redirect_stderr
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from numpy.testing import assert_array_equal
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

import de_5_ensemble_learning as workflow

ROOT = Path(__file__).resolve().parents[1]


class ReferenceWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_breast_cancer()
        with patch.object(workflow, "select_depth", wraps=workflow.select_depth) as select:
            cls.experiment = workflow.run_experiment(cls.data, seed=42)
            cls.tuning_X = select.call_args.args[0]
            cls.tuning_y = select.call_args.args[1]

    def test_depth_tuning_receives_only_the_outer_training_partition(self):
        train, test = train_test_split(
            np.arange(len(self.data.target)), test_size=.25,
            stratify=self.data.target, random_state=42,
        )
        self.assertFalse(set(train) & set(test))
        assert_array_equal(self.tuning_X, self.data.data[train])
        assert_array_equal(self.tuning_y, self.data.target[train])
        assert_array_equal(self.experiment.test_indices, test)

    def test_reference_results_and_positive_class_are_preserved(self):
        self.assertEqual(self.experiment.depth, 3)
        self.assertEqual((len(self.experiment.y_train), len(self.experiment.y_test)), (426, 143))
        expected = [(48, 5, 3, 87), (49, 4, 3, 87), (49, 4, 3, 87)]
        for row, counts in zip(self.experiment.metrics, expected):
            with self.subTest(model=row["model"]):
                self.assertEqual(tuple(row[key] for key in ["tp", "fn", "fp", "tn"]), counts)
                tp, fn, fp, tn = counts
                self.assertAlmostEqual(row["recall_malignant"], tp / (tp + fn))
                self.assertAlmostEqual(row["specificity_benign"], tn / (tn + fp))
                self.assertAlmostEqual(row["accuracy"], (tp + tn) / 143)

    def test_oob_reference_and_first_disagreement_are_honest(self):
        model = self.experiment.models["Manual Bagging"]
        self.assertAlmostEqual(model.oob_score_, 401 / 426)
        self.assertEqual(model.oob_coverage_, 1)
        positions = np.flatnonzero((model.votes(self.experiment.X_test) > 0).sum(axis=1) > 1)
        self.assertEqual(len(positions), 45)
        trace = workflow.make_trace(self.experiment, self.data, int(positions[0]))
        self.assertEqual(trace["test_position"], 2)
        self.assertEqual(trace["dataset_row"], 291)
        self.assertEqual(trace["all_tree_votes"], {"malignant": 27, "benign": 24})
        self.assertEqual(trace["true_class"], "benign")
        self.assertEqual(trace["ensemble_prediction"], "malignant")
        self.assertFalse(trace["correct"])


class ExportAndSummaryTests(unittest.TestCase):
    def test_summary_uses_sample_sd_and_single_run_has_no_sd(self):
        rows = [{"model": "example", **dict.fromkeys(workflow.METRICS, value)} for value in [.8, 1.0]]
        summary = workflow.summarize(rows)[0]
        self.assertEqual(summary["n_runs"], 2)
        self.assertAlmostEqual(summary["accuracy_mean"], .9)
        self.assertAlmostEqual(summary["accuracy_std"], np.sqrt(.02))
        single = workflow.summarize(rows[:1])[0]
        self.assertIsNone(single["accuracy_std"])
        # Std N/A must serialize as JSON null, never non-standard NaN.
        json.dumps(single, allow_nan=False)

    def test_cli_exports_all_artifacts_with_custom_tree_count(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            output = folder / "results"
            env = {**os.environ, "MPLCONFIGDIR": str(folder / "mpl"), "XDG_CACHE_HOME": str(folder / "cache")}
            completed = subprocess.run(
                [sys.executable, str(ROOT / "de_5_ensemble_learning.py"), "--repeats", "1",
                 "--n-estimators", "1", "--seed", "7", "--output-dir", str(output)],
                cwd=temp, env=env, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            expected = {
                "results.json", "metrics.csv", "classification_report.json", "confusion_matrices.png",
                "predictions.csv", "repeated_metrics.csv", "summary_metrics.csv", "voting_example.png",
                "stability.png", "report.md",
            }
            self.assertEqual({path.name for path in output.iterdir()}, expected)
            report = json.loads((output / "results.json").read_text(encoding="utf-8"))
            self.assertEqual(report["n_estimators"], 1)
            self.assertEqual(report["repeated_evaluation"]["seeds"], [7])
            self.assertIsNone(report["repeated_evaluation"]["summary"][0]["accuracy_std"])
            self.assertIsNone(report["disagreement_example"])
            self.assertNotIn("all_51_votes", report["worked_example"])
            self.assertEqual(sum(report["worked_example"]["all_tree_votes"].values()), 1)
            with (output / "predictions.csv").open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(len(rows), 143)
            self.assertTrue(all(int(row["votes_malignant"]) + int(row["votes_benign"]) == 1 for row in rows))
            for filename in ("confusion_matrices.png", "voting_example.png", "stability.png"):
                self.assertEqual((output / filename).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_invalid_cli_arguments_fail_before_creating_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "must_not_exist"
            for options in (["--repeats", "0"], ["--n-estimators", "0"], ["--seed", "-1"]):
                with self.subTest(options=options), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    workflow.main([*options, "--output-dir", str(output)])
                self.assertEqual(error.exception.code, 2)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
