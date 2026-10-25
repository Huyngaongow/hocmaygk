# Hướng dẫn demo, thuyết trình và nộp bài — Chủ đề 5

**Nhóm:** Nguyễn Nghĩa Hiếu — 52400013; Trần Quốc Bảo — 52400102.

**Giảng viên:** TS. Trần Lương Quốc Đại.

**Học phần:** Nhập môn Học máy.

**Xác định đề tài:** (3 + 2) mod 8 = 5 → Ensemble Learning.

## 1. Các tệp cần dùng

| Tệp | Mục đích |
|---|---|
| `report/Bao_cao_De_5_Ensemble_Learning.docx` | Báo cáo Word, có thể chỉnh sửa |
| `report/Bao_cao_De_5_Ensemble_Learning.pdf` | Báo cáo PDF để đọc/nộp |
| `De_5_Ensemble_Learning.pptx` | Slide có ghi chú lời thuyết trình |
| `De_5_Ensemble_Learning.pdf` | Bản PDF của slide, không thay thế báo cáo |
| `ensemble_model.py`, `de_5_ensemble_learning.py` | Thuật toán và thí nghiệm chính |
| `examples/toy_bagging.py` | Ví dụ tính tay được kiểm chứng bằng code |
| `outputs/` | Bảng số liệu, biểu đồ và dấu vết dự đoán thực |
| `presentation/loi_thuyet_trinh.md` | Lời dẫn để luyện tập, không cần đọc nguyên văn |
| `submission/52400013_52400102.zip` | Gói nộp gồm báo cáo, code, slide và kết quả |

Nếu chỉnh thông tin nhóm, sửa `report/group_info.json` rồi dựng lại tài liệu.
Không tự điền tên trường, mã lớp hoặc đóng góp cá nhân chưa được xác nhận.

## 2. Bài nói tập trung vào điều gì?

Thông điệp chính: **Bagging tạo nhiều cây từ những mẫu có hoàn lại, sau đó đếm phiếu để dự đoán.**
Mục tiêu là giải thích được từng bước, không ghi nhớ nhiều công thức.

Mạch trình bày:

1. Một cây dễ thay đổi khi dữ liệu thay đổi; nhiều cây cần có sự đa dạng.
2. Cho xem dữ liệu nhỏ, ba bootstrap và ba ngưỡng được học.
3. Cho cùng x = 2,8 đi qua ba cây: ác, lành, ác → kết quả ác theo 2:1.
4. Chỉ vào đoạn code lấy mẫu và đếm phiếu để nối lý thuyết với triển khai.
5. Giới thiệu dữ liệu thật, giữ test riêng và đọc bảng kết quả.
6. Giải thích một lỗi cụ thể, rồi kết luận trong phạm vi đã kiểm tra.

Boosting và Stacking chỉ cần giải thích ý tưởng và điểm khác với Bagging.
Công thức phương sai là phần bổ sung; không cần chứng minh khi trình bày chính.

## 3. Gợi ý chia phần cho hai thành viên

Đây là **phương án luyện tập**, không phải xác nhận phân công đã thực hiện.
Hai bạn có thể đổi phần theo sở trường, nhưng cả hai cần hiểu toàn bộ thuật toán.

| Người trình bày | Phần chính | Câu chuyển |
|---|---|---|
| Nguyễn Nghĩa Hiếu | Slide 1–11: ý tưởng, các họ Ensemble và ví dụ tính từng bước | “Từ ví dụ nhỏ, phần tiếp theo áp dụng đúng cơ chế này vào bộ dữ liệu thực.” |
| Trần Quốc Bảo | Slide 12–24: bài toán, code, thực nghiệm, phân tích lỗi và kết luận | “Kết quả cho thấy lợi ích trong thí nghiệm này; nhóm vẫn giữ rõ các giới hạn.” |
| Cả hai | Slide 25–26: hỏi đáp/phép tính chỉ số | Người nắm phần được hỏi trả lời trước, người còn lại bổ sung nếu cần. |

Luyện theo thời lượng giảng viên thông báo. Nếu chưa có quy định riêng, có thể
tập bản 15–20 phút và một bản rút gọn. Khi cần rút thời gian, nói ngắn slide 4,
10–11 và để slide 25–26 cho hỏi đáp; giữ nguyên ví dụ, code và kết quả.
15–20 phút là gợi ý luyện tập, không phải thời lượng bắt buộc trong PDF đề bài.

## 4. Demo ngắn, ít rủi ro

Chạy từ thư mục gốc repo, sau khi đã cài dependencies theo README:

```bash
export MPLCONFIGDIR=/tmp/hocmaygk-matplotlib
export XDG_CACHE_HOME=/tmp/hocmaygk-cache
.venv/bin/python examples/toy_bagging.py --output-dir outputs/toy
.venv/bin/python de_5_ensemble_learning.py --repeats 1 --output-dir outputs/quick
```

