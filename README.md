# Đề 5 — Ensemble Learning

Nguyễn Nghĩa Hiếu — 52400013; Trần Quốc Bảo — 52400102.
Giảng viên: TS. Trần Lương Quốc Đại.

## Tài liệu

- [Báo cáo PDF](52400013_52400102.pdf)
- [PowerPoint: 18 slide chính và 6 dự phòng](52400013_52400102.pptx)
- [Mã nguồn và hướng dẫn chạy](source/README.md)

Bộ tài liệu được cập nhật từ ZIP của nhóm. **Chưa có file Word (.docx)**;
đề yêu cầu nộp cả Word và PDF, cần bổ sung bản Word nguồn tương ứng PDF này.

## Chạy thực nghiệm

Mở terminal tại thư mục `source`, dùng Python 3.11 trở lên (đã kiểm tra Python 3.12):

```bash
cd source
python -m pip install -r requirements.txt
python de_5_ensemble_learning.py
python examples/toy_bagging.py
python experiments/report_extensions.py
python experiments/controlled_comparison.py
python experiments/ensemble_families.py
```

Dữ liệu có sẵn trong scikit-learn. Kết quả được tạo trong `source/outputs/`.
Bagging tự triển khai bootstrap, hard voting và OOB; cây cơ sở và các mô hình
đối chiếu dùng scikit-learn. Mười lần chia seed 42–51; SD mẫu không phải CI.

PDF và PPTX được giữ nguyên như ZIP. Phần hướng dẫn kiểm thử trong phụ lục PDF
thuộc bộ repo đầy đủ trước đây; bản nộp rút gọn không đóng kèm `tests/`.
