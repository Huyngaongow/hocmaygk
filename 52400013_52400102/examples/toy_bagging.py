import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.tree import DecisionTreeClassifier


def build_toy_example():
    X = np.arange(1, 6, dtype=float).reshape(-1, 1)
    y = np.array([1, 1, 0, 0, 0])
    samples = ([0, 0, 2, 4, 1], [0, 0, 1, 3, 4], [4, 2, 4, 1, 3])
    query_x = 2.8
    trees, fitted = [], []
    for number, indices in enumerate(samples, 1):
        indices = np.array(indices)
        model = DecisionTreeClassifier(max_depth=1, random_state=number)
        model.fit(X[indices], y[indices])
        fitted.append(model)
        root = model.tree_
        left, right = int(root.children_left[0]), int(root.children_right[0])
        left_size = int(root.n_node_samples[left])
        right_size = int(root.n_node_samples[right])
        gini_after = float(
            (left_size * root.impurity[left] + right_size * root.impurity[right]) / len(indices)
        )
        threshold = float(root.threshold[0])
        trees.append({
            "name": f"h{number}",
            "bootstrap_indices": indices.tolist(),
            "bootstrap_labels": y[indices].tolist(),
            "omitted_indices": sorted(set(range(len(X))) - set(indices.tolist())),
            "threshold": threshold,
            "left_label": int(model.classes_[root.value[left][0].argmax()]),
            "right_label": int(model.classes_[root.value[right][0].argmax()]),
            "left_size": left_size,
            "right_size": right_size,
            "gini_before": float(root.impurity[0]),
            "left_gini": float(root.impurity[left]),
            "right_gini": float(root.impurity[right]),
            "gini_after": gini_after,
            "gini_gain": float(root.impurity[0]) - gini_after,
            "query_prediction": int(model.predict([[query_x]])[0]),
        })

    predictions = [tree["query_prediction"] for tree in trees]
    votes = np.bincount(predictions, minlength=2)
    oob_rows = []
    for index in range(len(X)):
        eligible = [i for i, tree in enumerate(trees) if index in tree["omitted_indices"]]
        row_predictions = [int(fitted[i].predict(X[index:index + 1])[0]) for i in eligible]
        row_votes = np.bincount(row_predictions, minlength=2)
        predicted = int(row_votes.argmax()) if eligible else None
        oob_rows.append({
            "index": index,
            "true_label": int(y[index]),
            "eligible_trees": [trees[i]["name"] for i in eligible],
            "tree_predictions": row_predictions,
            "vote_counts": {str(c): int(row_votes[c]) for c in range(2)},
            "prediction": predicted,
            "correct": bool(predicted == y[index]) if eligible else None,
        })
    covered = sum(row["prediction"] is not None for row in oob_rows)
    correct = sum(row["correct"] is True for row in oob_rows)
    return {
        "schema_version": 1,
        "description": "Dữ liệu giả lập; bootstrap cố định để minh họa phép tính, không phải kết quả Breast Cancer.",
        "dataset": {
            "synthetic": True,
            "indices": list(range(len(X))),
            "feature_values": X[:, 0].astype(int).tolist(),
            "labels": y.tolist(),
            "class_names": {"0": "ác tính", "1": "lành tính"},
        },
        "trees": trees,
        "query": {
            "x": query_x,
            "tree_predictions": predictions,
            "vote_counts": {str(c): int(votes[c]) for c in range(2)},
            "prediction": int(votes.argmax()),
            "note": "Không gán nhãn thật cho mẫu mới này. Tỷ lệ phiếu không phải xác suất bệnh.",
        },
        "oob": {
            "rows": oob_rows,
            "covered_samples": covered,
            "total_samples": len(X),
            "coverage": covered / len(X),
            "correct_samples": correct,
            "accuracy": correct / covered if covered else None,
            "note": "Chỉ cây chưa thấy quan sát mới được bỏ phiếu; mẫu không có phiếu không được tính accuracy OOB.",
        },
    }


