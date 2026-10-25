# Đề 5 — Ensemble Learning

Đề tương ứng với **phần dư 5 (mod 8)** trong PDF *Essay Midterm I-2627*.
Đây là mã minh họa và tài liệu nền để nhóm phát triển bài báo cáo, không phải
bộ hồ sơ nộp hoàn chỉnh. Đề yêu cầu báo cáo Word/PDF, mã Python và slide.

## Slide thuyết trình

Đã có bộ **24 slide** trong `De_5_Ensemble_Learning.pptx`, kèm bản xem nhanh
`De_5_Ensemble_Learning.pdf`. PowerPoint có lời thuyết trình trong phần Notes;
bản văn bản riêng nằm tại `presentation/loi_thuyet_trinh.md`.
Điền tên thành viên và lớp tại slide 1 trước khi trình bày. Xem
`presentation/README.md` nếu muốn tạo lại slide. Báo cáo Word/PDF dạng bài
viết chưa được tạo; PDF ở đây là bản xuất của slide.

## Chạy chương trình

```bash
cd /workspace/hocmaygk
python3 -m venv /workspace/venvs/hocmaygk
/workspace/venvs/hocmaygk/bin/python -m pip install -r requirements.txt
export MPLCONFIGDIR=/tmp/hocmaygk-matplotlib
export XDG_CACHE_HOME=/tmp/hocmaygk-cache
/workspace/venvs/hocmaygk/bin/python de_5_ensemble_learning.py
```

Kết quả lưu vào `outputs/`: bảng chỉ số `metrics.csv`, chi tiết thí nghiệm và
ví dụ bỏ phiếu `results.json`, hình ma trận nhầm lẫn `confusion_matrices.png`.
Dữ liệu có sẵn trong scikit-learn, không cần tải dữ liệu hoặc khóa API.

## 1. Nguyên lý hoạt động

Ensemble Learning kết hợp nhiều mô hình cơ sở để đưa ra dự đoán chung.
Các hướng chính gồm Bagging (huấn luyện trên các mẫu bootstrap), Boosting
(huấn luyện tuần tự để sửa sai), Voting (kết hợp dự đoán) và Stacking
(một mô hình học cách kết hợp các dự đoán ngoài mẫu).

Ví dụ này tập trung vào **Bagging với cây quyết định**. Với tập train gồm N
quan sát, mỗi cây nhận N mẫu lấy ngẫu nhiên có hoàn lại. Các cây được huấn
luyện độc lập và tổ hợp chọn lớp có nhiều phiếu nhất:

`H(x) = argmax_c Σ_b I[h_b(x) = c]`.

Một quan sát có xác suất `(1 - 1/N)^N ≈ 0,368` không xuất hiện trong mẫu
bootstrap của một cây. Đây là cơ sở cho đánh giá out-of-bag, nhưng chương
trình hiện dùng tập test riêng, không tính chỉ số out-of-bag.

Trung bình nhiều mô hình giúp giảm phương sai khi lỗi của chúng không quá
tương quan. Với B mô hình có cùng phương sai σ² và tương quan cặp ρ,
phương sai trung bình là `σ²[ρ + (1-ρ)/B]`. Đây là trực giác cho trung bình
dự đoán số; chất lượng bỏ phiếu phân lớp còn phụ thuộc phân bố lỗi.
Ensemble không bảo đảm luôn tốt hơn mô hình đơn.

Random Forest bổ sung chọn ngẫu nhiên tập con đặc trưng tại mỗi phép chia
để giảm tương quan giữa các cây. Chương trình dùng Random Forest của
scikit-learn làm đối chiếu, không nhận là tự cài đặt thuật toán đó.

## 2. Quy trình và ví dụ tính toán

1. Chia dữ liệu thành train 75% và test 25%, giữ tỷ lệ lớp, seed 42.
2. Chọn độ sâu cây từ 2 đến 6 bằng CV phân tầng 5 fold trên train với
   balanced accuracy. Dùng chung độ sâu này cho các mô hình đối chiếu;
   đây không phải tối ưu riêng từng ensemble.
