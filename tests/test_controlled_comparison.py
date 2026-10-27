"""Check voting/probability alignment and the diversity measurement."""

import unittest

import numpy as np

from experiments.controlled_comparison import aggregate_trees, pair_disagreement


class FixedTree:
    def __init__(self, classes, probabilities):
        self.classes_ = np.array(classes)
        self.probabilities = np.array(probabilities)

    def predict(self, X):
        return np.full(len(X), self.classes_[self.probabilities.argmax()])

    def predict_proba(self, X):
        return np.tile(self.probabilities, (len(X), 1))


class ControlledComparisonTests(unittest.TestCase):
    def test_same_trees_can_produce_opposite_hard_and_soft_labels(self):
        trees = [FixedTree([0, 1], [.51, .49]), FixedTree([0, 1], [.51, .49]),
                 FixedTree([0, 1], [.01, .99])]
        result = aggregate_trees(trees, [[1]])
        np.testing.assert_array_equal(result["votes"], [[2, 1]])
        np.testing.assert_array_equal(result["hard"], [0])
        np.testing.assert_array_equal(result["soft"], [1])
        np.testing.assert_allclose(result["mean_probabilities"], [[1.03/3, 1.97/3]])
        self.assertAlmostEqual(pair_disagreement(result["votes"]), 2/3)

    def test_single_class_trees_keep_global_probability_column(self):
        result = aggregate_trees([FixedTree([1], [1.]), FixedTree([1], [1.])], [[1], [2]])
        np.testing.assert_array_equal(result["votes"], [[0, 2], [0, 2]])
        np.testing.assert_allclose(result["mean_probabilities"], [[0, 1], [0, 1]])
        self.assertEqual(pair_disagreement(result["votes"]), 0.)
        with self.assertRaises(ValueError):
            pair_disagreement([[1, 0]])


if __name__ == "__main__":
    unittest.main()
