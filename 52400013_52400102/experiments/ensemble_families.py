"""Illustrate four ensemble families with fixed, reproducible configurations.

Run from the repository root: python experiments/ensemble_families.py
This is a post-hoc descriptive extension; it does not replace the Bagging study.
"""

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import AdaBoostClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from de_5_ensemble_learning import evaluate, run_experiment, summarize, write_csv, write_json


MODEL_NAMES = (
    "Decision Tree", "Manual Bagging", "Random Forest (sklearn)",
    "Decision Tree (depth=3)", "Logistic Regression", "Gaussian NB",
    "AdaBoost", "Voting (hard)", "Voting (soft)", "Stacking",
)
ENSEMBLE_NAMES = (
    "Manual Bagging", "Random Forest (sklearn)", "AdaBoost",
    "Voting (hard)", "Voting (soft)", "Stacking",
)


def build_base_estimators(seed):
    """Fresh, unfitted fixed configurations; scaling stays inside each fit/fold."""
    return [
        ("tree", DecisionTreeClassifier(max_depth=3, random_state=seed)),
        ("lr", make_pipeline(StandardScaler(), LogisticRegression(
            max_iter=2000, random_state=seed))),
        ("nb", GaussianNB()),
    ]


def build_models(seed):
    """No search over these configurations or use of outer test labels."""
    base = build_base_estimators(seed)
    return {
        "Decision Tree (depth=3)": clone(base[0][1]),
        "Logistic Regression": clone(base[1][1]),
        "Gaussian NB": clone(base[2][1]),
        "AdaBoost": AdaBoostClassifier(
            estimator=DecisionTreeClassifier(max_depth=1, random_state=seed),
            n_estimators=51, learning_rate=1.0, random_state=seed),
        "Voting (hard)": VotingClassifier(
            estimators=build_base_estimators(seed), voting="hard", n_jobs=1),
        "Voting (soft)": VotingClassifier(
            estimators=build_base_estimators(seed), voting="soft", n_jobs=1),
        "Stacking": StackingClassifier(
            estimators=build_base_estimators(seed),
            final_estimator=LogisticRegression(max_iter=2000, random_state=seed),
            cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=seed),
            stack_method="predict_proba", passthrough=False, n_jobs=1),
    }


def validate_seeds(seeds):
    seeds = list(seeds)
    if not seeds or any(isinstance(s, bool) or not isinstance(s, (int, np.integer))
                        or not 0 <= s <= 2**32 - 1 for s in seeds):
        raise ValueError("Seeds must be nonempty integers in [0, 2**32-1].")
    if len(set(seeds)) != len(seeds):
        raise ValueError("Seeds must be distinct.")
    return [int(s) for s in seeds]


def run_family_experiment(data, seed):
    """All ten methods see the same split; only original tree depth uses train CV."""
    validate_seeds([seed])
    train, test = train_test_split(
        np.arange(len(data.target)), test_size=.25,
        stratify=data.target, random_state=seed)
    original = run_experiment(data, seed, n_estimators=51)
    np.testing.assert_array_equal(original.test_indices, test)
    np.testing.assert_array_equal(original.X_train, data.data[train])
    np.testing.assert_array_equal(original.y_train, data.target[train])
    X_train, X_test = data.data[train], data.data[test]
    y_train, y_test = data.target[train], data.target[test]
    models = build_models(seed)
    metrics = list(original.metrics)
    predictions = {name: model.predict(X_test).astype(int).tolist()
                   for name, model in original.models.items()}
    for name, model in models.items():
        model.fit(X_train, y_train)
        metrics.append(evaluate(name, model, X_test, y_test))
        predictions[name] = model.predict(X_test).astype(int).tolist()

    # With deterministic base configurations, both Voting rules must use the
    # same fitted base predictions/probabilities, not different random learners.
    for hard, soft in zip(models["Voting (hard)"].estimators_,
                          models["Voting (soft)"].estimators_):
        np.testing.assert_allclose(hard.predict_proba(X_test), soft.predict_proba(X_test),
                                   rtol=0, atol=1e-12)
    folds = [
        {"fold": fold, "fit_indices": train[fit].tolist(),
         "validation_indices": train[validation].tolist()}
        for fold, (fit, validation) in enumerate(
            models["Stacking"].cv.split(X_train, y_train), 1)
    ]
    split = {"seed": seed, "train_indices": train.tolist(), "test_indices": test.tolist(),
             "stacking_folds": folds}
    run = {"seed": seed, "selected_depth": original.depth,
           "test_metrics": metrics, "test_labels": y_test.astype(int).tolist(),
           "confusion_matrices": {m["model"]: [[m["tp"], m["fn"]], [m["fp"], m["tn"]]]
                                  for m in metrics},
           "predictions": predictions,
           "ada_n_estimators_fitted": len(models["AdaBoost"].estimators_),
           "voting_hard_soft_changed": int(np.sum(
               np.array(predictions["Voting (hard)"]) != predictions["Voting (soft)"]))}
    return run, split


