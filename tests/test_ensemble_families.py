"""Check cross-fitting boundaries and scientific conventions of the extension."""

from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

from de_5_ensemble_learning import evaluate, summarize
from experiments.ensemble_families import (
    MODEL_NAMES, build_models, export_result, run_family_experiment, validate_seeds,
)


class FixedPrediction:
    def predict(self, X):
        return np.array([0, 1, 1, 0, 1, 1])


class EnsembleFamilyTests(unittest.TestCase):
    def test_metrics_treat_malignant_zero_as_positive(self):
        row = evaluate("fixed", FixedPrediction(), np.zeros((6, 1)), [0, 0, 0, 1, 1, 1])
        self.assertEqual([row[k] for k in ("tp", "fn", "fp", "tn")], [1, 2, 1, 2])
        self.assertAlmostEqual(row["recall_malignant"], 1/3)
        self.assertAlmostEqual(row["specificity_benign"], 2/3)
        self.assertAlmostEqual(row["f1_malignant"], 2/5)

    def test_stacking_scaler_fits_only_current_fold(self):
        rng = np.random.default_rng(9)
        X = rng.normal(size=(60, 4)); X[:, 0] = np.arange(60)
        y = np.tile([0, 1], 30)
        fitted_rows = []
        original_fit = StandardScaler.fit

        def tracked_fit(scaler, values, y=None, sample_weight=None):
            fitted_rows.append(tuple(sorted(np.asarray(values)[:, 0].astype(int))))
            return original_fit(scaler, values, y, sample_weight=sample_weight)

        with patch.object(StandardScaler, "fit", tracked_fit):
            build_models(42)["Stacking"].fit(X, y)
        expected = [tuple(range(60))]  # Refit base on all outer train for prediction.
        for fit, _ in StratifiedKFold(5, shuffle=True, random_state=42).split(X, y):
            expected.append(tuple(sorted(fit.tolist())))
        self.assertEqual(Counter(fitted_rows), Counter(expected))

    def test_voting_rules_use_identical_fitted_bases(self):
        data = load_breast_cancer()
        models = build_models(42)
        hard, soft = models["Voting (hard)"], models["Voting (soft)"]
        hard.fit(data.data[:150], data.target[:150])
        soft.fit(data.data[:150], data.target[:150])
        for a, b in zip(hard.estimators_, soft.estimators_):
            np.testing.assert_allclose(a.predict_proba(data.data[150:]),
                                       b.predict_proba(data.data[150:]), rtol=0, atol=1e-12)

    def test_outer_test_is_excluded_from_all_stacking_folds(self):
        run, split = run_family_experiment(load_breast_cancer(), 42)
        train, test = set(split["train_indices"]), set(split["test_indices"])
        self.assertEqual((len(train), len(test)), (426, 143))
        self.assertFalse(train & test)
        validation = []
        for fold in split["stacking_folds"]:
            fit, heldout = set(fold["fit_indices"]), set(fold["validation_indices"])
            self.assertEqual(fit | heldout, train)
            self.assertFalse(fit & heldout)
            self.assertFalse((fit | heldout) & test)
            validation.extend(heldout)
        self.assertEqual(Counter(validation), Counter({i: 1 for i in train}))
        self.assertEqual(tuple(row["model"] for row in run["test_metrics"]), MODEL_NAMES)
        for row in run["test_metrics"]:
            self.assertEqual(sum(row[k] for k in ("tp", "fn", "fp", "tn")), 143)
        self.assertEqual(run["selected_depth"], 3)

    def test_one_run_export_has_null_sd_and_full_artifacts(self):
        rows = [{"model": name, "accuracy": .9, "balanced_accuracy": .9,
                 "precision_malignant": .9, "recall_malignant": .9,
                 "specificity_benign": .9, "f1_malignant": .9,
                 "tp": 9, "fn": 1, "fp": 1, "tn": 9} for name in MODEL_NAMES]
        result = {"protocol": {"seeds": [42]}, "records": rows, "summary": summarize(rows)}
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            export_result(result, folder)
            self.assertEqual({p.name for p in folder.iterdir()}, {
                "family_comparison.json", "family_comparison_runs.csv",
                "family_comparison_summary.csv", "family_comparison.png",
                "family_comparison.pdf", "family_comparison.md"})
            encoded = (folder / "family_comparison.json").read_text()
            self.assertNotIn("NaN", encoded)
            self.assertIsNone(json.loads(encoded)["summary"][0]["accuracy_std"])

    def test_invalid_seed_ranges_fail_explicitly(self):
        for invalid in ([], [-1], [2**32], [42, 42], [True], [1.5]):
            with self.subTest(seeds=invalid), self.assertRaises(ValueError):
                validate_seeds(invalid)


if __name__ == "__main__":
    unittest.main()
