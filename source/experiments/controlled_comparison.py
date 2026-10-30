"""Controlled feature/aggregation study on seed42 TRAIN only; no test tuning.

Run: .venv/bin/python experiments/controlled_comparison.py
Reuse the original bootstraps and per-tree seeds across feature settings.
"""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, recall_score
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.tree import DecisionTreeClassifier

from de_5_ensemble_learning import select_depth
from ensemble_model import ManualBagging
from experiments.report_extensions import write_csv


def aggregate_trees(trees, X, n_classes=2):
    """Trees learn globally encoded labels, possibly seeing only one class."""
    votes = np.zeros((len(X), n_classes), dtype=np.int64)
    probabilities = np.zeros((len(X), n_classes), dtype=float)
    for tree in trees:
        predicted = tree.predict(X).astype(int)
        np.add.at(votes, (np.arange(len(X)), predicted), 1)
        probabilities[:, tree.classes_.astype(int)] += tree.predict_proba(X)
    return {"votes": votes, "mean_probabilities": probabilities / len(trees),
            "hard": votes.argmax(axis=1), "soft": probabilities.argmax(axis=1)}


def pair_disagreement(votes):
    """Fraction of unordered tree pairs giving different hard labels, mean over X."""
    votes = np.asarray(votes)
    count = votes.sum(axis=1)
    if np.any(count < 2) or not np.all(count == count[0]):
        raise ValueError("Need a common count >=2 trees for all observations")
    return float(np.mean((count**2 - np.sum(votes**2, axis=1)) / (count * (count - 1))))


def controlled_study(X_train, y_train, count=51, seed=42):
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    records, fold_info = [], []
    for fold, (fit, validation) in enumerate(folds.split(X_train, y_train), 1):
        depth, _ = select_depth(X_train[fit], y_train[fit], seed + fold)
        reference = ManualBagging(n_estimators=count, max_depth=depth,
                                  random_state=seed + fold, oob_score=False)
        reference.fit(X_train[fit], y_train[fit])
        encoded = np.searchsorted(reference.classes_, y_train[fit])
        feature_sampled = []
        for original, indices in zip(reference.estimators_, reference.estimators_samples_):
            tree = DecisionTreeClassifier(max_depth=depth, max_features="sqrt",
                                          random_state=original.random_state)
            tree.fit(X_train[fit][indices], encoded[indices])
            feature_sampled.append(tree)
        fold_info.append({"fold": fold, "seed": seed + fold, "depth": int(depth),
                          "fit_indices": fit.tolist(), "validation_indices": validation.tolist(),
                          "matching_tree_seeds": all(a.random_state == b.random_state for a, b
                                                     in zip(reference.estimators_, feature_sampled))})
        for features, trees in [("all", reference.estimators_), ("sqrt", feature_sampled)]:
            result = aggregate_trees(trees, X_train[validation], len(reference.classes_))
            disagreement = pair_disagreement(result["votes"])
            individual = np.mean([balanced_accuracy_score(
                y_train[validation], reference.classes_[t.predict(X_train[validation]).astype(int)])
                                  for t in trees])
            changed = int(np.sum(result["hard"] != result["soft"]))
            for aggregation in ("hard", "soft"):
                prediction = reference.classes_[result[aggregation]]
                truth = y_train[validation]
                records.append({"fold": fold, "depth": int(depth), "features": features,
                                "aggregation": aggregation, "n_estimators": count,
                                "n_validation": len(validation),
                                "accuracy": float(accuracy_score(truth, prediction)),
                                "balanced_accuracy": float(balanced_accuracy_score(truth, prediction)),
                                "recall_malignant": float(recall_score(truth, prediction, pos_label=0)),
                                "f1_malignant": float(f1_score(truth, prediction, pos_label=0)),
                                "mean_tree_balanced_accuracy": float(individual),
                                "pair_disagreement": disagreement,
                                "hard_soft_changed_predictions": changed})
    summary = []
    for features in ("all", "sqrt"):
        for aggregation in ("hard", "soft"):
            rows = [r for r in records if r["features"] == features and r["aggregation"] == aggregation]
            result = {"features": features, "aggregation": aggregation, "n_estimators": count, "n_folds": 5}
            for metric in ("accuracy", "balanced_accuracy", "recall_malignant", "f1_malignant",
                           "mean_tree_balanced_accuracy", "pair_disagreement"):
                values = np.array([r[metric] for r in rows])
                result[metric + "_mean"] = float(values.mean())
                result[metric + "_std"] = float(values.std(ddof=1))
            result["hard_soft_changed_total"] = sum(r["hard_soft_changed_predictions"] for r in rows)
            summary.append(result)
    paired = []
    contrasts = [
        ("soft_minus_hard_all", ("all", "soft"), ("all", "hard")),
        ("soft_minus_hard_sqrt", ("sqrt", "soft"), ("sqrt", "hard")),
        ("sqrt_minus_all_hard", ("sqrt", "hard"), ("all", "hard")),
        ("sqrt_minus_all_soft", ("sqrt", "soft"), ("all", "soft")),
    ]
    for name, a, b in contrasts:
        differences = []
        for fold in range(1, 6):
            lookup = {(r["features"], r["aggregation"]): r for r in records if r["fold"] == fold}
            differences.append(lookup[a]["balanced_accuracy"] - lookup[b]["balanced_accuracy"])
        paired.append({"contrast": name, "balanced_accuracy_differences": differences,
                       "mean_difference": float(np.mean(differences)),
                       "sample_sd": float(np.std(differences, ddof=1)),
                       "positive_folds": sum(d > 0 for d in differences),
                       "zero_folds": sum(d == 0 for d in differences)})
    return {"folds": fold_info, "records": records, "summary": summary, "paired_contrasts": paired}


