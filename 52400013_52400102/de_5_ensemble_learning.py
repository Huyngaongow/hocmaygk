import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import platform

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    ConfusionMatrixDisplay, accuracy_score, balanced_accuracy_score,
    classification_report, confusion_matrix, f1_score, precision_score, recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.tree import DecisionTreeClassifier

from ensemble_model import ManualBagging

METRICS = ("accuracy", "balanced_accuracy", "precision_malignant",
           "recall_malignant", "specificity_benign", "f1_malignant")
DEPTHS = (2, 3, 4, 5, 6)
CV_FOLDS = 5


@dataclass
class Experiment:
    seed: int
    depth: int
    cv_scores: dict
    models: dict
    metrics: list
    X_train: np.ndarray
    X_test: np.ndarray
    y_train: np.ndarray
    y_test: np.ndarray
    test_indices: np.ndarray


def select_depth(X_train, y_train, seed):
    folds = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=seed)
    scores = {}
    for depth in DEPTHS:
        values = cross_val_score(
            DecisionTreeClassifier(max_depth=depth, random_state=seed),
            X_train, y_train, cv=folds, scoring="balanced_accuracy", n_jobs=1,
        )
        scores[depth] = float(values.mean())
    return max(scores, key=scores.get), scores


def evaluate(name, model, X, y):
    predicted = model.predict(X)
    tp, fn, fp, tn = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {
        "model": name,
        "accuracy": float(accuracy_score(y, predicted)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predicted)),
        "precision_malignant": float(precision_score(y, predicted, pos_label=0, zero_division=0)),
        "recall_malignant": float(recall_score(y, predicted, pos_label=0, zero_division=0)),
        "specificity_benign": float(recall_score(y, predicted, pos_label=1, zero_division=0)),
        "f1_malignant": float(f1_score(y, predicted, pos_label=0, zero_division=0)),
        "tp": int(tp), "fn": int(fn), "fp": int(fp), "tn": int(tn),
    }


def run_experiment(data, seed, n_estimators=51):
    train_indices, test_indices = train_test_split(
        np.arange(len(data.target)), test_size=0.25,
        stratify=data.target, random_state=seed,
    )
    X_train, X_test = data.data[train_indices], data.data[test_indices]
    y_train, y_test = data.target[train_indices], data.target[test_indices]
    depth, cv_scores = select_depth(X_train, y_train, seed)
    models = {
        "Decision Tree": DecisionTreeClassifier(max_depth=depth, random_state=seed),
        "Manual Bagging": ManualBagging(n_estimators=n_estimators, max_depth=depth, random_state=seed),
        "Random Forest (sklearn)": RandomForestClassifier(
            n_estimators=n_estimators, max_depth=depth, random_state=seed, n_jobs=1,
        ),
    }
    metrics = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        metrics.append(evaluate(name, model, X_test, y_test))
    return Experiment(seed, depth, cv_scores, models, metrics, X_train, X_test,
                      y_train, y_test, test_indices)


def summarize(rows):
    summaries = []
    for name in dict.fromkeys(row["model"] for row in rows):
        group = [row for row in rows if row["model"] == name]
        summary = {"model": name, "n_runs": len(group)}
        for metric in METRICS:
            values = np.asarray([row[metric] for row in group])
            summary[f"{metric}_mean"] = float(values.mean())
            summary[f"{metric}_std"] = float(values.std(ddof=1)) if len(values) > 1 else None
        summaries.append(summary)
    return summaries


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def make_trace(run, data, position):
    model = run.models["Manual Bagging"]
    X = run.X_test[position:position + 1]
    votes = model.votes(X)[0]
    predicted = model.predict(X)[0]
    counts = dict(zip(data.target_names.tolist(), votes.tolist()))
    result = {
        "sample": "First held-out test observation" if position == 0 else "First test observation with mixed votes",
        "test_position": int(position), "dataset_row": int(run.test_indices[position]),
        "true_class": str(data.target_names[run.y_test[position]]),
        "bootstrap_first_10_train_indices": model.bootstrap_preview_[:3],
        "first_5_tree_predictions": [
            str(data.target_names[model.classes_[int(tree.predict(X)[0])]])
            for tree in model.estimators_[:5]
        ],
        "all_tree_votes": counts, "ensemble_prediction": str(data.target_names[predicted]),
        "correct": bool(predicted == run.y_test[position]),
        "vote_fraction_malignant": float(votes[0] / len(model.estimators_)),
        "interpretation": "Vote fraction is not a calibrated disease probability.",
    }
    if len(model.estimators_) == 51:
        result["all_51_votes"] = counts
    return result