Trên Windows, dùng `.venv\Scripts\python.exe` thay `.venv/bin/python`;
hai lệnh `export` chỉ dành cho Linux/macOS và không cần trên Windows thông thường.

Khi demo, mở `outputs/toy/toy_example.md`, sau đó `outputs/quick/report.md`
và `outputs/quick/voting_example.png`. Chỉ cần chỉ ra ba ngưỡng, phiếu 2:1,
accuracy/recall và ví dụ bất đồng. Không cần duyệt mọi tệp JSON trên màn hình.

**Kết quả 10 seed trong báo cáo** nằm tại `outputs/`, không được thay bằng kết quả
của demo một seed. Demo nhanh có SD không xác định; đó không phải SD bằng 0.
Có sẵn PDF và PNG để trình bày nếu máy chiếu hoặc terminal gặp vấn đề.

## 5. Các câu cần trả lời được

- **Tại sao phải bootstrap?** Cùng số lượt lấy mẫu nhưng thành phần và số lần xuất hiện khác nhau, giúp các cây đa dạng.
- **Tại sao vẫn dùng sklearn?** Cây cơ sở và Random Forest dùng thư viện; lấy mẫu bootstrap, hard voting và OOB được tự triển khai.
- **Có phải làm đủ mọi loại Ensemble?** Đề không bắt cài tất cả. Nhóm giới thiệu các hướng phổ biến và triển khai sâu Bagging.
- **Vì sao 51 cây?** Đây là cấu hình minh họa cố định và tránh hòa trong bài toán hai lớp; chưa tối ưu số cây.
- **Vì sao không chuẩn hóa?** Cây chia theo ngưỡng của từng đặc trưng, không dùng khoảng cách giữa các quan sát.
- **Có rò rỉ test không?** Trong code, chọn depth bằng CV trên train; test chỉ dùng sau khi chốt cấu hình.
- **OOB khác test thế nào?** OOB dùng các cây không lấy mẫu train đó; test là dữ liệu giữ riêng. OOB sau chọn depth không hoàn toàn độc lập với tuning.
- **Tại sao Random Forest và Bagging cùng điểm?** Cùng số đếm ở seed 42 không làm hai mô hình thành một; các kết quả tổng hợp 10 seed có khác nhau.
- **27/51 có phải xác suất ung thư?** Không. Đây là tỷ lệ phiếu cây chưa hiệu chỉnh, không phải xác suất bệnh.
- **Bagging có luôn tốt hơn không?** Không; kết quả chỉ cho thấy cải thiện trong thí nghiệm đã chạy. Các cây mắc lỗi giống nhau thì lợi ích có thể thấp.
- **Vì sao quan tâm recall?** Nó phản ánh tỷ lệ ca ác tính được nhận ra. Cần xem thêm precision và số dương tính giả, không chỉ tối đa một chỉ số.
- **Có dùng để chẩn đoán được không?** Bài minh họa chưa có xác thực lâm sàng và vẫn có lỗi; không phải công cụ chẩn đoán.

## 6. Dựng lại và đóng gói

Sau khi cài thêm dependencies tạo tài liệu, LibreOffice và Poppler (`pdftotext`):

```bash
.venv/bin/python -m pip install -r requirements.txt -r presentation/requirements.txt -r report/requirements.txt
.venv/bin/python tools/prepare_submission.py
```

Lệnh thứ hai kiểm thử, chạy lại 10 seed và ví dụ nhỏ, tạo Word/slide, xuất hai PDF,
cập nhật mục lục theo số trang thực rồi đóng gói theo MSSV. Nó tạo lại các tài liệu sinh tự động; lưu bản sao trước
nếu đã sửa thủ công Word hoặc PowerPoint. Trình đóng gói bao gồm `outputs/`
dù Git bỏ qua thư mục này, và không kèm `.venv`, `.git` hay cache.

## 7. Kiểm tra lần cuối trước khi nộp

- [ ] Tên và MSSV hai thành viên, tên giảng viên đúng trên Word và slide.
- [ ] Đọc Word/PDF để bảo đảm không còn ghi chú cần điền hoặc sai dấu tiếng Việt.
- [ ] Có đủ Word, PDF báo cáo, Python và slide trong file nén theo MSSV.
- [ ] Đối chiếu quy định trình bày riêng của khoa/lớp nếu giảng viên đã cung cấp.
- [ ] Mỗi thành viên đã nói thử phần mình và trả lời được các câu phía trên.
- [ ] Giải nén thử và mở báo cáo/slide trước khi tải lên eLearning.
- [ ] Nộp trong khoảng 17/10/2026 đến hết 30/10/2026 theo PDF đề bài; kiểm tra trạng thái nộp trên hệ thống.

PDF đề bài không chỉ rõ số trang báo cáo hay thời lượng thuyết trình cụ thể.
Không suy diễn các con số gợi ý trong repo thành quy định của giảng viên.