def render_markdown(example):
    names = example["dataset"]["class_names"]
    lines = [
        "# Ví dụ Bagging xuyên suốt: từ dữ liệu đến quyết định", "",
        "Dữ liệu dưới đây là **giả lập một chiều**, không phải ca bệnh thực tế. "
        "Dùng nhãn 0 = ác tính, 1 = lành tính để thống nhất ký hiệu với thí nghiệm chính.", "",
        "## 1. Dữ liệu ban đầu", "",
        "| Chỉ số i | Đặc trưng x | Nhãn y |", "|---:|---:|---|",
    ]
    data = example["dataset"]
    for index, x, y in zip(data["indices"], data["feature_values"], data["labels"]):
        lines.append(f"| {index} | {x} | {y}: {names[str(y)]} |")
    lines += ["", "## 2. Bootstrap và học ba cây nhỏ", "",
              "Mỗi mẫu có 5 lượt lấy **có hoàn lại** từ 5 quan sát. Ba dãy dưới đây "
              "được chọn cố định để có thể đối chiếu bằng tay; không phải ba tập rời nhau. "
              "Cây độ sâu 1 chọn ngưỡng giảm Gini nhiều nhất.", "",
              "| Cây | Chỉ số bootstrap | Không có mặt | Ngưỡng học được | Gini trước | Gini sau |",
              "|---|---|---|---:|---:|---:|"]
    for tree in example["trees"]:
        lines.append(f"| {tree['name']} | {tree['bootstrap_indices']} | {tree['omitted_indices']} "
                     f"| {tree['threshold']:g} | {tree['gini_before']:.2f} | {tree['gini_after']:.2f} |")
    first = example["trees"][0]
    lines += ["", "Với h1, bootstrap tạo các cặp: (1,lành), (1,lành), (3,ác), (5,ác), (2,lành).",
              "Gini trước = 1 − (3/5)² − (2/5)² = 0,48. Ngưỡng 2,5 cho nhánh trái có 3 lành "
              "và nhánh phải có 2 ác; cả hai nhánh thuần nhất nên Gini sau = (3/5)×0 + (2/5)×0 = 0.",
              f"Mức giảm = {first['gini_gain']:.2f}. Ngưỡng này nằm giữa x=2 và x=3. "
              "Ngược lại, h2 không có x=3 nên chọn ngưỡng giữa x=2 và x=4, tức 3,0. "
              "Đó là cách bootstrap có thể tạo cây khác nhau.", "",
              "## 3. Cùng dự đoán một mẫu mới x = 2,8", "",
              "| Cây | Quy tắc đã học | Thay x=2,8 | Dự đoán |", "|---|---|---|---|"]
    for tree in example["trees"]:
        prediction = tree["query_prediction"]
        relation = "≤" if example["query"]["x"] <= tree["threshold"] else ">"
        lines.append(f"| {tree['name']} | x ≤ {tree['threshold']:g}: lành; còn lại: ác "
                     f"| 2,8 {relation} {tree['threshold']:g} | {names[str(prediction)]} ({prediction}) |")
    lines += ["", "Ba dự đoán **[0, 1, 0]** cho **2 phiếu ác, 1 phiếu lành**; hard voting chọn **ác tính (0)**.",
              "Không có nhãn thật của mẫu mới nên chưa kết luận dự đoán đúng hay sai. "
              "2/3 chỉ là tỷ lệ phiếu, không phải xác suất bệnh đã hiệu chỉnh.", "",
              "## 4. Kiểm tra OOB trên chính năm mẫu train", "",
              "| Chỉ số | Nhãn thật | Cây được bỏ phiếu OOB | Dự đoán OOB | Đúng? |",
              "|---:|---|---|---|---|"]
    for row in example["oob"]["rows"]:
        eligible = ", ".join(row["eligible_trees"]) or "Không có"
        predicted = names[str(row["prediction"])] if row["prediction"] is not None else "Không xác định"
        correct = "Có" if row["correct"] is True else "Không" if row["correct"] is False else "Không tính"
        lines.append(f"| {row['index']} | {names[str(row['true_label'])]} | {eligible} | {predicted} | {correct} |")
    lines += ["", "Mẫu 2 (x=3, nhãn ác) chỉ nhận phiếu từ h2 vì h1/h3 đã học mẫu đó. "
              "h2 dự đoán lành do 3 ≤ 3,0: đây là một lỗi OOB thật của ví dụ.",
              "**Coverage = 3/5 = 60%; accuracy OOB = 2/3 ≈ 66,67%** trên ba mẫu có phiếu. "
              "Hai mẫu không có phiếu không bị coi là dự đoán lớp 0 hoặc tự động tính sai.", "",
              "## 5. Điều cần rút ra", "",
              "Bootstrap thay đổi dữ liệu mỗi cây; cây học ngưỡng khác nhau; voting kết hợp "
              "các dự đoán. OOB chỉ dùng những cây chưa học mẫu được đánh giá. "
              "Ba cây ở đây phục vụ tính tay, không dùng để suy ra hiệu năng của thí nghiệm 51 cây.", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Ví dụ bootstrap, Gini và bỏ phiếu.')
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/toy"))
    args = parser.parse_args(argv)
    example = build_toy_example()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "toy_example.json").write_text(
        json.dumps(example, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
    )
    (args.output_dir / "toy_example.md").write_text(render_markdown(example), encoding="utf-8")
    print("Dữ liệu giả lập: bootstrap cố định, ngưỡng và dự đoán được cây tính thực sự.")
    print("Ngưỡng:", [tree["threshold"] for tree in example["trees"]])
    print("x=2.8 →", example["query"]["tree_predictions"], "→ 2:1 → ác tính (0)")
    print("OOB: coverage=3/5=60%; accuracy=2/3=66.67% (chỉ trên mẫu có phiếu)")
    print("Outputs:", args.output_dir.resolve())


if __name__ == "__main__":
    main()
