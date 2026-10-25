# Nội dung bổ sung theo form báo cáo sáu chương

Các mục dưới đây dùng cho bản người dùng tự dàn trong Word. Không tạo hoặc
thay thế Word/PDF đã có. Điểm test gốc và số liệu 10 seed giữ nguyên.

## Bổ sung sau mục 5.9: Khảo sát ảnh hưởng của số cây

### Thiết kế khảo sát

Khảo sát bổ sung xét B∈{1,5,11,21,51,101}, chỉ trên 426 quan sát train của lần
chia seed 42. Tập test 143 quan sát không tham gia khảo sát.

Train được chia thành 5 fold ngoài có phân tầng. Trong phần học của mỗi fold,
CV 5 fold bên trong chọn độ sâu từ {2, 3, 4, 5, 6} bằng cây đơn. Sau đó, từng cấu
hình số cây được học trên phần học và đánh giá trên fold ngoài còn lại.
Mọi B dùng cùng các fold, độ sâu và seed tương ứng để giảm khác biệt do cách
chia hoặc khởi tạo. Độ sâu được chọn trong 5 fold lần lượt là 2, 6, 2, 2, 6.

Cách thực hiện bảo đảm fold đánh giá ngoài không tham gia chọn độ sâu.
Đây là phân tích bổ sung sau thí nghiệm gốc, không đổi cấu hình 51 cây hoặc
đánh giá lại test để chọn kết quả đẹp. SD giữa các fold chỉ mô tả biến thiên.

| Số cây B | Accuracy CV trung bình (%) | Balanced accuracy CV trung bình ± SD |
|---:|---:|---:|
|1|92,72|92,33 ± 2,11|
|5|93,66|92,83 ± 1,82|
|11|95,08|94,44 ± 3,11|
|21|95,31|94,88 ± 2,22|
|51|95,78|95,26 ± 2,45|
|101|95,54|95,07 ± 2,53|

Trung bình tính theo %, SD tính theo điểm phần trăm. Nguồn:
`outputs/extensions/tree_counts_summary.csv`.

Balanced accuracy tăng từ 92,33% với 1 cây lên 95,26% với 51 cây trong khảo sát.
Tăng tiếp lên 101 cây không cải thiện, điểm giảm nhẹ còn 95,07%.
Recall không tăng đồng loạt theo B; chẳng hạn 5 cây thấp hơn 1 cây ở chỉ số này.
Các thanh sai số chồng lấn đáng kể, nên không khẳng định khác biệt nhỏ có ý
nghĩa thống kê. Chưa đo thời gian chạy, không kết luận định lượng về tốc độ.

Trong sáu cấu hình, 51 cây có balanced accuracy CV trung bình cao nhất. Kết quả
này cung cấp thêm căn cứ thực nghiệm cho cấu hình ban đầu, không chứng minh
51 tối ưu với mọi dữ liệu hay seed. Điểm CV 95,26% không được thay cho điểm
test 95,10% hoặc mean 10 seed 94,76%: ba số thuộc ba quy trình đánh giá khác nhau.

Chèn hình: `outputs/extensions/tree_count_cv.png`.

Caption gợi ý: **Hình 5.3. Ảnh hưởng của số cây trên tập train seed 42. Mỗi
cấu hình được đánh giá bằng 5 fold ngoài; độ sâu chọn trong phần học của từng
fold. Thanh sai số là SD giữa các fold, không phải khoảng tin cậy.**

## Thay mục 5.11: Phân tích một trường hợp dự đoán sai

### Đặc điểm quan sát

Mẫu tại vị trí test 2 tương ứng hàng 291, nhãn thật là lành. Bagging cho 27 phiếu
ác và 24 phiếu lành nên dự đoán ác. Biên phiếu là (27−24)/51 ≈ 5,88 điểm phần trăm,
thể hiện sự bất đồng tương đối lớn giữa các cây. Đây không phải thước đo xác
suất bệnh hoặc ranh giới lâm sàng.

