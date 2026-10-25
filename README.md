# Đề 5 — Ensemble Learning

**Nhóm:** Nguyễn Nghĩa Hiếu — 52400013; Trần Quốc Bảo — 52400102.

**Giảng viên:** TS. Trần Lương Quốc Đại.

**Học phần:** Nhập môn Học máy. `(3 + 2) mod 8 = 5`.

Mã minh họa tiểu luận **phần dư 5 (mod 8)**: tự triển khai bootstrap,
hard voting và out-of-bag (OOB) cho Bagging cây quyết định. So sánh với
cây đơn và Random Forest; đánh giá trên 10 lần chia dữ liệu có phân tầng.
Cây cơ sở và Random Forest do scikit-learn cung cấp.

Đọc báo cáo tại `report/Bao_cao_De_5_Ensemble_Learning.pdf` hoặc bản Word
cùng tên. Hướng dẫn demo, phân chia phần nói và đóng gói:
[`HUONG_DAN_NOP_BAI.md`](HUONG_DAN_NOP_BAI.md).

## Chạy trên Windows (PowerShell)

Cần Python **3.11 trở lên**; phiên bản đã kiểm tra trong môi trường này là
3.12. Từ thư mục kho mã:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe de_5_ensemble_learning.py
```

Dùng trực tiếp Python trong venv nên không cần bật quyền chạy Activate.ps1.
Nếu đã cài đúng dependencies vào Python đang dùng, có thể chạy như trước:

```powershell
py de_5_ensemble_learning.py
```

## Chạy trên Linux / macOS

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python de_5_ensemble_learning.py
```

Trong cloud có thư mục home chỉ đọc, đặt cache trước khi chạy:

```bash
export MPLCONFIGDIR=/tmp/hocmaygk-matplotlib
export XDG_CACHE_HOME=/tmp/hocmaygk-cache
```

Dữ liệu có sẵn trong scikit-learn, không cần khóa API hoặc tải dataset riêng.

## Chế độ chạy

Lệnh mặc định chạy **10 seed liên tiếp, 42–51**. Seed đầu là lần tham chiếu,
giữ kết quả tương thích với demo ban đầu. Có thể chạy nhanh một lần:

```powershell
py de_5_ensemble_learning.py --repeats 1 --output-dir outputs/quick
```

Ví dụ cấu hình đầy đủ:

```powershell
py de_5_ensemble_learning.py --seed 42 --repeats 10 --n-estimators 51 --output-dir outputs
```

| Tham số | Mặc định | Ý nghĩa |
|---|---|---|
| `--seed` | 42 | Seed đầu tiên, cũng là seed tham chiếu |
| `--repeats` | 10 | Tổng số seed, bao gồm seed tham chiếu; phải ≥ 1 |
| `--n-estimators` | 51 | Số cây của mỗi ensemble; phải ≥ 1 |
| `--output-dir` | outputs | Thư mục lưu kết quả, tính từ thư mục chạy lệnh |

Chạy lại vào cùng thư mục sẽ thay thế các kết quả cùng tên. Dùng thư mục
khác khi so sánh cấu hình; không chọn cấu hình hoặc seed theo điểm test.

## Các tệp kết quả

| Tệp trong `outputs/` | Nội dung |
|---|---|
| `metrics.csv` | Chỉ số ba mô hình của **seed tham chiếu** |
| `repeated_metrics.csv` | Điểm từng mô hình, từng seed và depth đã chọn |
| `summary_metrics.csv` | Mean và SD mẫu trên tất cả seed |
| `results.json` | Cấu hình, phiên bản, CV, OOB, trace và toàn bộ kết quả |
| `report.md` | Báo cáo thực nghiệm tự sinh, dễ đọc và đưa vào bài viết |
| `classification_report.json` | Precision/recall/F1 của cả hai lớp, seed tham chiếu |
| `predictions.csv` | Nhãn thật, dự đoán từng mô hình, số phiếu từng mẫu test |
| `confusion_matrices.png` | Ma trận nhầm lẫn seed tham chiếu |
| `voting_example.png` | Mẫu bất đồng đầu tiên, ghi rõ nhãn thật và dự đoán |
| `stability.png` | Trung bình và SD của accuracy/recall qua các seed |

