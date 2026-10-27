# Báo cáo tiểu luận đề 5

Bản dùng để đọc và nộp là báo cáo đã hoàn thiện trực tiếp theo form của nhóm:

- [Word có thể chỉnh sửa](Bao_cao_Ensemble_Learning_da_hoan_thien.docx).
- [PDF đã kiểm tra bố cục, 51 trang](Bao_cao_Ensemble_Learning_da_hoan_thien.pdf).

Báo cáo gồm sáu chương: mở đầu; cơ sở lý thuyết; thuật toán và ví dụ tính tay;
bài toán và thiết kế thực nghiệm; triển khai, kết quả và thảo luận; kết luận
và hướng phát triển. Phụ lục hướng dẫn tái lập mã và đối chiếu tệp kết quả.
Các công thức, code, khảo sát số cây, truy vết mẫu sai và đối chứng 2 × 2 đã
được tích hợp vào cùng bản này. Bộ mã có 26 kiểm thử đạt.

`tools/prepare_submission.py` giữ nguyên cặp Word/PDF hoàn thiện và đóng gói
cùng code, slide, kết quả. Khi sửa Word, xuất và kiểm tra lại PDF tương ứng
trước khi đóng gói; mã không tự viết lại báo cáo đã chỉnh theo form.

## Mã và nội dung hỗ trợ

- `group_info.json`: thông tin nhóm dùng chung cho các tài liệu sinh tự động.
- `Bo_sung_phan_tich_va_thuc_nghiem.md`: nội dung khảo sát số cây và phân tích lỗi.
- `Nang_cao_phan_tich_hoc_thuat.md`: nội dung đối chứng và cơ sở thống kê.
- `../experiments/README.md`: cách tái lập hai phân tích bổ sung.

## Bản nháp sinh tự động trước đây

Các tệp `Bao_cao_De_5_Ensemble_Learning.docx`, `.pdf`, `.md` là bản nháp bốn
chương trước khi chỉnh theo form; chúng được giữ để tham khảo. `create_report.py`
chỉ tạo lại bản nháp này, không dựng lại báo cáo hoàn thiện sáu chương.
Khi có bản hoàn thiện, trình đóng gói loại ba tệp nháp khỏi gói nộp để tránh
nhầm phiên bản. Chỉ dùng lệnh tạo nháp dưới đây khi cần tham khảo:

```bash
.venv/bin/python -m pip install -r report/requirements.txt
.venv/bin/python de_5_ensemble_learning.py
.venv/bin/python report/create_report.py
```

Trên Windows thay `.venv/bin/python` bằng `.venv\Scripts\python.exe`.