Ba đặc trưng minh họa được chọn từ tần suất sử dụng tại nút gốc của 51 cây
đã học trên train. Không lựa chọn theo nhãn mẫu lỗi hoặc theo mức độ thuận
lợi cho nhận xét. `worst perimeter`, `worst concave points`, `worst radius`
được dùng tại nút gốc lần lượt 16, 14, 9 cây.

| Đặc trưng | Giá trị mẫu 291 | Trung vị train lành | Trung vị train ác |
|---|---:|---:|---:|
|worst perimeter|109,10|86,82|135,10|
|worst concave points|0,14890|0,07174|0,18270|
|worst radius|16,25|13,35|20,42|

Mẫu 291 có giá trị lớn hơn trung vị nhóm lành và nhỏ hơn trung vị nhóm ác
ở cả ba đặc trưng. Cụ thể, các giá trị đều vượt tứ phân vị 75% của nhóm lành
nhưng thấp hơn tứ phân vị 25% của nhóm ác. Điều này cho thấy các giá trị nằm
giữa hai vùng trung tâm của phân bố train trên những đặc trưng được xem xét.
Phân tích ba đặc trưng chưa đủ xác định ranh giới quyết định trong không gian
30 chiều và không giải thích nguyên nhân y khoa.

Chèn hình: `outputs/extensions/error_feature_context.png`.

Caption gợi ý: **Hình 5.5. Ba đặc trưng của mẫu 291 so với phân bố hai lớp trên
train. Hộp biểu diễn Q1–Q3, vạch giữa là trung vị; đường nét đứt biểu diễn giá
trị mẫu lỗi. Tên đặc trưng được giữ nguyên từ dataset.**

### Vì sao hai cây dự đoán khác nhau?

Truy vết đường đi cho thấy cây 1 đi qua các điều kiện:

1. worst radius=16,25 ≤16,79500;
2. worst concave points=0,14890 >0,14315;
3. worst symmetry=0,29620 >0,28855.

Mẫu đi tới lá có 18 lượt mẫu bootstrap, tất cả nhãn ác, nên cây 1 dự đoán ác.
Độ thuần của lá trên bootstrap không bảo đảm dự đoán đúng quan sát mới.

Cây 2 đi qua các điều kiện:

1. mean concave points=0,04819 ≤0,04989;
2. worst symmetry=0,29620 >0,16385;
3. worst perimeter=109,10 ≤127,20.

Lá của cây 2 có khoảng 98,84% lượt mẫu bootstrap mang nhãn lành, nên dự đoán
lành. Các số ngưỡng được làm tròn để trình bày; JSON lưu giá trị đầy đủ.

Hai cây sử dụng đặc trưng và ngưỡng khác nhau do được học trên các bootstrap
khác nhau. Đây là bằng chứng cụ thể về nguồn gốc bất đồng của các cây.
Truy vết hai cây chỉ minh họa; dự đoán cuối vẫn lấy đủ 51 phiếu.

### Cùng điểm tổng hợp không có nghĩa cùng lỗi

Bagging và RF khác dự đoán ở đúng 2 mẫu test, đều có nhãn thật lành:

| Hàng dữ liệu gốc | Nhãn thật | Bagging | Random Forest |
|---:|---|---|---|
|291|Lành|Ác — sai|Lành — đúng|
|128|Lành|Lành — đúng|Ác — sai|

Hai mô hình có thể cùng accuracy 95,10%, cùng TP 49, FN 4, FP 3, TN 87 mà vẫn mắc
lỗi trên các quan sát khác nhau. Không thể kết luận RF luôn tốt hơn từ việc
RF dự đoán đúng riêng mẫu 291. Nguồn: `bagging_rf_disagreements.csv`.

## Biên tập để giảm lặp

| Phần | Nội dung giữ lại | Nội dung chuyển/bỏ |
|---|---|---|
|Chương 2|Định nghĩa, công thức, ý tưởng của Bagging/Voting/OOB|Không đưa kết quả 95,10% và phép tính test vào đây|
|Chương 3|Một ví dụ 5 mẫu xuyên suốt: Gini, ngưỡng, phiếu, OOB|Không nhắc lại đầy đủ các định nghĩa chương 2|
|Chương 4|Dữ liệu, train/test, CV, cấu hình, chỉ số|Không phân tích kết quả mô hình trước chương 5|
|Chương 5|Code, bằng chứng, kết quả, khảo sát số cây, phân tích lỗi|Không mở lại tổng quan bốn họ Ensemble|
|Chương 6|Kết quả chính, hạn chế và bước tiếp theo|Không lặp bảng số liệu hoặc công thức|

