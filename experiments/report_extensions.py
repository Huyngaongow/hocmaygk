"""Khảo sát số cây chỉ trên train và phân tích lỗi của mô hình gốc.

Run: .venv/bin/python experiments/report_extensions.py
Không đổi cấu hình hay số liệu test của thí nghiệm gốc.
"""

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, recall_score
from sklearn.model_selection import StratifiedKFold, train_test_split

from de_5_ensemble_learning import run_experiment, select_depth
from ensemble_model import ManualBagging


def survey_tree_counts(X_train, y_train, counts=(1, 5, 11, 21, 51, 101), seed=42,
                       n_splits=5, depth_selector=select_depth):
    """Chỉ nhận train; chọn lại depth bên trong phần học của từng fold ngoài."""
    folds = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    records, splits = [], []
    for fold, (fit, validation) in enumerate(folds.split(X_train, y_train), 1):
        depth, _ = depth_selector(X_train[fit], y_train[fit], seed + fold)
        splits.append({"fold": fold, "fit_indices": fit.tolist(),
                       "validation_indices": validation.tolist(), "selected_depth": int(depth)})
        # Cùng fold và seed cho các B: cùng chuỗi bootstrap, khác số cây.
        for count in counts:
            model = ManualBagging(n_estimators=count, max_depth=depth,
                                  random_state=seed + fold, oob_score=False)
            model.fit(X_train[fit], y_train[fit])
            predicted = model.predict(X_train[validation])
            truth = y_train[validation]
            records.append({"fold": fold, "n_estimators": count, "depth": int(depth),
                            "accuracy": float(accuracy_score(truth, predicted)),
                            "balanced_accuracy": float(balanced_accuracy_score(truth, predicted)),
                            "recall_malignant": float(recall_score(truth, predicted, pos_label=0)),
                            "f1_malignant": float(f1_score(truth, predicted, pos_label=0))})
    summaries = []
    for count in counts:
        rows = [r for r in records if r["n_estimators"] == count]
        row = {"n_estimators": count, "n_folds": n_splits}
        for metric in ("accuracy", "balanced_accuracy", "recall_malignant", "f1_malignant"):
            values = np.array([r[metric] for r in rows])
            row[metric + "_mean"] = float(values.mean())
            row[metric + "_std"] = float(values.std(ddof=1))
        summaries.append(row)
    return {"folds": splits, "records": records, "summary": summaries}


def explain_tree_path(tree, sample, feature_names):
    """Trả đúng nhánh và lá đã dùng; sklearn cây dùng đầu vào float32."""
    x = np.asarray(sample, dtype=np.float32).reshape(1, -1)
    path = tree.decision_path(x).indices
    leaf = int(tree.apply(x)[0])
    conditions = []
    for node in path:
        if node == leaf:
            continue
        feature = int(tree.tree_.feature[node])
        threshold = float(tree.tree_.threshold[node])
        conditions.append({"node": int(node), "feature_index": feature,
                           "feature": str(feature_names[feature]), "value": float(x[0, feature]),
                           "threshold": threshold,
                           "relation": "<=" if x[0, feature] <= threshold else ">"})
    weights = tree.tree_.value[leaf][0]
    probabilities = weights / weights.sum()
    return {"prediction_encoded": int(tree.predict(x)[0]), "leaf": leaf,
            "conditions": conditions,
            "leaf_samples": int(tree.tree_.n_node_samples[leaf]),
            "leaf_class_fractions": {str(int(c)): float(p) for c, p in zip(tree.classes_, probabilities)}}


def analyze_reference_error(data, run):
    model = run.models["Manual Bagging"]
    votes = model.votes(run.X_test)
    positions = np.flatnonzero((votes > 0).sum(axis=1) > 1)
    position = int(positions[0])  # Giữ cùng quy tắc chọn mẫu của báo cáo gốc.
    sample = run.X_test[position]
    trace_by_prediction = {}
    for number, tree in enumerate(model.estimators_, 1):
        predicted = int(tree.predict(sample.reshape(1, -1))[0])
        if str(predicted) not in trace_by_prediction:
            trace_by_prediction[str(predicted)] = {
                "tree_number": number, **explain_tree_path(tree, sample, data.feature_names)}
    # Các đặc trưng được root của mô hình train dùng nhiều nhất; không chọn theo nhãn mẫu lỗi.
    root_features = np.array([int(tree.tree_.feature[0]) for tree in model.estimators_])
    frequencies = np.bincount(root_features[root_features >= 0], minlength=len(data.feature_names))
    top = sorted(range(len(frequencies)), key=lambda f: (-frequencies[f], f))[:3]
    comparisons = []
    for feature in top:
        row = {"feature": str(data.feature_names[feature]), "value": float(sample[feature]),
               "root_uses": int(frequencies[feature])}
        for label, name in [(0, "malignant"), (1, "benign")]:
            values = run.X_train[run.y_train == label, feature]
            row[name + "_q25"] = float(np.quantile(values, .25))
            row[name + "_median"] = float(np.median(values))
            row[name + "_q75"] = float(np.quantile(values, .75))
        comparisons.append(row)
    wrong = model.predict(run.X_test) != run.y_test
    margin = np.abs(votes[:, 0] - votes[:, 1]) / len(model.estimators_)
    bagging_predictions = model.predict(run.X_test)
    forest_predictions = run.models["Random Forest (sklearn)"].predict(run.X_test)
    differing_positions = np.flatnonzero(bagging_predictions != forest_predictions)
    return {"test_position": position, "dataset_row": int(run.test_indices[position]),
            "true_label": int(run.y_test[position]), "prediction": int(model.predict(sample.reshape(1, -1))[0]),
            "votes": votes[position].tolist(), "vote_margin": float(margin[position]),
            "comparisons": comparisons, "representative_paths": trace_by_prediction,
            "baseline_predictions": {name: int(m.predict(sample.reshape(1, -1))[0])
                                     for name, m in run.models.items()},
            "bagging_rf_disagreements": [
                {"test_position": int(i), "dataset_row": int(run.test_indices[i]),
                 "true_label": int(run.y_test[i]), "bagging": int(bagging_predictions[i]),
                 "random_forest": int(forest_predictions[i])} for i in differing_positions],
            "test_error_count": int(wrong.sum()),
            "median_vote_margin_correct": float(np.median(margin[~wrong])),
            "median_vote_margin_wrong": float(np.median(margin[wrong]))}


