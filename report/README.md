# Báo cáo tiểu luận đề 5

- `Bao_cao_De_5_Ensemble_Learning.docx`: báo cáo Word có thể chỉnh sửa.
- `Bao_cao_De_5_Ensemble_Learning.pdf`: bản PDF của cùng báo cáo, tạo bằng LibreOffice.
- `Bao_cao_De_5_Ensemble_Learning.md`: bản nội dung để đọc và quản lý phiên bản.
- `group_info.json`: thông tin nhóm dùng chung cho bìa báo cáo và slide.
- `create_report.py`: tạo lại Word và Markdown từ kết quả chạy thật và ví dụ tính tay.

Báo cáo có bốn chương tương ứng bốn nội dung chuyên môn trong đề: nguyên lý,
quy trình/ví dụ, bài toán ứng dụng, triển khai/kết quả. Lý thuyết tập trung
vào Bagging; Boosting và Stacking chỉ phục vụ tổng quan. Không cần học thuộc
những phần mở rộng để giải thích được demo.

Từ thư mục gốc repository, sau khi đã cài dependencies mô hình:

```bash
.venv/bin/python -m pip install -r report/requirements.txt
.venv/bin/python de_5_ensemble_learning.py
.venv/bin/python report/create_report.py
soffice --headless --convert-to pdf --outdir report report/Bao_cao_De_5_Ensemble_Learning.docx
```

Để mục lục có số trang đúng theo bản PDF đã xuất, cài Poppler (`pdftotext`)
và chạy thêm:

```bash
.venv/bin/python report/create_report.py --toc-pdf report/Bao_cao_De_5_Ensemble_Learning.pdf
soffice --headless --convert-to pdf --outdir report report/Bao_cao_De_5_Ensemble_Learning.docx
```

Trên Windows thay `.venv/bin/python` bằng `.venv\Scripts\python.exe`.
Chỉnh sửa `group_info.json` trước khi tạo lại để không phải sửa tên ở nhiều nơi.
Lệnh tạo báo cáo ghi đè Word và Markdown đã có; lệnh chuyển đổi ghi đè PDF.
Lưu riêng nếu đã chỉnh tay bản Word. Kết quả đầu vào phải là lượt mặc định
10 seed tại `outputs/results.json`, không dùng lượt demo nhanh một seed.