Thay mục 6.2 bằng:

“Khảo sát số cây đã được bổ sung trên sáu cấu hình, nhưng chỉ sử dụng tập
train của seed 42 và một cách chia CV ngoài. Vì thế, chưa thể coi 51 cây là
cấu hình tối ưu tổng quát. Độ sâu trong quy trình gốc vẫn được chọn bằng
cây đơn rồi dùng chung cho các mô hình, chưa tối ưu riêng từng ensemble.
Các holdout của thí nghiệm 10 seed có thể giao nhau; chưa có kiểm định ngoài
trên một quần thể độc lập. Phân tích mẫu lỗi giải thích hành vi mô hình
trong dữ liệu khảo sát, chưa xác định nguyên nhân y khoa hoặc giá trị
ứng dụng lâm sàng.”

Thay phần kết luận dài bằng:

“Báo cáo đã triển khai và kiểm tra cơ chế bootstrap, hard voting và OOB của
Bagging cây. Trên 10 holdout, accuracy trung bình đạt 94,76%, cao hơn cây đơn
trong phạm vi khảo sát. Khảo sát bổ sung trên train cho thấy tăng số cây
có lợi đến một mức nhất định; 101 cây không cải thiện so với 51 cây ở thiết
kế CV đã chạy. Phân tích mẫu 291 cho thấy các cây có thể học những ngưỡng
khác nhau, bỏ phiếu bất đồng và vẫn tạo kết quả sai. Kết quả hỗ trợ việc
hiểu cơ chế học tổ hợp, đồng thời cần giữ giới hạn khi suy rộng.”

## Kiểm tra hình thức theo form

- Font Times New Roman 13; giãn dòng 1,5; căn đều; lề trên/trái 3,5 cm, dưới 3 cm, phải 2 cm.
- Khảo sát chèn sau mục 5.9 dùng Hình 5.3 mới; hình phiếu 27:24 cũ đổi thành
  Hình 5.4; hình đặc trưng mẫu lỗi là Hình 5.5. Dùng Caption để cập nhật danh mục.
- Bảng khảo sát số cây là Bảng 5.10; bảng OOB cũ chuyển thành Bảng 5.11;
  bảng đặc trưng mẫu lỗi và bảng bất đồng Bagging/RF là Bảng 5.12 và 5.13.
- Có ảnh 300 dpi và PDF vector đi kèm cho hai hình mới.
- Caption hình ở dưới, caption bảng ở trên; dùng Insert Caption và Cross-reference.
- Bảng số cây ghi rõ CV, trung bình theo %, SD theo điểm phần trăm. Không gọi số CV là số test.
- Nguồn hình/bảng mới: Kết quả chương trình nhóm; không gán thành số liệu Breiman.
- Giữ trích dẫn [1]–[7] khớp tài liệu tham khảo đã có; không cần thêm nguồn ngoài
  cho bảng thực nghiệm tự sinh.
- Dùng Heading và Caption để cập nhật mục lục/danh mục; tránh gõ số trang tay.
- Cập nhật tất cả field bằng Ctrl+A, F9 rồi xuất PDF; kiểm tra lại các trang có hình,
  bảng và tiêu đề. Chưa thể xác nhận bố cục bản Word người dùng tự dàn khi chưa có file.
- Cập nhật kiểm thử thành 24/24: 22 kiểm thử gốc và 2 kiểm thử mới về ranh giới CV
  và truy vết nhánh cây.

## Tái lập

`.venv/bin/python experiments/report_extensions.py`

Windows thay `.venv/bin/python` bằng `.venv\Scripts\python.exe`.
Toàn bộ dữ liệu nguồn, chỉ số các fold, nhánh cây và hình ở `outputs/extensions/`.
