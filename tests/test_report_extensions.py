"""Check leakage boundaries and the explanation of a real tree decision."""

import unittest

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from experiments.report_extensions import explain_tree_path, survey_tree_counts


class ReportExtensionTests(unittest.TestCase):
    def test_depth_selection_only_receives_fit_part_of_each_outer_fold(self):
        X = np.column_stack([np.arange(36), np.arange(36) % 5]).astype(float)
        y = np.arange(36) % 2
        seen = []

        def depth_selector(fit_X, fit_y, seed):
            seen.append(set(fit_X[:, 0].astype(int)))
            return 2, {2: .5}

        result = survey_tree_counts(X, y, counts=(1, 3), n_splits=3,
                                    depth_selector=depth_selector)
        validation_rows = []
        for observed, split in zip(seen, result["folds"]):
            fit = set(split["fit_indices"])
            validation = set(split["validation_indices"])
            self.assertEqual(observed, fit)
            self.assertFalse(observed & validation)
            self.assertEqual(fit | validation, set(range(36)))
            validation_rows.extend(validation)
        self.assertEqual(sorted(validation_rows), list(range(36)))
        self.assertEqual(len(result["records"]), 6)
        self.assertEqual([r["n_estimators"] for r in result["summary"]], [1, 3])

    def test_path_explains_opposite_predictions_and_threshold_equality(self):
        X = np.arange(1, 6, dtype=float).reshape(-1, 1)
        y = np.array([1, 1, 0, 0, 0])
        tree = DecisionTreeClassifier(max_depth=1).fit(X[[0, 0, 1, 3, 4]], y[[0, 0, 1, 3, 4]])
        left = explain_tree_path(tree, [3], ["x"])
        right = explain_tree_path(tree, [3.1], ["x"])
        self.assertEqual(left["conditions"][0]["relation"], "<=")
        self.assertEqual(right["conditions"][0]["relation"], ">")
        self.assertEqual(left["prediction_encoded"], 1)
        self.assertEqual(right["prediction_encoded"], 0)
        self.assertEqual(left["leaf_class_fractions"], {"0": 0., "1": 1.})
        self.assertEqual(right["leaf_class_fractions"], {"0": 1., "1": 0.})


if __name__ == "__main__":
    unittest.main()