3. Với từng cây trong 51 cây, lấy N chỉ số bootstrap từ train, rồi huấn luyện.
4. Thu dự đoán của từng cây trên quan sát mới.
5. Đếm số phiếu cho từng lớp rồi lấy lớp có nhiều phiếu nhất. Nếu hòa,
   chọn lớp có mã nhỏ hơn (51 cây và bài toán hai lớp không xảy ra hòa).
6. Đánh giá trên test sau khi chốt cấu hình.

Ví dụ tính tay, train có chỉ số `[0, 1, 2, 3, 4]`. Ba mẫu bootstrap hợp lệ
là `[0, 0, 2, 4, 1]`, `[1, 3, 3, 2, 0]`, `[4, 2, 4, 1, 3]`. Nếu ba cây
dự đoán một quan sát là `[ác tính, lành tính, ác tính]`, số phiếu tương ứng
là 2 và 1, nên kết quả là ác tính. Ví dụ này minh họa cơ chế, không phải
kết quả thí nghiệm. Chương trình xuất các chỉ số bootstrap và phiếu thực
của quan sát test đầu tiên vào `results.json` để trình bày từng bước.

## 3. Bài toán ứng dụng

Phân loại mẫu khối u vú trong bộ Breast Cancer Wisconsin Diagnostic:
569 mẫu, 30 đặc trưng số mô tả nhân tế bào, nhãn `0=malignant` (ác tính),
`1=benign` (lành tính). Đầu vào là 30 đặc trưng, đầu ra là lớp dự đoán.
Không cần chuẩn hóa cho các cây quyết định trong ví dụ này.

Báo cáo accuracy, precision, recall và F1; **lớp dương là ác tính (0)**.
Recall ác tính cho biết tỷ lệ ca ác tính được nhận ra; cần xem cả ca bỏ sót
trong ma trận nhầm lẫn. Đây là bài minh họa học máy, chưa có xác thực
lâm sàng hay kiểm định trên quần thể độc lập.

## 4. Mã nguồn và nhận xét kết quả

Kết quả chạy với các phiên bản trong `requirements.txt`, 426 mẫu train và
143 mẫu test, độ sâu được chọn là 3:

| Mô hình | Accuracy | Precision ác tính | Recall ác tính | F1 ác tính |
| --- | ---: | ---: | ---: | ---: |
| Decision Tree | 0,9441 | 0,9412 | 0,9057 | 0,9231 |
| Manual Bagging | 0,9510 | 0,9423 | 0,9245 | 0,9333 |
| Random Forest | 0,9510 | 0,9423 | 0,9245 | 0,9333 |

Trên lần chia này, Bagging bỏ sót 4/53 ca ác tính, cây đơn bỏ sót 5/53.
Bagging và Random Forest có cùng các chỉ số tổng hợp trong lần chạy này;
điều này không chứng minh chúng luôn cho kết quả giống nhau.

`ManualBagging.fit()` tự thực hiện bootstrap và huấn luyện các cây;
`votes()` đếm phiếu; `predict()` chọn lớp thắng. Cây cơ sở do scikit-learn
cung cấp. `main()` chia dữ liệu, chọn độ sâu bằng CV, huấn luyện và đánh giá
Decision Tree, Manual Bagging và Random Forest.

Đọc số đo thực trong `outputs/metrics.csv` sau khi chạy. So sánh recall ác
tính, F1 và số âm tính giả giữa ba mô hình; không kết luận chỉ dựa vào
accuracy. Một lần chia dữ liệu và một seed chưa chứng minh phương pháp
nào tốt hơn nói chung. Nhóm có thể mở rộng bằng đánh giá lặp lại với nhiều
seed và khoảng biến thiên, đồng thời giữ test độc lập với chọn tham số.

## Tài liệu tham khảo

- Breiman (1996), *Bagging Predictors*, Machine Learning 24, 123–140.
  https://doi.org/10.1007/BF00058655
- Breiman (2001), *Random Forests*, Machine Learning 45, 5–32.
  https://doi.org/10.1023/A:1010933404324
- Dữ liệu và nguồn gốc:
  https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html
- Tổng quan ensemble:
  https://scikit-learn.org/stable/modules/ensemble.html
