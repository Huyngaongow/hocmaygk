# Nâng cao phần phân tích học thuật — nội dung để đưa vào Word

Phần này bổ sung cho báo cáo sáu chương, không tạo hay chỉnh sửa Word.
Các kết quả mới là phân tích bổ sung trên train, giữ nguyên kết quả test gốc.

## Bổ sung cuối mục 1.2: Câu hỏi nghiên cứu

Báo cáo đặt ra ba câu hỏi nghiên cứu. Thứ nhất, Bagging có cải thiện kết quả
so với cây đơn một cách nhất quán trên những lần chia đã khảo sát hay không?
Thứ hai, tăng số cây ảnh hưởng thế nào đến kết quả và liệu lợi ích có tiếp tục
tăng khi số cây lớn hơn? Thứ ba, khi kiểm soát các yếu tố khác, cách chọn đặc
trưng và quy tắc tổng hợp ảnh hưởng thế nào đến chất lượng cây cơ sở, mức
bất đồng và kết quả của tổ hợp?

Đóng góp thực nghiệm của báo cáo là triển khai minh bạch cơ chế Bagging,
đối chiếu các mô hình trên cùng lần chia, khảo sát số cây trên train và thực
hiện đối chứng để giải thích cơ chế. Các phương pháp nền tảng dựa trên tài
liệu đã trích dẫn; kết quả và nhận xét gắn với giao thức thực nghiệm cụ thể.

## Bổ sung Chương 2: Cơ sở thống kê của bootstrap

Với N quan sát, xác suất một quan sát không được chọn trong một bootstrap
gồm N lượt lấy có hoàn lại là q = (1−1/N)^N. Nếu U là số quan sát khác nhau
xuất hiện trong bootstrap, tính tuyến tính của kỳ vọng cho:

**E[U] = N × [1 − (1 − 1/N)^N].**

Với N = 426, số quan sát khác nhau kỳ vọng xấp xỉ 269,47, tương ứng 63,26% tập
train. Số quan sát OOB kỳ vọng của mỗi cây là 156,53. Với 51 cây, mỗi quan sát
train kỳ vọng nhận khoảng 18,74 phiếu OOB.

Đối chiếu với 51 bootstrap thực của mô hình seed 42, số quan sát khác nhau
trung bình là 268,04, nằm trong khoảng 254–281 giữa các cây; số phiếu OOB
trung bình trên mỗi quan sát là 18,91. Đây là các đại lượng ngẫu nhiên nên
không bắt buộc bằng đúng kỳ vọng trong một lượt chạy.

Kết quả làm rõ vì sao một bootstrap có 426 lượt lấy nhưng thường chỉ chứa
khoảng 63% quan sát khác nhau, đồng thời giải thích nguồn dữ liệu đánh giá OOB.

### Trực giác về phương sai và tương quan

Nếu các dự đoán số có cùng phương sai σ² và cùng tương quan cặp ρ, phương
sai của trung bình B dự đoán là:

**Var(h̄) = σ²[ρ + (1−ρ)/B].**

Với B = 51, ρ = 0,2 cho 0,216 σ², còn ρ = 0,8 cho 0,804 σ². Những mô hình quá giống
nhau vẫn để lại một thành phần dao động lớn ngay cả khi tăng số lượng.
Công thức cung cấp trực giác cho trung bình dự đoán số dưới các giả thiết
trên, không phải công thức trực tiếp tính lỗi phân loại hard voting. Các giá
trị ρ là minh họa, không được suy từ mức bất đồng D trong thí nghiệm.

## Thêm mục 4.9: Thiết kế đối chứng có kiểm soát

Để phân biệt ảnh hưởng của xét đặc trưng và quy tắc tổng hợp, báo cáo thực
hiện thiết kế 2 × 2 trên 426 mẫu train của seed 42. Bốn cấu hình gồm:

