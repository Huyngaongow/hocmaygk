# PowerPoint đề 5

- `../De_5_Ensemble_Learning.pptx`: 28 slide, gồm 24 slide chính và 4 slide dự phòng;
  chữ, bảng, sơ đồ và biểu đồ chỉnh sửa được trong PowerPoint;
  mỗi trang có lời thuyết trình trong phần **Notes**.
- `../De_5_Ensemble_Learning.pdf`: bản xem nhanh của cùng bộ slide.
- `loi_thuyet_trinh.md`: lời thuyết trình tách thành văn bản.
- `create_presentation.py`: mã tạo lại PowerPoint từ kết quả gốc và hai phân tích bổ sung.
- `assets/tdtu_logo.png`: logo lấy từ biểu mẫu báo cáo của nhóm.
- `../report/Bao_cao_Ensemble_Learning_da_hoan_thien.docx` và PDF cùng tên: báo cáo
  bài viết; khác với bản PDF xuất slide ở thư mục gốc.

Thông tin thành viên, MSSV và giảng viên lấy từ `../report/group_info.json`;
chỉnh ở một nơi rồi tạo lại slide, đồng thời cập nhật báo cáo Word để giữ thống nhất. Không tự điền
tên lớp chưa được cung cấp. Nhóm có tối đa 3 thành viên theo đề.

Dành khoảng 18–22 phút để luyện 24 slide chính; dùng 4 slide phụ lục để hỏi đáp.
Đây là thời lượng tập luyện gợi ý,
không phải quy định trong đề. Cả hai thành viên cần tham gia trình bày và hiểu
code. Lời thuyết trình có gợi ý chuyển lời sau slide 13; đó là phương án chuẩn
bị, không phải xác nhận lịch sử đóng góp.

Để tạo lại sau khi chạy thí nghiệm theo README ở thư mục gốc:

```bash
python3 -m pip install -r presentation/requirements.txt
python3 de_5_ensemble_learning.py
python3 examples/toy_bagging.py --output-dir outputs/toy
python3 experiments/report_extensions.py
python3 experiments/controlled_comparison.py
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

Ví dụ slide 5–7 dùng xuyên suốt `x=[1,2,3,4,5]`, nhãn lành/lành/ác/ác/ác,
ba bootstrap cố định và ba cây một mức. Mã `examples/toy_bagging.py` tính
ngưỡng `2,5; 3; 2,5`, Gini, dự đoán tại `x=2,8`, tổng phiếu `2:1` và OOB.
Ngưỡng và phiếu trên slide được lấy trực tiếp từ hàm tính ví dụ; đây là dữ liệu
giả lập, không phải một ca bệnh. Mẫu mới không có nhãn thật nên không kết luận
dự đoán đúng/sai. Ba bootstrap được chọn để nhìn rõ cơ chế; Bagging thực nghiệm
vẫn lấy mẫu ngẫu nhiên có hoàn lại.

Slide 17 khảo sát số cây chỉ trên train. Slide 18–19 phân tích mẫu sai 291.
Slide 20–22 trình bày đối chứng 2 × 2 giữ chung bootstrap và seed từng cây;
nhóm sqrt tự xây không đồng nhất với Random Forest của sklearn. Phân tích
theo cặp nằm cùng bảng mười seed ở slide 16. Mọi số liệu lấy từ JSON thực,
không gõ lại kết quả làm tròn để dựng bảng.

Thiết kế dùng khung hình 16:9, nền sáng, màu navy/teal thống nhất và không
đổ bóng; màu coral dùng cho lỗi hoặc nhãn ác tính. Hai đoạn code tách riêng
để dễ đọc khi chiếu. Slide 24 kết thúc phần chính; phụ lục gồm truy vết cây,
công thức chỉ số, Boosting/Stacking và tài liệu tham khảo. Công thức sâu và
chi tiết cập nhật AdaBoost nằm trong Notes. Các phương pháp này chỉ được
giới thiệu lý thuyết, chưa được đo thực nghiệm.