def configuration_description():
    return {
        "original_reference": {
            "models": list(MODEL_NAMES[:3]), "n_estimators": 51,
            "depth": "single-tree 5-fold train CV from {2,3,4,5,6}, shared per seed"},
        "base_trio": {
            "tree": "DecisionTreeClassifier(max_depth=3, random_state=seed)",
            "lr": "StandardScaler -> LogisticRegression(max_iter=2000, random_state=seed)",
            "nb": "GaussianNB()"},
        "AdaBoost": {"algorithm": "SAMME (scikit-learn 1.8)", "max_rounds": 51,
                     "learning_rate": 1.0, "base_tree_max_depth": 1},
        "Voting (hard)": {"base_estimators": ["tree", "lr", "nb"], "weights": "equal"},
        "Voting (soft)": {"base_estimators": ["tree", "lr", "nb"], "weights": "equal"},
        "Stacking": {"base_estimators": ["tree", "lr", "nb"], "n_folds": 5,
                     "shuffle": True, "fold_seed": "outer seed", "stack_method": "predict_proba",
                     "passthrough": False,
                     "meta_model": "LogisticRegression(max_iter=2000, random_state=seed)",
                     "binary_meta_features": "P(class=1) from each base; sklearn drops first column"},
        "reason_for_fixed_new_tree": "Depth=3 is fixed for the new base trio; it is not selected using full outer-train labels before OOF prediction.",
    }


def run_study(seeds=range(42, 52), progress=False):
    seeds = validate_seeds(seeds)
    data = load_breast_cancer()
    runs, splits, records = [], [], []
    reference_path = ROOT / "outputs/results.json"
    original_bytes = reference_path.read_bytes() if reference_path.exists() else None
    saved_reference = json.loads(original_bytes) if original_bytes is not None else {}
    saved_runs = {r["seed"]: r for r in saved_reference.get("repeated_evaluation", {}).get("runs", [])}
    checked = []
    for seed in seeds:
        if progress:
            print(f"Seed {seed}: fitting 10 methods...", flush=True)
        run, split = run_family_experiment(data, seed)
        if seed in saved_runs and saved_reference.get("n_estimators") == 51:
            old = saved_runs[seed]
            if old["selected_depth"] != run["selected_depth"]:
                raise RuntimeError("Original selected depth changed; check pinned environment.")
            for before, after in zip(old["test_metrics"], run["test_metrics"][:3]):
                if before.keys() != after.keys() or any(
                    not np.isclose(before[k], after[k], rtol=0, atol=1e-12)
                    if isinstance(before[k], (int, float)) else before[k] != after[k]
                    for k in before):
                    raise RuntimeError("Original metrics changed; check pinned environment.")
            checked.append(seed)
        runs.append(run); splits.append(split)
        records.extend({"seed": seed, **m} for m in run["test_metrics"])
    if original_bytes is not None and reference_path.read_bytes() != original_bytes:
        raise RuntimeError("The original results.json must remain unchanged.")
    return {
        "schema_version": 1,
        "protocol": {
            "dataset": "Breast Cancer Wisconsin Diagnostic", "n_samples": 569, "n_features": 30,
            "seeds": seeds, "test_size": .25, "stratified": True,
            "n_train_per_seed": 426, "n_test_per_seed": 143,
            "positive_class": "malignant (0)", "confusion_matrix_order": [0, 1],
            "study_status": "post-hoc descriptive extension after the original Bagging study",
            "configuration_selection": "new configurations fixed before these runs; no search on test scores",
            "scope": "configurations differ; this is not an isolated causal comparison of ensemble families",
            "stacking_oof": "5-fold predictions within outer train; each scaler fits only its current fit fold",
            "standardization": "Only LR pipelines are scaled; trees and GaussianNB use original features",
            "probabilities": "Uncalibrated model probabilities; soft voting is not guaranteed to improve performance",
            "interpretation": "Mean +/- sample SD (ddof=1) across overlapping holdouts; not CI or significance test; not independent confirmation on new data",
            "original_reference_seeds_verified": checked,
            "original_results_sha256": hashlib.sha256(original_bytes).hexdigest() if original_bytes else None,
        },
        "configurations": configuration_description(),
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "scikit_learn": sklearn.__version__, "matplotlib": matplotlib.__version__},
        "splits": splits, "runs": runs, "records": records, "summary": summarize(records),
    }