| Đặc trưng xét tại nút | Quy tắc tổng hợp | Vai trò |
|---|---|---|
|Toàn bộ|Hard voting|Mốc tham chiếu|
|Toàn bộ|Trung bình xác suất|Thay riêng quy tắc tổng hợp|
|sqrt|Hard voting|Thay cách xét đặc trưng|
|sqrt|Trung bình xác suất|Kết hợp hai lựa chọn|

Mọi cấu hình sử dụng 51 cây và cùng 5 fold ngoài. Trong phần học của mỗi fold,
CV 5 fold chọn độ sâu bằng cây đơn xét toàn bộ đặc trưng, sau đó dùng chung
độ sâu cho bốn cấu hình. Khi đổi cách xét đặc trưng, giữ nguyên bootstrap
và seed của từng cây. Trong cùng nhóm đặc trưng, hard và soft sử dụng chính
cùng những cây đã học.

Cách thiết kế cho phép đối chiếu từng yếu tố ở độ sâu được kiểm soát. Tuy
nhiên, đây chưa phải tối ưu riêng từng biến thể. Nhóm sqrt tự xây được gọi
là “Bagging có ngẫu nhiên hóa đặc trưng”, không đồng nhất với kết quả chạy
RandomForestClassifier trong thí nghiệm gốc. Tập test 143 mẫu không tham gia.

## Thêm mục 5.13: Kết quả đối chứng và tính đa dạng

### Đối chiếu bốn cấu hình

| Xét đặc trưng | Tổng hợp | Accuracy CV (%) | Balanced accuracy CV trung bình ± SD |
|---|---|---:|---:|
|Toàn bộ|Hard|95,78|95,26 ± 2,45|
|Toàn bộ|Soft|95,78|95,26 ± 2,45|
|sqrt|Hard|94,37|93,62 ± 3,48|
|sqrt|Soft|94,13|93,44 ± 3,77|

Trung bình tính theo %, SD theo điểm phần trăm. Nguồn:
`outputs/extensions/controlled_comparison_summary.csv`.

Với các cây xét toàn bộ đặc trưng, hard và soft tạo cùng nhãn cho cả 426 lượt
dự đoán ngoài fold. Trong nhóm sqrt, hai quy tắc khác nhãn ở một quan sát;
soft có balanced accuracy trung bình thấp hơn khoảng 0,19 điểm phần trăm.
Điều này không chứng minh hai quy tắc luôn tương đương hoặc soft luôn kém
hơn; nó mô tả kết quả của các cây và dữ liệu đang khảo sát.

Khi giữ hard voting và đổi từ toàn bộ đặc trưng sang sqrt, balanced accuracy
giảm khoảng 1,63 điểm phần trăm. Các chênh lệch được đối chiếu trên cùng fold;
chưa thực hiện kiểm định để khẳng định ý nghĩa thống kê.

### Đo mức bất đồng và chất lượng cây cơ sở

Với v_ic là số cây dự đoán lớp c cho quan sát i, mức bất đồng trung bình giữa
các cặp cây trong một fold được tính:

**D = (1/N) × Σ_i [B² − Σ_c(v_ic²)] / [B(B−1)].**

D là tỷ lệ các cặp cây dự đoán khác nhau, trung bình trên các quan sát đánh
giá. Chỉ số được tính trong từng fold rồi lấy trung bình giữa 5 fold.
Với hai lớp và 51 cây, D tối đa khoảng 50,98% khi phiếu chia 26:25, không phải 100%.
D đo bất đồng nhãn, không trực tiếp đo tương quan lỗi hoặc độc lập thống kê.

| Cách xét đặc trưng | Balanced accuracy trung bình của một cây (%) | Mức bất đồng D (%) |
|---|---:|---:|
|Toàn bộ|91,67|7,99|
|sqrt|89,75|10,52|

