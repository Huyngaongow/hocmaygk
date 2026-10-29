# Mở rộng bốn hướng Ensemble Learning

Cấu hình cố định; so sánh mô tả bổ sung sau thí nghiệm gốc. Không chọn mô hình theo test.

Trung bình theo %, SD mẫu theo điểm phần trăm; các holdout có thể giao nhau.

| Mô hình | Accuracy | Recall ác | F1 ác | Balanced accuracy |
|---|---:|---:|---:|---:|
| Decision Tree | 92.80 ± 1.84 | 90.38 ± 4.66 | 90.30 ± 2.42 | 92.30 ± 1.94 |
| Manual Bagging | 94.76 ± 1.59 | 92.45 ± 3.77 | 92.89 ± 2.13 | 94.28 ± 1.75 |
| Random Forest (sklearn) | 95.03 ± 1.85 | 92.26 ± 3.26 | 93.26 ± 2.39 | 94.47 ± 1.80 |
| Decision Tree (depth=3) | 92.94 ± 2.15 | 90.19 ± 4.86 | 90.43 ± 2.92 | 92.37 ± 2.41 |
| Logistic Regression | 97.62 ± 0.82 | 96.60 ± 2.32 | 96.78 ± 1.12 | 97.41 ± 0.99 |
| Gaussian NB | 94.20 ± 1.40 | 90.19 ± 4.15 | 91.99 ± 2.01 | 93.37 ± 1.81 |
| AdaBoost | 96.43 ± 1.07 | 94.15 ± 2.08 | 95.14 ± 1.44 | 95.96 ± 1.13 |
| Voting (hard) | 95.80 ± 1.23 | 92.64 ± 3.72 | 94.23 ± 1.74 | 95.15 ± 1.58 |
| Voting (soft) | 95.66 ± 1.27 | 92.64 ± 3.72 | 94.04 ± 1.80 | 95.04 ± 1.63 |
| Stacking | 96.64 ± 1.22 | 95.09 ± 2.70 | 95.46 ± 1.62 | 96.32 ± 1.28 |

Ba mô hình tham chiếu dùng độ sâu chọn bằng CV; cây trong Voting/Stacking cố định depth=3.
AdaBoost dùng tối đa 51 cây depth=1; Voting/Stacking dùng cây depth=3, LR có StandardScaler và GaussianNB.
Stacking học tầng hai từ dự đoán OOF 5 fold trong train; mọi bước scale nằm trong pipeline từng fold.
Không suy ra một họ ensemble luôn tốt hơn từ các cấu hình này; đây không phải kiểm định hoặc xác nhận trên dữ liệu mới.