def make_figure(result, output):
    rows = {row["model"]: row for row in result["summary"]}
    names = list(ENSEMBLE_NAMES)
    means = np.array([rows[n]["balanced_accuracy_mean"] for n in names]) * 100
    errors = np.array([rows[n]["balanced_accuracy_std"] or 0 for n in names]) * 100
    fig, ax = plt.subplots(figsize=(10.3, 4.5))
    positions = np.arange(len(names))
    ax.barh(positions, means, xerr=errors, color=["#087f82", "#416dc4", "#c86449", "#8aa79d", "#478e91", "#142d46"], capsize=3)
    for y, value, error in zip(positions, means, errors):
        ax.text(value + error + .12, y, f"{value:.2f}%", va="center", fontsize=10)
    ax.set_yticks(positions, names); ax.invert_yaxis()
    ax.set_xlim(0, 105); ax.set_xlabel("Balanced accuracy (%)")
    ax.set_title(f"{len(result['protocol']['seeds'])} stratified holdouts; error bars = sample SD, not CI")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=.15); ax.set_axisbelow(True)
    fig.tight_layout()
    for extension in ("png", "pdf"):
        fig.savefig(output / f"family_comparison.{extension}", dpi=240)
    plt.close(fig)


def export_result(result, output):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    write_json(output / "family_comparison.json", result)
    write_csv(output / "family_comparison_runs.csv", result["records"])
    write_csv(output / "family_comparison_summary.csv", result["summary"])
    make_figure(result, output)
    lines = ["# Mở rộng bốn hướng Ensemble Learning", "",
             "Cấu hình cố định; so sánh mô tả bổ sung sau thí nghiệm gốc. Không chọn mô hình theo test.", "",
             "Trung bình theo %, SD mẫu theo điểm phần trăm; các holdout có thể giao nhau.", "",
             "| Mô hình | Accuracy | Recall ác | F1 ác | Balanced accuracy |",
             "|---|---:|---:|---:|---:|"]
    for row in result["summary"]:
        values = []
        for metric in ("accuracy", "recall_malignant", "f1_malignant", "balanced_accuracy"):
            sd = row[metric + "_std"]
            values.append(f"{100*row[metric+'_mean']:.2f} ± {100*sd:.2f}" if sd is not None
                          else f"{100*row[metric+'_mean']:.2f} (SD chưa xác định)")
        lines.append("| " + " | ".join([row["model"], *values]) + " |")
    lines += ["", "Ba mô hình tham chiếu dùng độ sâu chọn bằng CV; cây trong Voting/Stacking cố định depth=3.",
              "AdaBoost dùng tối đa 51 cây depth=1; Voting/Stacking dùng cây depth=3, LR có StandardScaler và GaussianNB.",
              "Stacking học tầng hai từ dự đoán OOF 5 fold trong train; mọi bước scale nằm trong pipeline từng fold.",
              "Không suy ra một họ ensemble luôn tốt hơn từ các cấu hình này; đây không phải kiểm định hoặc xác nhận trên dữ liệu mới.", ""]
    (output / "family_comparison.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--repeats", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/extensions")
    args = parser.parse_args(argv)
    if args.repeats < 1:
        parser.error("--repeats must be >=1")
    if not 0 <= args.seed <= 2**32 - 1 or args.seed + args.repeats - 1 > 2**32 - 1:
        parser.error("seed range must fit [0, 2**32-1]")
    result = run_study(range(args.seed, args.seed + args.repeats), progress=True)
    export_result(result, args.output_dir)
    print(f"Saved {args.output_dir / 'family_comparison.json'}", flush=True)


if __name__ == "__main__":
    main()