CSV dùng UTF-8 có BOM để Excel trên Windows nhận tiếng Việt. JSON tuân thủ
chuẩn: giá trị không xác định dùng `null`, không xuất `NaN`.
Khi `--repeats 1`, SD không xác định, không ghi bằng 0. Khi không có mẫu
bất đồng, chương trình báo rõ và không tạo ví dụ dự đoán giả.

## 1. Nguyên lý và các hướng Ensemble Learning

- **Bagging:** huấn luyện độc lập trên các mẫu bootstrap rồi tổng hợp.
- **Boosting:** huấn luyện tuần tự để tập trung vào sai sót hoặc giảm loss.
- **Voting:** kết hợp nhãn (hard) hoặc xác suất (soft) của nhiều mô hình.
- **Stacking:** học mô hình tầng hai bằng dự đoán ngoài fold của tầng cơ sở.

Phần triển khai tập trung vào Bagging, không nhận Boosting/Stacking là các
mô hình đã được đo thực nghiệm trong kho này.

Với N mẫu train, từng cây lấy N chỉ số ngẫu nhiên **có hoàn lại**. Dự đoán:

`H(x) = argmax_c Σ_b I[h_b(x) = c]`.

Bootstrap tạo đa dạng, hard voting giảm tác động của lỗi riêng khi các cây
không quá tương quan. Với trung bình dự đoán số, nếu các mô hình cùng
phương sai σ² và cùng tương quan cặp ρ, phương sai trung bình là
`σ²[ρ + (1−ρ)/B]`. Đây là trực giác cho trung bình số, không trực tiếp là
công thức lỗi phân lớp; ensemble không luôn tốt hơn cây đơn.

### Ví dụ tính tay

Ví dụ nhỏ xuyên suốt dùng `x = [1, 2, 3, 4, 5]` và nhãn
`[lành, lành, ác, ác, ác]`. Ba cây độ sâu 1 học từ các bootstrap cố định:

| Cây | Chỉ số bootstrap | Ngưỡng học được | Dự đoán tại x = 2,8 |
|---|---|---:|---|
| h₁ | `[0, 0, 2, 4, 1]` | 2,5 | Ác |
| h₂ | `[0, 0, 1, 3, 4]` | 3,0 | Lành |
| h₃ | `[4, 2, 4, 1, 3]` | 2,5 | Ác |

Mỗi cây dự đoán lành nếu `x ≤ ngưỡng`, ác nếu lớn hơn. Kết quả **2:1 → ác**
được tính từ chính ba cây đã học, không ghép các phiếu giả định rời nhau.
Đây là dữ liệu tổng hợp để giải thích cơ chế; x = 2,8 không có nhãn thật,
không phải mẫu bệnh nhân và không dùng để tính accuracy thí nghiệm thực.

```bash
.venv/bin/python examples/toy_bagging.py --output-dir outputs/toy
```

Mở `outputs/toy/toy_example.md` để xem toàn bộ phép tính Gini, ngưỡng,
phiếu và OOB. Ba bootstrap được chọn trước cho dễ tính tay; chương trình
thí nghiệm chính vẫn lấy mẫu ngẫu nhiên có hoàn lại bằng seed.

### Out-of-bag

Một quan sát không xuất hiện trong bootstrap của cây có thể được cây đó
dự đoán OOB. Xác suất không được chọn là `(1−1/N)^N`, gần 36,8% khi N lớn.
Mỗi mẫu chỉ nhận phiếu OOB từ các cây **chưa học mẫu đó**.

Mô hình lưu `oob_counts_`, `oob_vote_counts_`, `oob_decision_function_`,
`oob_score_` và `oob_coverage_`. Mẫu chưa có phiếu có hàng `NaN` trong
`oob_decision_function_` và bị loại khỏi tính accuracy OOB, không bị xem
là một dự đoán lớp 0. Hãy đọc cả coverage, nhất là khi số cây nhỏ.
Depth đã chọn trên train, nên OOB sau bước chọn này không phải kiểm định
độc lập hoàn toàn; test giữ riêng vẫn là đánh giá bên ngoài của từng lần chạy.

## 2. Thiết kế thí nghiệm

