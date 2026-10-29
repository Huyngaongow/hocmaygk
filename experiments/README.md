# Phân tích bổ sung cho báo cáo

Từ gốc repo, dùng Python đã cài `requirements.txt`:

```bash
export MPLCONFIGDIR=/tmp/hocmaygk-matplotlib
export XDG_CACHE_HOME=/tmp/hocmaygk-cache
.venv/bin/python experiments/report_extensions.py
```

Windows dùng `.venv\Scripts\python.exe` thay `.venv/bin/python`; không cần hai
lệnh export trong môi trường Windows thông thường.

Đầu ra tại `outputs/extensions/`:

- `analysis.json`: giao thức, chỉ số train/test, từng fold, thống kê và nhánh cây.
- `tree_counts_folds.csv`, `tree_counts_summary.csv`: kết quả khảo sát số cây.
- `error_features.csv`: đặc trưng mẫu lỗi so với phân bố hai lớp trên train.
- `bagging_rf_disagreements.csv`: các mẫu Bagging và RF dự đoán khác nhau.
- `tree_count_cv.png/.pdf`, `error_feature_context.png/.pdf`: hình 300 dpi và PDF vector.

Khảo sát B∈{1,5,11,21,51,101} chỉ nhận 426 mẫu train của seed 42. Năm fold ngoài
đánh giá cấu hình; trong phần học của mỗi fold, CV năm fold chọn depth bằng cây
đơn từ {2,3,4,5,6}. Mọi B dùng cùng fold, depth và chuỗi seed tương ứng.
Không đưa tập test vào hàm khảo sát. SD giữa fold là mô tả, không phải CI.

Đây là phân tích bổ sung sau thí nghiệm gốc, không thay cấu hình B = 51 hoặc
viết lại điểm test. Không tuyên bố B = 51 tối ưu tổng quát hay số CV là điểm test.

Các nhánh của mẫu lỗi được lấy từ mô hình gốc 51 cây. Các đặc trưng minh họa
được chọn từ tần suất sử dụng tại nút gốc của các cây đã học, không chọn theo
độ đẹp của hình hoặc nhãn mẫu test. Phân tích mô tả quyết định của mô hình,
không xác định nguyên nhân y khoa hoặc hiệu chỉnh xác suất bệnh.

Không tạo hay chỉnh sửa file Word. Phần văn bản để chèn vào báo cáo lưu tại
`report/Bo_sung_phan_tich_va_thuc_nghiem.md`.

## Đối chứng có kiểm soát và đo mức bất đồng

Phần này cần kết quả gốc đủ 10 seed trong `outputs/results.json`. Nếu chưa có,
chạy `python de_5_ensemble_learning.py` bằng cùng Python venv trước.

```bash
.venv/bin/python experiments/controlled_comparison.py
```

Thí nghiệm 2 × 2 thay đổi cách xét đặc trưng (`all`/`sqrt`) và cách tổng hợp
(`hard`/`soft`), giữ 51 cây. Chỉ sử dụng train 426 mẫu của seed 42, cùng 5 fold
ngoài và cách chọn depth trong phần học của từng fold như khảo sát số cây.
Các nhóm đặc trưng dùng cùng bootstrap và seed từng cây; hard/soft sử dụng
chính cùng những cây đã học. Nhóm `sqrt` là Bagging có ngẫu nhiên hóa đặc
trưng tự xây, không phải kết quả chạy `RandomForestClassifier`.

Các file `controlled_comparison.json`, `controlled_comparison_folds.csv` và
`controlled_comparison_summary.csv` lưu trong `outputs/extensions/`.
JSON còn chứa so sánh từng cặp trên 10 holdout gốc và đối chiếu số quan sát
khác nhau trong bootstrap với kỳ vọng lý thuyết. Bảng fold lưu cả chất lượng
cây cơ sở và mức bất đồng giữa các cặp cây. Đây là phân tích mô tả bổ sung;
SD không phải CI và chưa có kiểm định ý nghĩa thống kê.

## AdaBoost, Voting và Stacking

```bash
.venv/bin/python experiments/ensemble_families.py
```

Chạy sau thí nghiệm gốc để đối chiếu ba mô hình tham chiếu. Mặc định dùng
10 seed 42–51, cùng các lần chia train/test phân tầng 75/25 của bài gốc.
Các cấu hình bổ sung được cố định trước khi chạy phần mở rộng:

- AdaBoost: tối đa 51 cây độ sâu 1, learning rate 1; sklearn 1.8 dùng SAMME.
- Ba mô hình cơ sở: cây độ sâu 3 cố định, Logistic Regression có
  `StandardScaler` trong `Pipeline`, Gaussian Naive Bayes.
- Voting: cùng bộ ba trên, trọng số bằng nhau, chạy cả hard và soft.
- Stacking: cùng bộ ba; tạo dự đoán xác suất ngoài fold bằng CV phân tầng
  5 fold có xáo trộn, rồi học Logistic Regression tầng hai. Các pipeline
  được học riêng trong từng fold; khi dự đoán test, mô hình cơ sở học lại
  trên toàn train. Không dùng `cv='prefit'`.

Ba mô hình gốc và ba mô hình cơ sở riêng lẻ cũng có mặt trong bảng kết quả.
Cây độ sâu 3 cố định của phần mở rộng khác cây được chọn độ sâu bằng CV
trong thí nghiệm gốc. Đây là so sánh các cấu hình cụ thể, không tách riêng
ảnh hưởng nhân quả của tên phương pháp.

Đầu ra trong `outputs/extensions/`:

- `family_comparison.json`: giao thức, cấu hình, phiên bản, chỉ số từng lần
  chạy, dự đoán và chỉ số các hàng train/test/fold để kiểm tra.
- `family_comparison_runs.csv`, `family_comparison_summary.csv`: bảng từng
  seed và trung bình ± SD mẫu.
- `family_comparison.png/.pdf`: biểu đồ kết quả.
- `family_comparison.md`: tóm tắt thực nghiệm tự sinh.

Đây là phần mở rộng sau khi đã quan sát thí nghiệm gốc. Không chọn cấu hình
theo điểm test và không coi các holdout này là một lần xác nhận độc lập mới.
SD giữa các holdout giao nhau là thống kê mô tả. Ensemble không được bảo đảm
tốt hơn từng mô hình cơ sở; phải đọc cả các hàng baseline trong bảng kết quả.
