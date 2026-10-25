# Đề 5 — Ensemble Learning

Mã minh họa tiểu luận **phần dư 5 (mod 8)**: tự triển khai bootstrap,
hard voting và out-of-bag (OOB) cho Bagging cây quyết định. So sánh với
cây đơn và Random Forest; đánh giá trên 10 lần chia dữ liệu có phân tầng.
Cây cơ sở và Random Forest do scikit-learn cung cấp.

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

Tập chỉ số `[0, 1, 2, 3, 4]` có thể tạo ba bootstrap:
`[0, 0, 2, 4, 1]`, `[1, 3, 3, 2, 0]`, `[4, 2, 4, 1, 3]`.
Chỉ số có thể lặp; một số mẫu không xuất hiện trong một cây.
Nếu ba phiếu giả định là `[ác, lành, ác]`, tổ hợp chọn ác với 2/3 phiếu.
Đây là ví dụ cơ chế, không khẳng định là đầu ra của các cây cụ thể.

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

`ManualBagging` hỗ trợ `get_params`, `set_params`, `clone` và cross-validation
của sklearn. `votes(X)` trả số phiếu; `predict_vote_fraction(X)` trả tỷ lệ
phiếu; `predict(X)` chọn lớp thắng. Nếu hòa, chọn lớp đầu theo `classes_`.
51 cây tránh hòa ở bài toán **hai lớp**, không bảo đảm cho đa lớp.

Chạy kiểm thử bằng cùng Python đã cài dependencies:

```powershell
py -m unittest discover -s tests -v
```

Không cần cài thêm pytest. Bộ kiểm thử gồm cả workflow thực, không chỉ cú pháp.

## Slide và tài liệu nộp

Bộ **26 slide** trong `De_5_Ensemble_Learning.pptx` và PDF cùng tên được
cập nhật theo phiên bản mã này. Đồ họa/chữ chỉnh sửa được; phần Notes chứa
lời thuyết trình. Bản văn bản: `presentation/loi_thuyet_trinh.md`.
Xem `presentation/README.md` để tạo lại slide. Điền tên thành viên và lớp.

`outputs/report.md` là báo cáo thực nghiệm tự sinh, **chưa phải báo cáo
Word/PDF hoàn chỉnh theo đề**. PDF ở thư mục gốc là bản xuất slide.

## Tài liệu tham khảo

- Breiman (1996), *Bagging Predictors*, Machine Learning 24, 123–140.
  https://doi.org/10.1007/BF00058655
- Breiman (2001), *Random Forests*, Machine Learning 45, 5–32.
  https://doi.org/10.1023/A:1010933404324
- Ensemble methods: https://scikit-learn.org/stable/modules/ensemble.html
- Dataset và nguồn gốc:
  https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html