def reference_artifacts(run, data, output):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    reports, predictions = {}, {}
    for ax, (name, model) in zip(axes, run.models.items()):
        predicted = model.predict(run.X_test)
        predictions[name] = predicted
        reports[name] = classification_report(
            run.y_test, predicted, labels=[0, 1], target_names=data.target_names,
            output_dict=True, zero_division=0,
        )
        ConfusionMatrixDisplay.from_predictions(
            run.y_test, predicted, labels=[0, 1], display_labels=data.target_names,
            ax=ax, colorbar=False,
        )
        ax.set_title(name)
    fig.suptitle(f"Reference split: seed {run.seed}; rows=true, columns=predicted")
    fig.tight_layout()
    fig.savefig(output / "confusion_matrices.png", dpi=180)
    plt.close(fig)
    write_json(output / "classification_report.json", reports)

    model = run.models["Manual Bagging"]
    votes = model.votes(run.X_test)
    mixed_positions = np.flatnonzero((votes > 0).sum(axis=1) > 1)
    disagreement = make_trace(run, data, int(mixed_positions[0])) if len(mixed_positions) else None
    write_csv(output / "predictions.csv", [
        {
            "test_position": i, "dataset_row": int(run.test_indices[i]),
            "true_class": str(data.target_names[run.y_test[i]]),
            "decision_tree": str(data.target_names[predictions["Decision Tree"][i]]),
            "manual_bagging": str(data.target_names[predictions["Manual Bagging"][i]]),
            "random_forest": str(data.target_names[predictions["Random Forest (sklearn)"][i]]),
            "votes_malignant": int(votes[i, 0]), "votes_benign": int(votes[i, 1]),
            "bagging_correct": bool(predictions["Manual Bagging"][i] == run.y_test[i]),
        }
        for i in range(len(run.y_test))
    ])
    fig, ax = plt.subplots(figsize=(7, 4))
    if disagreement:
        counts = list(disagreement["all_tree_votes"].values())
        bars = ax.bar(data.target_names, counts, color=["#E67B47", "#087E83"])
        ax.bar_label(bars)
        ax.set_ylim(0, max(counts) * 1.3)
        ax.set_title(
            f"First mixed vote: test row {disagreement['test_position']}\n"
            f"True={disagreement['true_class']}; predicted={disagreement['ensemble_prediction']}"
        )
        ax.set_ylabel("Number of hard votes (not probability)")
    else:
        ax.text(.5, .5, "No mixed-vote test observation in this run.", ha="center", va="center")
        ax.set_axis_off()
    fig.tight_layout()
    fig.savefig(output / "voting_example.png", dpi=180)
    plt.close(fig)
    return make_trace(run, data, 0), disagreement, int(len(mixed_positions))


def plot_summary(summary, output):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    labels = ["Decision Tree", "Manual Bagging", "Random Forest"]
    for ax, metric, title in zip(axes, ["accuracy", "recall_malignant"], ["Accuracy", "Malignant recall"]):
        means = [row[f"{metric}_mean"] for row in summary]
        stds = [row[f"{metric}_std"] for row in summary]
        bars = ax.bar(labels, means, color=["#93B7B1", "#087E83", "#E67B47"],
                      yerr=stds if all(value is not None for value in stds) else None, capsize=5)
        ax.bar_label(bars, labels=[f"{value:.1%}" for value in means], padding=8)
        ax.set_ylim(0, 1.08)
        ax.set_yticks(np.arange(0, 1.01, .2))
        ax.set_title(title)
    fig.suptitle(f"{summary[0]['n_runs']} stratified holdout(s); error bars = sample SD, not CI")
    fig.tight_layout()
    fig.savefig(output / "stability.png", dpi=180)
    plt.close(fig)


def percent(value):
    return f"{value * 100:.2f}%"


