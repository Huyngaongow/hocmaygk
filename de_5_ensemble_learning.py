"""Đề 5 — Ensemble Learning: tự triển khai Bagging và bỏ phiếu đa số.

Chạy: python3 de_5_ensemble_learning.py
Cây cơ sở dùng scikit-learn; bootstrap, huấn luyện tổ hợp và voting tự viết.
"""

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier


class ManualBagging:
    """Bootstrap N quan sát cho từng cây, sau đó lấy đa số dự đoán.

    Nhãn đầu vào được mã hóa bằng classes_; hòa phiếu chọn nhãn nhỏ hơn.
    Đây là bagging cây, không phải tự triển khai Random Forest: mỗi cây
    có thể xét mọi đặc trưng khi chọn phép chia.
    """

    def __init__(self, n_estimators=51, max_depth=4, random_state=42):
        if n_estimators < 1:
            raise ValueError("n_estimators phải >= 1")
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state

    def fit(self, X, y):
        rng = np.random.default_rng(self.random_state)
        self.classes_, encoded = np.unique(y, return_inverse=True)
        self.trees_ = []
        self.bootstrap_preview_ = []
        for _ in range(self.n_estimators):
            # Lấy mẫu có hoàn lại; chỉ lấy từ tập huấn luyện.
            indices = rng.integers(0, len(X), size=len(X))
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                random_state=int(rng.integers(0, 2**31 - 1)),
            )
            tree.fit(X[indices], encoded[indices])
            self.trees_.append(tree)
            self.bootstrap_preview_.append(indices[:10].tolist())
        return self

    def votes(self, X):
        predictions = np.asarray([tree.predict(X) for tree in self.trees_])
        return np.asarray([
            np.sum(predictions == label, axis=0)
            for label in range(len(self.classes_))
        ]).T

    def predict(self, X):
        return self.classes_[self.votes(X).argmax(axis=1)]


def evaluate(name, model, X, y):
    predicted = model.predict(X)
    # Dữ liệu gốc: 0=malignant, 1=benign. Xem malignant là lớp dương.
    return {
        "model": name,
        "accuracy": float(accuracy_score(y, predicted)),
        "precision_malignant": float(precision_score(y, predicted, pos_label=0, zero_division=0)),
        "recall_malignant": float(recall_score(y, predicted, pos_label=0, zero_division=0)),
        "f1_malignant": float(f1_score(y, predicted, pos_label=0, zero_division=0)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.25, stratify=data.target, random_state=42
    )
    # Chọn độ sâu trên TRAIN bằng CV; không dùng test để chọn tham số.
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = {}
    for depth in [2, 3, 4, 5, 6]:
        scores = cross_val_score(
            DecisionTreeClassifier(max_depth=depth, random_state=42),
            X_train, y_train, cv=folds, scoring="balanced_accuracy", n_jobs=1,
        )
        cv_results[depth] = float(scores.mean())
    depth = max(cv_results, key=cv_results.get)
    models = {
        "Decision Tree": DecisionTreeClassifier(max_depth=depth, random_state=42),
        "Manual Bagging": ManualBagging(max_depth=depth),
        "Random Forest (sklearn)": RandomForestClassifier(
            n_estimators=51, max_depth=depth, random_state=42, n_jobs=1
        ),
    }
    results = []
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, (name, model) in zip(axes, models.items()):
        model.fit(X_train, y_train)
        row = evaluate(name, model, X_test, y_test)
        results.append(row)
        print(json.dumps(row, ensure_ascii=False))
        ConfusionMatrixDisplay.from_predictions(
            y_test, model.predict(X_test), labels=[0, 1],
            display_labels=data.target_names, ax=ax, colorbar=False,
        )
        ax.set_title(name)
    fig.tight_layout()
    fig.savefig(args.output_dir / "confusion_matrices.png", dpi=160)
    plt.close(fig)

    bagging = models["Manual Bagging"]
    trace = {
        "sample": "First held-out test observation",
        "true_class": str(data.target_names[y_test[0]]),
        "bootstrap_first_10_train_indices": bagging.bootstrap_preview_[:3],
        "first_5_tree_predictions": [
            str(data.target_names[bagging.classes_[int(t.predict(X_test[:1])[0])]])
            for t in bagging.trees_[:5]
        ],
        "all_51_votes": dict(zip(data.target_names.tolist(), bagging.votes(X_test[:1])[0].tolist())),
        "ensemble_prediction": str(data.target_names[bagging.predict(X_test[:1])[0]]),
    }
    report = {
        "dataset": "sklearn Breast Cancer Wisconsin Diagnostic",
        "seed": 42, "train_size": len(y_train), "test_size": len(y_test),
        "positive_class": "malignant (0)",
        "depth_selection_train_cv_balanced_accuracy": cv_results,
        "selected_depth": depth, "test_metrics": results, "worked_example": trace,
    }
    (args.output_dir / "results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (args.output_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print("Selected depth:", depth)
    print(json.dumps(trace, ensure_ascii=False, indent=2))
    print("Outputs:", args.output_dir.resolve())


if __name__ == "__main__":
    main()