def write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    output = ROOT / "outputs/extensions"
    output.mkdir(parents=True, exist_ok=True)
    data = load_breast_cancer()
    train_indices, test_indices = train_test_split(
        np.arange(len(data.target)), test_size=.25, stratify=data.target, random_state=42)
    survey = survey_tree_counts(data.data[train_indices], data.target[train_indices])
    # Phân tích test được thực hiện sau khảo sát; không gửi test cho hàm khảo sát.
    reference = run_experiment(data, 42)
    error = analyze_reference_error(data, reference)
    result = {"protocol": {"seed": 42, "train_size": len(train_indices), "test_size": len(test_indices),
                           "train_indices": train_indices.tolist(), "test_indices": test_indices.tolist(),
                           "outer_cv_folds": 5, "inner_cv_folds": 5,
                           "candidate_depths": [2, 3, 4, 5, 6],
                           "note": "Post-hoc supplementary analysis. Count survey uses train only; baseline B=51 unchanged. SD across folds is descriptive, not CI."},
              "tree_count_survey": survey, "reference_error": error}
    (output / "analysis.json").write_text(json.dumps(result, ensure_ascii=False, indent=2,
                                                    allow_nan=False), encoding="utf-8")
    write_csv(output / "tree_counts_folds.csv", survey["records"])
    write_csv(output / "tree_counts_summary.csv", survey["summary"])
    write_csv(output / "error_features.csv", error["comparisons"])
    write_csv(output / "bagging_rf_disagreements.csv", error["bagging_rf_disagreements"])
    plt.rcParams.update({"font.family": "Noto Sans", "font.size": 11})
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3))
    x = np.arange(len(survey["summary"]))
    for ax, metric, title in zip(axes, ["balanced_accuracy", "recall_malignant"],
                               ["Balanced accuracy CV", "Recall ác tính CV"]):
        means = np.array([r[metric + "_mean"] for r in survey["summary"]]) * 100
        stds = np.array([r[metric + "_std"] for r in survey["summary"]]) * 100
        ax.errorbar(x, means, yerr=stds, marker="o", color="#087E83", capsize=4)
        ax.set_xticks(x, [r["n_estimators"] for r in survey["summary"]])
        ax.set_xlabel("Số cây B")
        ax.set_ylabel("%")
        ax.set_title(title)
        ax.grid(alpha=.2)
    fig.suptitle("Khảo sát trên train — 5 fold ngoài; chọn depth trong từng fold học\nThanh sai số: SD giữa các fold, không phải khoảng tin cậy", fontsize=11)
    fig.tight_layout()
    fig.savefig(output / "tree_count_cv.png", dpi=300)
    fig.savefig(output / "tree_count_cv.pdf")
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for ax, row in zip(axes, error["comparisons"]):
        ax.boxplot([reference.X_train[reference.y_train == label,
                                     list(data.feature_names).index(row["feature"])] for label in [1, 0]],
                   tick_labels=["Train lành", "Train ác"], showfliers=False)
        ax.axhline(row["value"], color="#E67B47", linestyle="--", label="Mẫu lỗi 291")
        ax.set_title(row["feature"])
        ax.grid(axis="y", alpha=.2)
    axes[0].legend(fontsize=9)
    fig.suptitle("Đặc trưng được chọn từ tần suất dùng tại nút gốc của mô hình train\nHộp: Q1–Q3; vạch giữa: trung vị; đường cam: mẫu lành bị dự đoán ác", fontsize=11)
    fig.tight_layout()
    fig.savefig(output / "error_feature_context.png", dpi=300)
    fig.savefig(output / "error_feature_context.pdf")
    plt.close(fig)
    print(json.dumps({"summary": survey["summary"], "error": error}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