def write_report(report, output):
    lines = [
        "# Báo cáo thực nghiệm — Ensemble Learning", "",
        f"Seed tham chiếu: **{report['seed']}**; train: {report['train_size']}; test: {report['test_size']}; "
        f"depth chọn trên train: **{report['selected_depth']}**; số cây: {report['n_estimators']}.", "",
        "Ác tính (malignant=0) là lớp dương. Hàng ma trận là nhãn thật, cột là dự đoán.", "",
        "## Kết quả seed tham chiếu", "",
        "| Mô hình | Accuracy | Precision ác | Recall ác | F1 ác | Bỏ sót ác |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in report["test_metrics"]:
        vals = " | ".join(percent(row[key]) for key in ["accuracy", "precision_malignant", "recall_malignant", "f1_malignant"])
        lines.append(f"| {row['model']} | {vals} | {row['fn']} |")
    lines += ["", "## Độ ổn định giữa các lần chia", "",
              "Mean ± SD mẫu (đơn vị %; SD tính bằng ddof=1). Một lần chạy: SD không xác định.", "",
              "| Mô hình | Số lần | Accuracy mean ± SD | Recall ác mean ± SD | F1 ác mean ± SD |",
              "|---|---:|---:|---:|---:|"]
    for row in report["repeated_evaluation"]["summary"]:
        vals = []
        for key in ["accuracy", "recall_malignant", "f1_malignant"]:
            sd = row[f"{key}_std"]
            vals.append(f"{row[f'{key}_mean']*100:.2f} ± {sd*100:.2f}" if sd is not None else f"{row[f'{key}_mean']*100:.2f} (SD: N/A)")
        lines.append(f"| {row['model']} | {row['n_runs']} | " + " | ".join(vals) + " |")
    lines += ["", "Các tập test giữa các seed có thể giao nhau. SD mô tả độ biến thiên, không phải khoảng tin cậy độc lập.",
              "Mỗi seed chọn lại depth bằng CV trên train của seed đó; không chọn seed tốt nhất dựa trên test.",
              "Depth chọn bằng cây đơn rồi dùng chung cho ba mô hình, chưa tuning riêng từng ensemble.", "",
              "## Out-of-bag (Bagging, seed tham chiếu)", "",
              f"- Accuracy OOB: {percent(report['oob']['accuracy']) if report['oob']['accuracy'] is not None else 'N/A'}.",
              f"- Coverage: {percent(report['oob']['coverage'])}; mẫu có phiếu: {report['oob']['covered_samples']}.",
              "- Chỉ cây không thấy mẫu khi huấn luyện mới được bỏ phiếu OOB cho mẫu đó.",
              "- Depth đã chọn trên train, nên OOB sau lựa chọn này không phải điểm kiểm định độc lập.", "",
              "## Ví dụ bất đồng", ""]
    example = report["disagreement_example"]
    if example:
        lines += [f"Vị trí test {example['test_position']}, hàng dữ liệu gốc {example['dataset_row']} (đếm từ 0).",
                  f"Phiếu: {example['all_tree_votes']}. Nhãn thật: {example['true_class']}; "
                  f"dự đoán: {example['ensemble_prediction']}; đúng: {example['correct']}.",
                  "Chọn mẫu bất đồng đầu tiên theo thứ tự test, không chọn theo dự đoán đúng."]
    else:
        lines.append("Không có mẫu bất đồng trong lần chạy này; không tạo ví dụ giả.")
    lines += ["", "Tỷ lệ phiếu không phải xác suất bệnh đã hiệu chỉnh. RF lấy trung bình xác suất cây, khác hard voting.",
              "Đây là bài minh họa học máy, chưa xác thực lâm sàng.", "",
              "## Tái lập", "", f"Phiên bản: xem results.json. Seeds: {report['repeated_evaluation']['seeds']}.",
              "Biểu đồ ma trận và voting thuộc seed tham chiếu; stability.png thuộc tất cả seed.", ""]
    (output / "report.md").write_text("\n".join(lines), encoding="utf-8")


def positive_int(value):
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("phải là số nguyên >= 1")
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description='Thực nghiệm Bagging, cây quyết định và Random Forest.')
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    parser.add_argument("--seed", type=int, default=42, help="seed tham chiếu và bắt đầu dãy seed")
    parser.add_argument("--repeats", type=positive_int, default=10, help="tổng số seed gồm seed tham chiếu (mặc định 10)")
    parser.add_argument("--n-estimators", type=positive_int, default=51, help="số cây mỗi ensemble (mặc định 51)")
    args = parser.parse_args(argv)
    if not 0 <= args.seed <= 2**32 - args.repeats:
        parser.error("seed và dãy seed phải nằm trong [0, 2**32-1]")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    data = load_breast_cancer()
    all_rows, runs = [], []
    reference = None
    for i, seed in enumerate(range(args.seed, args.seed + args.repeats)):
        run = run_experiment(data, seed, args.n_estimators)
        if reference is None:
            reference = run
        all_rows.extend({"seed": seed, "selected_depth": run.depth, **row} for row in run.metrics)
        runs.append({"seed": seed, "selected_depth": run.depth,
                     "train_cv_balanced_accuracy": run.cv_scores, "test_metrics": run.metrics})
        print(f"[{i+1}/{args.repeats}] seed={seed}, depth={run.depth}, "
              f"Bagging accuracy={percent(run.metrics[1]['accuracy'])}")

    worked_example, disagreement, mixed_count = reference_artifacts(reference, data, args.output_dir)
    model = reference.models["Manual Bagging"]
    summary = summarize(all_rows)
    report = {
        "schema_version": 2, "dataset": "sklearn Breast Cancer Wisconsin Diagnostic",
        "seed": args.seed, "train_size": len(reference.y_train), "test_size": len(reference.y_test),
        "n_estimators": args.n_estimators, "positive_class": "malignant (0)",
        "class_order": data.target_names.tolist(),
        "depth_selection_train_cv_balanced_accuracy": reference.cv_scores,
        "selected_depth": reference.depth, "test_metrics": reference.metrics,
        "worked_example": worked_example, "disagreement_example": disagreement,
        "mixed_vote_test_samples": mixed_count,
        "oob": {
            "accuracy": float(model.oob_score_) if np.isfinite(model.oob_score_) else None,
            "coverage": model.oob_coverage_, "covered_samples": int((model.oob_counts_ > 0).sum()),
            "min_trees_per_sample": int(model.oob_counts_.min()), "max_trees_per_sample": int(model.oob_counts_.max()),
            "note": "Hard votes on train-only OOB samples; not independent of train-based depth selection.",
        },
        "protocol": {
            "test_size": .25, "stratified": True, "cv_folds": CV_FOLDS, "candidate_depths": list(DEPTHS),
            "depth_selection": "Single-tree train CV, shared depth for all models; no per-ensemble tuning.",
            "random_forest_aggregation": "Mean of tree class probabilities, unlike manual hard voting.",
        },
        "repeated_evaluation": {
            "seeds": list(range(args.seed, args.seed + args.repeats)), "runs": runs, "summary": summary,
            "interpretation": "Overlapping stratified holdouts; sample SD (ddof=1) is descriptive, not an independent CI.",
        },
        "versions": {"python": platform.python_version(), "numpy": np.__version__,
                     "scikit-learn": sklearn.__version__, "matplotlib": matplotlib.__version__},
    }
    write_json(args.output_dir / "results.json", report)
    write_csv(args.output_dir / "metrics.csv", reference.metrics)
    write_csv(args.output_dir / "repeated_metrics.csv", all_rows)
    write_csv(args.output_dir / "summary_metrics.csv", summary)
    write_report(report, args.output_dir)
    plot_summary(summary, args.output_dir)

    print(f"\nReference seed {args.seed}: train={report['train_size']}, test={report['test_size']}, depth={reference.depth}")
    print(f"{'Model':<25} {'Accuracy':>10} {'Recall(M)':>11} {'F1(M)':>10} {'FN':>5}")
    for row in reference.metrics:
        print(f"{row['model']:<25} {percent(row['accuracy']):>10} {percent(row['recall_malignant']):>11} "
              f"{percent(row['f1_malignant']):>10} {row['fn']:>5}")
    oob_accuracy = percent(report['oob']['accuracy']) if report['oob']['accuracy'] is not None else 'N/A'
    print(f"OOB accuracy={oob_accuracy}, coverage={percent(model.oob_coverage_)}")
    print(f"\nStability across {args.repeats} holdouts (mean +/- sample SD; not CI):")
    for row in summary:
        sd = row["accuracy_std"]
        spread = f"{sd*100:.2f} pp" if sd is not None else "N/A"
        print(f"{row['model']:<25} accuracy={percent(row['accuracy_mean'])}, SD={spread}")
    if disagreement:
        print(f"Mixed-vote example: test_position={disagreement['test_position']}, "
              f"votes={disagreement['all_tree_votes']}, true={disagreement['true_class']}, "
              f"predicted={disagreement['ensemble_prediction']}, correct={disagreement['correct']}")
    else:
        print("No mixed-vote example in this reference split.")
    print("Outputs:", args.output_dir.resolve())


if __name__ == "__main__":
    main()
