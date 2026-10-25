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

Khảo sát B∈{1,5,11,21,51,101} chỉ nhận 426 mẫu train của seed42. Năm fold ngoài
đánh giá cấu hình; trong phần học của mỗi fold, CV năm fold chọn depth bằng cây
đơn từ {2,3,4,5,6}. Mọi B dùng cùng fold, depth và chuỗi seed tương ứng.
Không đưa tập test vào hàm khảo sát. SD giữa fold là mô tả, không phải CI.

Đây là phân tích bổ sung sau thí nghiệm gốc, không thay cấu hình B=51 hoặc
viết lại điểm test. Không tuyên bố B=51 tối ưu tổng quát hay số CV là điểm test.

Các nhánh của mẫu lỗi được lấy từ mô hình gốc51cây. Các đặc trưng minh họa
được chọn từ tần suất sử dụng tại nút gốc của các cây đã học, không chọn theo
độ đẹp của hình hoặc nhãn mẫu test. Phân tích mô tả quyết định của mô hình,
không xác định nguyên nhân y khoa hoặc hiệu chỉnh xác suất bệnh.

Không tạo hay chỉnh sửa file Word. Phần văn bản để chèn vào báo cáo lưu tại
`report/Bo_sung_phan_tich_va_thuc_nghiem.md`.