1. Với mỗi seed, chia 75% train và 25% test, giữ tỷ lệ lớp bằng `stratify`.
2. Chọn depth trong `[2, 3, 4, 5, 6]` bằng CV phân tầng 5 fold **chỉ trên
   train**, theo balanced accuracy. Nếu hòa, ưu tiên depth nhỏ hơn.
3. Dùng chung depth vừa chọn cho cây đơn, Bagging và Random Forest.
   Đây là thiết kế đối chiếu đơn giản, chưa tuning riêng từng ensemble.
4. Huấn luyện 51 cây cho mỗi ensemble. Bagging tự viết dùng **đa số nhãn**;
   RF của sklearn ngẫu nhiên hóa đặc trưng và dùng **trung bình xác suất lớp**.
5. Đánh giá trên test của seed đó sau khi chốt cấu hình.
6. Tổng hợp mean và **SD mẫu (`ddof=1`)** trên 10 seed.

Các test giữa những seed có thể giao nhau. SD mô tả mức dao động của kết
quả, **không phải khoảng tin cậy độc lập** hoặc bằng chứng ý nghĩa thống kê.
Không chọn seed tốt nhất để thay thế kết quả tổng hợp.

## 3. Dữ liệu và quy ước chỉ số

Breast Cancer Wisconsin Diagnostic: **569 mẫu, 30 đặc trưng số** mô tả
nhân tế bào; **212 ác tính (`0=malignant`)**, **357 lành tính (`1=benign`)**.
Đầu vào là đặc trưng đã trích xuất, không phải ảnh. Không cần chuẩn hóa
cho các cây trong bài minh họa này.

**Lớp dương là ác tính = 0.** Ma trận dùng hàng nhãn thật, cột dự đoán,
thứ tự `[ác tính, lành tính]`: `[[TP,FN],[FP,TN]]`.

- Recall ác tính = TP/(TP+FN): tỷ lệ nhận ra các ca ác tính.
- Precision ác tính = TP/(TP+FP).
- Specificity = recall lớp lành tính = TN/(TN+FP).
- F1 ác tính = 2TP/(2TP+FP+FN).
- Balanced accuracy = trung bình recall hai lớp.

Tỷ lệ phiếu cây **không phải xác suất bệnh đã hiệu chỉnh**. Đây là minh
họa học máy, chưa có xác thực lâm sàng hay đánh giá trên quần thể độc lập.

## 4. Kết quả đã chạy

Seed 42: train 426, test 143, depth 3. Các chỉ số này giữ nguyên so với mã
ban đầu và kết quả bạn đã chạy trên Windows:

| Mô hình | Accuracy | Precision ác | Recall ác | F1 ác | Bỏ sót ác |
|---|---:|---:|---:|---:|---:|
| Cây đơn | 94,41% | 94,12% | 90,57% | 92,31% | 5/53 |
| Bagging tự viết | 95,10% | 94,23% | 92,45% | 93,33% | 4/53 |
| Random Forest | 95,10% | 94,23% | 92,45% | 93,33% | 4/53 |

Mười lần chia, seed 42–51, với dependencies được ghim trong `requirements.txt`:

| Mô hình | Accuracy mean ± SD | Recall ác mean ± SD | F1 ác mean ± SD |
|---|---:|---:|---:|
| Cây đơn | 92,80 ± 1,84 | 90,38 ± 4,66 | 90,30 ± 2,42 |
| Bagging tự viết | 94,76 ± 1,59 | 92,45 ± 3,77 | 92,89 ± 2,13 |
| Random Forest | 95,03 ± 1,85 | 92,26 ± 3,26 | 93,26 ± 2,39 |

Mean tính theo %, SD theo điểm phần trăm. Bagging có accuracy trung bình
cao hơn cây đơn trong các lần chia này; không suy ra luôn tốt hơn trên mọi
dữ liệu. RF và Bagging cùng điểm seed 42 nhưng khác kết quả tổng hợp.

