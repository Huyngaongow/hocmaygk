"""Behavioral checks for the educational hard-voting Bagging estimator.

Run from the repository root: python -m unittest discover -s tests -v
No network or optional testing dependencies are needed.
"""

import unittest
import warnings

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal
from sklearn.base import clone
from sklearn.exceptions import NotFittedError
from sklearn.model_selection import StratifiedKFold, cross_val_score

from ensemble_model import ManualBagging


class ConstantEncodedTree:
    """Minimal tree stand-in to construct a real two-class vote tie."""

    def __init__(self, label):
        self.label = label

    def predict(self, X):
        return np.full(len(X), self.label, dtype=int)


class ManualBaggingTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(7)
        self.X = rng.normal(size=(36, 3))
        self.y = np.where(self.X[:, 0] > 0, 17, 4)

    def fitted(self, **kwargs):
        params = {"n_estimators": 11, "random_state": 42}
        params.update(kwargs)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            return ManualBagging(**params).fit(self.X, self.y)

    def test_prediction_before_fit_is_an_explicit_error(self):
        model = ManualBagging()
        for method in (model.predict, model.votes, model.predict_vote_fraction):
            with self.subTest(method=method.__name__):
                with self.assertRaises(NotFittedError):
                    method(self.X)

    def test_bad_hyperparameters_are_rejected(self):
        invalid = [
            {"n_estimators": 0},
            {"n_estimators": -1},
            {"n_estimators": 1.5},
            {"max_depth": 0},
            {"max_depth": -2},
            {"max_depth": 1.5},
        ]
        for params in invalid:
            with self.subTest(params=params):
                with self.assertRaises((ValueError, TypeError)):
                    ManualBagging(**params).fit(self.X, self.y)

    def test_input_shape_and_nonfinite_data_are_rejected(self):
        bad_X = self.X.copy()
        bad_X[0, 0] = np.nan
        cases = [(self.X, self.y[:-1]), (bad_X, self.y), ([], [])]
        for X, y in cases:
            with self.subTest(shape=np.shape(X)):
                with self.assertRaises(ValueError):
                    ManualBagging().fit(X, y)
        model = self.fitted()
        for invalid_X in (self.X[:, :2], bad_X):
            with self.subTest(prediction_shape=invalid_X.shape):
                with self.assertRaises(ValueError):
                    model.predict(invalid_X)

    def test_list_inputs_and_string_labels_round_trip(self):
        y = np.where(self.y == 17, "malignant", "benign")
        model = ManualBagging(n_estimators=7).fit(self.X.tolist(), y.tolist())
        predicted = model.predict(self.X[:5].tolist())
        self.assertEqual(predicted.shape, (5,))
        self.assertTrue(set(predicted).issubset(set(y)))
        assert_array_equal(model.classes_, ["benign", "malignant"])

    def test_hard_votes_are_counts_for_every_original_label(self):
        model = self.fitted()
        votes = model.votes(self.X)
        self.assertEqual(votes.shape, (len(self.X), 2))
        self.assertTrue(np.issubdtype(votes.dtype, np.integer))
        assert_array_equal(votes.sum(axis=1), np.full(len(self.X), 11))
        predictions = model.predict(self.X)
        self.assertTrue(set(predictions).issubset({4, 17}))
        assert_array_equal(predictions, model.classes_[votes.argmax(axis=1)])
        fractions = model.predict_vote_fraction(self.X)
        assert_allclose(fractions, votes / 11)
        assert_allclose(fractions.sum(axis=1), 1)

    def test_tree_that_saw_one_class_keeps_global_label_mapping(self):
        X = [[0.0], [1.0]]
        y = [90, -10]
        found = False
        for seed in range(20):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                model = ManualBagging(n_estimators=1, random_state=seed).fit(X, y)
            tree = model.estimators_[0]
            if len(tree.classes_) == 1:
                encoded_label = int(tree.classes_[0])
                expected_label = model.classes_[encoded_label]
                assert_array_equal(model.predict(X), [expected_label] * 2)
                expected_votes = np.zeros((2, 2), dtype=int)
                expected_votes[:, encoded_label] = 1
                assert_array_equal(model.votes(X), expected_votes)
                found = True
                break
        self.assertTrue(found, "The deterministic seeds must exercise a one-class bootstrap")

    def test_equal_votes_choose_first_sorted_class(self):
        model = self.fitted(n_estimators=2)
        model.estimators_ = [ConstantEncodedTree(1), ConstantEncodedTree(0)]
        assert_array_equal(model.votes(self.X[:3]), np.ones((3, 2), dtype=int))
        assert_array_equal(model.predict(self.X[:3]), np.full(3, 4))

    def test_bootstrap_samples_have_train_size_and_replacement(self):
        model = self.fitted()
        self.assertEqual(len(model.estimators_samples_), 11)
        self.assertEqual(model.n_features_in_, self.X.shape[1])
        for indices in model.estimators_samples_:
            self.assertEqual(len(indices), len(self.X))
            self.assertTrue(np.all((indices >= 0) & (indices < len(self.X))))
        self.assertTrue(any(len(np.unique(i)) < len(self.X)
                            for i in model.estimators_samples_))

    def test_same_seed_reproduces_bootstraps_and_predictions(self):
        first = self.fitted()
        second = self.fitted()
        assert_array_equal(first.predict(self.X), second.predict(self.X))
        assert_array_equal(first.oob_vote_counts_, second.oob_vote_counts_)
        for a, b in zip(first.estimators_samples_, second.estimators_samples_):
            assert_array_equal(a, b)

    def test_refit_replaces_previous_state(self):
        model = self.fitted()
        original = [idx.copy() for idx in model.estimators_samples_]
        model.fit(self.X, self.y)
        self.assertEqual(len(model.estimators_), 11)
        for a, b in zip(original, model.estimators_samples_):
            assert_array_equal(a, b)
        new_y = np.where(self.y == 17, "yes", "no")
        model.fit(self.X, new_y)
        assert_array_equal(model.classes_, ["no", "yes"])
        self.assertEqual(len(model.estimators_), 11)
        self.assertTrue(set(model.predict(self.X)).issubset({"no", "yes"}))

    def test_oob_only_uses_trees_that_excluded_each_observation(self):
        model = self.fitted()
        expected_votes = np.zeros((len(self.X), 2), dtype=int)
        expected_counts = np.zeros(len(self.X), dtype=int)
        for tree, sampled in zip(model.estimators_, model.estimators_samples_):
            omitted = sorted(set(range(len(self.X))) - set(sampled))
            if omitted:
                predictions = tree.predict(self.X[omitted]).astype(int)
                np.add.at(expected_votes, (omitted, predictions), 1)
                expected_counts[omitted] += 1
        assert_array_equal(model.oob_counts_, expected_counts)
        assert_array_equal(model.oob_vote_counts_, expected_votes)
        covered = expected_counts > 0
        self.assertGreater(covered.sum(), 0)
        assert_allclose(model.oob_decision_function_[covered],
                        expected_votes[covered] / expected_counts[covered, None])
        expected_prediction = model.classes_[expected_votes[covered].argmax(axis=1)]
        self.assertAlmostEqual(model.oob_score_, np.mean(expected_prediction == self.y[covered]))
        self.assertAlmostEqual(model.oob_coverage_, covered.mean())

    def test_oob_uncovered_rows_are_not_confident_predictions(self):
        model = self.fitted(n_estimators=1)
        missing = model.oob_counts_ == 0
        self.assertTrue(missing.any())
        self.assertTrue(np.isnan(model.oob_decision_function_[missing]).all())
        self.assertLess(model.oob_coverage_, 1)

    def test_sklearn_clone_and_cross_validation_work(self):
        estimator = ManualBagging(n_estimators=5, oob_score=False, random_state=3)
        copied = clone(estimator)
        self.assertEqual(copied.get_params(), estimator.get_params())
        folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=3)
        scores = cross_val_score(copied, self.X, self.y, cv=folds, scoring="accuracy")
        self.assertEqual(len(scores), 3)
        self.assertTrue(np.isfinite(scores).all())
        self.assertGreater(scores.mean(), 0.6)


if __name__ == "__main__":
    unittest.main()
