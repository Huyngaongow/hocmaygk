# PowerPoint đề 5

- `../De_5_Ensemble_Learning.pptx`: 26 slide, đồ họa và chữ chỉnh sửa được;
  mỗi trang có lời thuyết trình trong phần **Notes**.
- `../De_5_Ensemble_Learning.pdf`: bản xem nhanh của cùng bộ slide.
- `loi_thuyet_trinh.md`: lời thuyết trình tách thành văn bản.
- `create_presentation.py`: mã tạo lại PowerPoint từ `outputs/results.json`.

**Trước khi nộp:** điền tên thành viên và lớp tại slide 1. Dành khoảng
15–20 phút cho 24 slide chính (rút gọn phần mở rộng khi cần), dùng 2 slide phụ lục để hỏi đáp.
Thời lượng này là gợi ý, không phải quy định được nêu trong đề.

Để tạo lại sau khi chạy thí nghiệm theo README ở thư mục gốc:

```bash
python3 -m pip install -r presentation/requirements.txt
python3 de_5_ensemble_learning.py
python3 presentation/create_presentation.py
```

Lệnh tạo lại sẽ thay thế PowerPoint và tệp lời thuyết trình; hãy lưu riêng
nếu đã chỉnh sửa thủ công. Thư viện tạo slide tách khỏi dependencies chạy
mô hình, không cần cài để chạy thí nghiệm Python.

Nếu có LibreOffice, có thể tạo lại PDF từ PowerPoint:

```bash
soffice --headless --convert-to pdf --outdir . De_5_Ensemble_Learning.pptx
```

Số liệu tham chiếu trên slide lấy từ seed 42, 426 mẫu train và 143 mẫu test.
Bản nâng cấp thêm kết quả 10 holdout phân tầng (seeds 42–51), mean và SD mẫu,
đánh giá hard-vote OOB với coverage và ví dụ bất đồng 27/24 có dự đoán sai.
Các test giữa seed có thể giao nhau; SD không phải khoảng tin cậy độc lập.
Độ sâu chọn bằng CV trên train của mỗi seed, rồi dùng chung cho ba mô hình.
OOB được tính sau bước chọn độ sâu trên train, không phải điểm độc lập với tuning.

Script tạo slide kiểm tra cấu hình/kết quả tham chiếu để tránh trộn các số liệu
cố định với kết quả của `--repeats 1` hoặc cấu hình khác. Demo nhanh nên dùng
`python de_5_ensemble_learning.py --repeats 1 --output-dir outputs/quick`;
tạo lại slide cần chạy đầy đủ cấu hình mặc định vào `outputs/` như trên.

Các ví dụ tính tay được ghi rõ; Boosting/Stacking là phần lý thuyết mở rộng,
không được nhận là các mô hình đã đo thực nghiệm trong bài này.