Bagging seed 42 có **OOB accuracy 401/426 = 94,13%**, coverage **100%**;
mỗi mẫu có từ 8 đến 34 cây OOB. Ví dụ bất đồng đầu tiên là vị trí test 2,
hàng dataset 291 (đếm từ 0): **27 phiếu ác / 24 phiếu lành**, nhãn thật là
lành, nên dự đoán **sai**. Mẫu này được chọn theo thứ tự, không lựa dự đoán
đúng để trình bày. Mẫu test đầu tiên vẫn có 51 phiếu lành và dự đoán đúng.

## 5. Đọc và kiểm thử code

- `ensemble_model.py`: `ManualBagging`, validation đầu vào, bootstrap,
  hard voting và OOB. Hỗ trợ nhãn chuỗi, nhãn số không liên tiếp và đa lớp.
- `de_5_ensemble_learning.py`: dữ liệu, train-only CV, so sánh mô hình,
  lặp seed, biểu đồ và xuất báo cáo cho bài toán nhị phân cụ thể.
- `tests/`: kiểm tra phiếu/OOB, nhãn, tái lập, tránh dùng test để chọn depth,
  hồi quy seed 42 và chạy CLI với số cây khác mặc định.
- `examples/toy_bagging.py`: ví dụ nhỏ cùng một luồng từ bootstrap đến voting;
  có kiểm thử riêng cho ngưỡng, phiếu và các mẫu OOB.

`ManualBagging` hỗ trợ `get_params`, `set_params`, `clone` và cross-validation
của sklearn. `votes(X)` trả số phiếu; `predict_vote_fraction(X)` trả tỷ lệ
phiếu; `predict(X)` chọn lớp thắng. Nếu hòa, chọn lớp đầu theo `classes_`.
51 cây tránh hòa ở bài toán **hai lớp**, không bảo đảm cho đa lớp.

Chạy kiểm thử bằng cùng Python đã cài dependencies:

```powershell
py -m unittest discover -s tests -v
```

Không cần cài thêm pytest. Bộ kiểm thử gồm cả workflow thực và ví dụ tính tay,
không chỉ cú pháp.

## Slide và tài liệu nộp

| Tài liệu | Vị trí |
|---|---|
| Báo cáo Word và PDF | `report/Bao_cao_De_5_Ensemble_Learning.docx` / `.pdf` |
| Nguồn nội dung báo cáo | `report/Bao_cao_De_5_Ensemble_Learning.md` |
| Slide PowerPoint và PDF | `De_5_Ensemble_Learning.pptx` / `.pdf` |
| Lời thuyết trình | `presentation/loi_thuyet_trinh.md` |
| Demo, hỏi đáp và quy trình nộp | `HUONG_DAN_NOP_BAI.md` |
| Thông tin nhóm dùng chung | `report/group_info.json` |

Bộ **26 slide** có đồ họa/chữ chỉnh sửa được và lời thuyết trình trong Notes.
`outputs/report.md` chỉ là phần thực nghiệm tự sinh; báo cáo hoàn chỉnh ở
`report/`. PDF gốc của repo là bản slide, khác với PDF báo cáo.

Để tạo lại toàn bộ tài liệu và gói nộp (cần LibreOffice để xuất PDF,
Poppler/`pdftotext` để cập nhật mục lục):

```bash
.venv/bin/python -m pip install -r requirements.txt -r presentation/requirements.txt -r report/requirements.txt
.venv/bin/python tools/prepare_submission.py
```

Lệnh kiểm thử và chạy lại thí nghiệm trước khi tạo tài liệu; file nén cuối tại
`submission/52400013_52400102.zip` có cả kết quả trong `outputs/` dù thư mục
này bị Git bỏ qua. `.venv/`, `.git/` và cache không được đóng gói.
Các tệp Word/slide sinh tự động sẽ được tạo lại; lưu riêng nếu đã sửa thủ công.
Xem `presentation/README.md` và `report/README.md` để tạo riêng từng tài liệu.

## Tài liệu tham khảo

- Breiman (1996), *Bagging Predictors*, Machine Learning 24, 123–140.
  https://doi.org/10.1007/BF00058655
- Breiman (2001), *Random Forests*, Machine Learning 45, 5–32.
  https://doi.org/10.1023/A:1010933404324
- Ensemble methods: https://scikit-learn.org/stable/modules/ensemble.html
- Dataset và nguồn gốc:
  https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html
