# Đề 5 — Ensemble Learning

Nguyễn Nghĩa Hiếu — 52400013; Trần Quốc Bảo — 52400102.
Giảng viên: TS. Trần Lương Quốc Đại.

## Tài liệu

- [Báo cáo Word](52400013_52400102.docx)
- [Báo cáo PDF](52400013_52400102.pdf)
- [PowerPoint: 18 slide chính và 6 dự phòng](52400013_52400102.pptx)
- [Mã nguồn và hướng dẫn chạy](52400013_52400102/README.md)

Bản Word mới nhất được bổ sung từ file nhóm cung cấp sau gói ZIP.
PDF hiện là bản trong ZIP trước đó; cần xuất lại PDF từ Word sau khi
hoàn tất các chỉnh sửa cuối để đồng bộ hai định dạng.

## Chạy thực nghiệm

Mở terminal tại thư mục gốc repo, rồi chuyển vào `52400013_52400102/` như dòng đầu
bên dưới. Dùng Python 3.11 trở lên (đã kiểm tra Python 3.12); xem hướng dẫn
tạo môi trường riêng cho Windows/Linux trong [README mã nguồn](52400013_52400102/README.md).

```bash
cd 52400013_52400102
python -m pip install -r requirements.txt
python de_5_ensemble_learning.py
python examples/toy_bagging.py
python experiments/report_extensions.py
python experiments/controlled_comparison.py
python experiments/ensemble_families.py
```

Dữ liệu có sẵn trong scikit-learn. Kết quả được tạo trong `52400013_52400102/outputs/`.
Bagging tự triển khai bootstrap, hard voting và OOB; cây cơ sở và các mô hình
đối chiếu dùng scikit-learn. Mười lần chia seed 42–51; SD mẫu không phải CI.

PDF và PPTX được giữ nguyên như ZIP. Phần hướng dẫn kiểm thử trong phụ lục PDF
thuộc bộ repo đầy đủ trước đây; bản nộp rút gọn không đóng kèm `tests/`.