Ngẫu nhiên hóa đặc trưng làm D tăng từ 7,99% lên 10,52%, nhưng chất lượng cây
cơ sở giảm từ 91,67% xuống 89,75%. Đồng thời, balanced accuracy tổ hợp hard
giảm từ 95,26% xuống 93,62%. Vì vậy, gia tăng đa dạng không tự động làm tổ
hợp tốt hơn. Cần xem đồng thời chất lượng cây cơ sở và cách các cây khác
nhau. Đây là kết luận quan sát được trong thiết kế hiện tại, không phải
quy luật rằng xét toàn bộ đặc trưng luôn tốt hơn ngẫu nhiên hóa đặc trưng.

## Thêm mục 5.14: So sánh theo cặp trên mười lần chia gốc

Với mỗi seed s, tính Δ_s = Accuracy_Bagging,s − Accuracy_đối_chiếu,s. Việc lấy
chênh lệch trong cùng seed giúp giữ chung điều kiện train/test khi so sánh.

| Đối chiếu | Bagging cao hơn | Bằng nhau | Thấp hơn | Chênh lệch accuracy trung bình |
|---|---:|---:|---:|---:|
|Bagging−cây đơn|9|1|0|+1,96 điểm phần trăm|
|Bagging−RF|2|4|4|−0,28 điểm phần trăm|

Bagging cao hơn cây đơn ở 9 trong 10 lần chia và không thấp hơn ở lần nào trong
khảo sát. Kết quả cung cấp thông tin về mức nhất quán của cải thiện, bổ sung
cho bảng trung bình. So với RF, Bagging chưa thể hiện ưu thế nhất quán.
Các test có thể giao nhau nên không coi đây là 10 phép thử độc lập hoặc suy
ra giá trị p từ số lần thắng. Kết luận vẫn giới hạn trong dữ liệu đã khảo sát.

## Bổ sung thảo luận về chi phí và giới hạn

Nếu T_tree là chi phí học một cây, triển khai huấn luyện tuần tự có chi phí
xấp xỉ B×T_tree. Với K quan sát, độ sâu tối đa d, chi phí duyệt cây khi dự đoán
có bậc O(KBd). Ma trận phiếu có kích thước K×C và mã còn lưu B×N chỉ số bootstrap.
Đây là phân tích cấu trúc thuật toán, không phải kết quả đo thời gian thực.
Khảo sát số cây cho thấy cần cân nhắc lợi ích tăng thêm với số mô hình phải
huấn luyện và lưu trữ, thay vì giả định số cây càng lớn càng tốt.

Các phân tích bổ sung đều được thực hiện sau thí nghiệm gốc. Không viết
thành nghiên cứu xác nhận được thiết kế trước khi thấy dữ liệu. Độ sâu vẫn
chọn bằng cây đơn rồi dùng chung; chưa tối ưu riêng mỗi biến thể. Khảo sát
chỉ sử dụng train của seed 42; SD các fold không là khoảng tin cậy và chưa có
đánh giá trên dữ liệu ngoài. Không diễn giải mức bất đồng thành xác suất
bệnh hoặc bằng chứng xác định nguyên nhân y khoa.

## Ghi chú cập nhật ở giai đoạn đối chứng ban đầu

Các ghi chú sau mô tả giai đoạn bổ sung đối chứng 2 × 2. Bản báo cáo hoàn thiện
hiện đã tích hợp nội dung này và phần mở rộng AdaBoost/Voting/Stacking; bộ mã
hiện có 32 kiểm thử. Nội dung mở rộng mới nằm trong
`Mo_rong_Boosting_Voting_Stacking.md`.

- Giữ nguyên các kết quả test và số cây của thí nghiệm gốc.
- Bổ sung thuật toán/mã đối chứng từ `experiments/controlled_comparison.py`.
- Đối chứng ban đầu nâng bộ kiểm thử lên 26/26, gồm hai kiểm thử về hard/soft voting,
  ánh xạ cột xác suất khi cây chỉ học một lớp và phép đo mức bất đồng.
- Các lỗi bìa, thụt lề code trong Word, caption và mục lục của bản đã gửi vẫn
  cần sửa; bổ sung học thuật không thay thế việc hoàn thiện hình thức.
- Tái lập bằng `.venv/bin/python experiments/controlled_comparison.py`.
