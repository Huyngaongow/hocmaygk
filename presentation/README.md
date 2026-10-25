# PowerPoint đề 5

- `../De_5_Ensemble_Learning.pptx`: 26 slide, đồ họa và chữ chỉnh sửa được;
  mỗi trang có lời thuyết trình trong phần **Notes**.
- `../De_5_Ensemble_Learning.pdf`: bản xem nhanh của cùng bộ slide.
- `loi_thuyet_trinh.md`: lời thuyết trình tách thành văn bản.
- `create_presentation.py`: mã tạo lại PowerPoint từ `outputs/results.json`.
- `../report/Bao_cao_De_5_Ensemble_Learning.docx` và PDF cùng tên: báo cáo
  bài viết; khác với bản PDF xuất slide ở thư mục gốc.

Thông tin thành viên, MSSV và giảng viên lấy từ `../report/group_info.json`;
chỉnh ở một nơi rồi tạo lại báo cáo và slide để giữ thống nhất. Không tự điền
tên lớp chưa được cung cấp. Nhóm có tối đa 3 thành viên theo đề.

Dành khoảng 15–20 phút cho 24 slide chính, nói ngắn phần mở rộng slide 10–11
khi cần; dùng 2 slide phụ lục để hỏi đáp. Đây là thời lượng tập luyện gợi ý,
không phải quy định trong đề. Cả hai thành viên cần tham gia trình bày và hiểu
code. Lời thuyết trình có gợi ý chuyển lời sau slide 11; đó là phương án chuẩn
bị, không phải xác nhận lịch sử đóng góp.

Để tạo lại sau khi chạy thí nghiệm theo README ở thư mục gốc:

```bash
python3 -m pip install -r presentation/requirements.txt
python3 de_5_ensemble_learning.py
python3 examples/toy_bagging.py --output-dir outputs/toy
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

Ví dụ slide 7–9 dùng xuyên suốt `x=[1,2,3,4,5]`, nhãn lành/lành/ác/ác/ác,
ba bootstrap cố định và ba cây một mức. Mã `examples/toy_bagging.py` tính
ngưỡng `2,5; 3; 2,5`, Gini, dự đoán tại `x=2,8`, tổng phiếu `2:1` và OOB.
Ngưỡng và phiếu trên slide được lấy trực tiếp từ hàm tính ví dụ; đây là dữ liệu
giả lập, không phải một ca bệnh. Mẫu mới không có nhãn thật nên không kết luận
dự đoán đúng/sai. Ba bootstrap được chọn để nhìn rõ cơ chế; Bagging thực nghiệm
vẫn lấy mẫu ngẫu nhiên có hoàn lại.

Phần chính ưu tiên trực giác và ví dụ tính được. Công thức phương sai và chi
tiết cập nhật AdaBoost nằm trong Notes để dùng nếu được hỏi. Boosting/Stacking
là phần lý thuyết mở rộng, chưa được đo thực nghiệm trong bài này.