def main():
    original_path = ROOT / "outputs/results.json"
    if not original_path.is_file():
        raise SystemExit("Chạy python de_5_ensemble_learning.py để tạo kết quả gốc trước.")
    original = json.loads(original_path.read_text(encoding="utf-8"))
    if (original.get("seed") != 42 or original.get("n_estimators") != 51
            or original.get("train_size") != 426
            or original.get("repeated_evaluation", {}).get("seeds") != list(range(42, 52))):
        raise SystemExit("Cần kết quả mặc định 10seed42–51; chạy python de_5_ensemble_learning.py.")
    data = load_breast_cancer()
    train, test = train_test_split(np.arange(len(data.target)), test_size=.25,
                                   stratify=data.target, random_state=42)
    result = controlled_study(data.data[train], data.target[train])
    result["protocol"] = {"seed": 42, "n_train": len(train), "n_test_excluded": len(test),
                          "train_indices": train.tolist(), "test_indices": test.tolist(),
                          "outer_folds": 5, "inner_folds": 5, "candidate_depths": [2, 3, 4, 5, 6],
                          "matching_bootstraps": True, "matching_per_tree_seeds": True,
                          "note": "Post-hoc train-only controlled diagnostic, not new test evaluation. sqrt variants are custom ensembles, not sklearn RandomForestClassifier."}
    original_paired = []
    for other in ("Decision Tree", "Random Forest (sklearn)"):
        differences = []
        for run in original["repeated_evaluation"]["runs"]:
            lookup = {r["model"]: r for r in run["test_metrics"]}
            differences.append(lookup["Manual Bagging"]["accuracy"] - lookup[other]["accuracy"])
        original_paired.append({"comparison": "Manual Bagging minus " + other,
                                "accuracy_differences": differences,
                                "mean_difference": float(np.mean(differences)),
                                "wins": sum(d > 0 for d in differences),
                                "ties": sum(d == 0 for d in differences),
                                "losses": sum(d < 0 for d in differences)})
    result["original_paired_comparisons"] = original_paired
    baseline = ManualBagging(n_estimators=51, max_depth=original["selected_depth"], random_state=42)
    baseline.fit(data.data[train], data.target[train])
    unique_counts = np.array([len(np.unique(i)) for i in baseline.estimators_samples_])
    N = len(train)
    q = (1 - 1/N)**N
    result["bootstrap_check"] = {"n_train": N, "n_estimators": 51,
                                  "theoretical_oob_probability": q,
                                  "expected_distinct_rows": N * (1 - q),
                                  "observed_mean_distinct_rows": float(unique_counts.mean()),
                                  "observed_min_distinct_rows": int(unique_counts.min()),
                                  "observed_max_distinct_rows": int(unique_counts.max()),
                                  "expected_oob_votes_per_row": 51 * q,
                                  "observed_mean_oob_votes_per_row": float(baseline.oob_counts_.mean())}
    output = ROOT / "outputs/extensions"
    output.mkdir(parents=True, exist_ok=True)
    (output / "controlled_comparison.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    write_csv(output / "controlled_comparison_folds.csv", result["records"])
    write_csv(output / "controlled_comparison_summary.csv", result["summary"])
    print(json.dumps({"summary": result["summary"], "paired": result["paired_contrasts"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
