# PowerPoint đề 5

- `../De_5_Ensemble_Learning.pptx`: 24 slide, đồ họa và chữ chỉnh sửa được;
  mỗi trang có lời thuyết trình trong phần **Notes**.
- `../De_5_Ensemble_Learning.pdf`: bản xem nhanh của cùng bộ slide.
- `loi_thuyet_trinh.md`: lời thuyết trình tách thành văn bản.
- `create_presentation.py`: mã tạo lại PowerPoint từ `outputs/results.json`.

**Trước khi nộp:** điền tên thành viên và lớp tại slide 1. Dành khoảng
15–20 phút cho 22 slide chính, dùng 2 slide phụ lục để hỏi đáp khi cần.
Thời lượng này là gợi ý, không phải quy định được nêu trong đề.

Để tạo lại sau khi chạy thí nghiệm theo README ở thư mục gốc:

```bash
python3 -m pip install -r presentation/requirements.txt
python3 presentation/create_presentation.py
```

Lệnh tạo lại sẽ thay thế PowerPoint và tệp lời thuyết trình; hãy lưu riêng
nếu đã chỉnh sửa thủ công. Thư viện tạo slide tách khỏi dependencies chạy
mô hình, không cần cài để chạy thí nghiệm Python.

Nếu có LibreOffice, có thể tạo lại PDF từ PowerPoint:

```bash
soffice --headless --convert-to pdf --outdir . De_5_Ensemble_Learning.pptx
```

Số liệu trên slide lấy từ lần chạy seed 42, 426 mẫu train và 143 mẫu test.
Các ví dụ tính tay được ghi rõ; Boosting/Stacking là phần lý thuyết mở rộng,
không được nhận là các mô hình đã đo thực nghiệm trong bài này.
