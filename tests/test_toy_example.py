"""Kiểm tra ví dụ tính tay dùng đúng các cây, phiếu và tập OOB."""

import json
import unittest

import numpy as np
from sklearn.tree import DecisionTreeClassifier

from examples.toy_bagging import build_toy_example, render_markdown


class ToyBaggingExampleTests(unittest.TestCase):
    def setUp(self):
        self.example = build_toy_example()

    def test_learned_thresholds_and_votes_match_hand_calculation(self):
        trees = self.example["trees"]
        self.assertEqual([tree["threshold"] for tree in trees], [2.5, 3.0, 2.5])
        self.assertEqual(self.example["query"]["tree_predictions"], [0, 1, 0])
        self.assertEqual(self.example["query"]["vote_counts"], {"0": 2, "1": 1})
        self.assertEqual(self.example["query"]["prediction"], 0)
        for tree, before in zip(trees, [.48, .48, .32]):
            self.assertAlmostEqual(tree["gini_before"], before)
            self.assertEqual(tree["gini_after"], 0)
            self.assertAlmostEqual(tree["gini_gain"], before)
            self.assertEqual(tree["left_size"] + tree["right_size"], 5)

    def test_oob_votes_only_come_from_trees_that_excluded_the_row(self):
        data = self.example["dataset"]
        X = np.array(data["feature_values"]).reshape(-1, 1)
        y = np.array(data["labels"])
        expected_predictions = {0: 1, 1: None, 2: 1, 3: 0, 4: None}
        for row in self.example["oob"]["rows"]:
            index = row["index"]
            expected_votes = np.zeros(2, dtype=int)
            expected_names = []
            for tree in self.example["trees"]:
                indices = tree["bootstrap_indices"]
                if index not in indices:
                    expected_names.append(tree["name"])
                    model = DecisionTreeClassifier(max_depth=1, random_state=1).fit(X[indices], y[indices])
                    expected_votes[int(model.predict(X[index:index + 1])[0])] += 1
            self.assertEqual(row["eligible_trees"], expected_names)
            self.assertEqual(row["vote_counts"], {"0": int(expected_votes[0]), "1": int(expected_votes[1])})
            self.assertEqual(row["prediction"], expected_predictions[index])
        self.assertEqual(self.example["oob"]["covered_samples"], 3)
        self.assertEqual(self.example["oob"]["correct_samples"], 2)
        self.assertAlmostEqual(self.example["oob"]["coverage"], 3 / 5)
        self.assertAlmostEqual(self.example["oob"]["accuracy"], 2 / 3)

    def test_uncovered_rows_stay_undefined_and_export_is_standard_json(self):
        for index in [1, 4]:
            row = self.example["oob"]["rows"][index]
            self.assertIsNone(row["prediction"])
            self.assertIsNone(row["correct"])
            self.assertEqual(row["tree_predictions"], [])
        self.assertEqual(json.loads(json.dumps(self.example, allow_nan=False)), self.example)
        self.assertIn("giả lập", render_markdown(self.example))
        self.assertIn("60%", render_markdown(self.example))


if __name__ == "__main__":
    unittest.main()
