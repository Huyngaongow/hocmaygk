# Bổ sung AdaBoost, Voting và Stacking

Các mục dưới đây đã được tích hợp vào báo cáo Word/PDF. Bagging vẫn là trọng tâm triển khai.

## 2.9 AdaBoost

AdaBoost xây dựng tuần tự các mô hình cơ sở. Mỗi vòng học sử dụng trọng số của các quan sát; mẫu bị dự đoán sai được tăng trọng số tương đối để vòng sau chú ý hơn. Phần minh họa sử dụng cây độ sâu 1 (decision stump), tối đa 51 vòng và learning_rate = 1 [3], [6].

Quy trình SAMME trong bài toán hai lớp: (1) khởi tạo wᵢ = 1/N; (2) học cây hₜ với trọng số wᵢ; (3) tính tổng trọng số các mẫu sai εₜ; (4) tính trọng số phiếu αₜ; (5) tăng trọng số mẫu sai và chuẩn hóa; (6) lặp lại rồi tổng hợp phiếu có trọng số. Với 0 < εₜ < 0,5, các công thức cho bước cập nhật là:

εₜ = ∑ᵢ wᵢ I[hₜ(xᵢ) ≠ yᵢ];    αₜ = ln((1 − εₜ)/εₜ).

wᵢ mới ∝ wᵢ × exp(αₜ I[hₜ(xᵢ) ≠ yᵢ]).

H(x) = argmax_c ∑ₜ αₜ I[hₜ(x) = c].

Đây là quy ước SAMME của AdaBoostClassifier trong scikit-learn 1.8 cho hai lớp, không dùng trực tiếp hệ số ½ của một cách viết AdaBoost nhị phân khác. Cây hoàn hảo có thể làm thuật toán dừng sớm; vì vậy 51 là số vòng tối đa, không luôn là số cây thực học.

Ví dụ: năm mẫu có trọng số bằng nhau 0,2; cây đầu dự đoán sai một mẫu nên ε = 0,2 và α = ln 4 ≈ 1,386. Mẫu sai nhân 4 thành 0,8; bốn mẫu đúng giữ 0,2 mỗi mẫu. Tổng trọng số chưa chuẩn hóa là 1,6. Sau chuẩn hóa, mẫu sai nhận 0,5; mỗi mẫu đúng nhận 0,125. Vòng kế tiếp tập trung hơn vào mẫu sai, không có nghĩa accuracy đã tăng lên 50%.

## 2.10 Voting

Voting trong phần mở rộng kết hợp ba mô hình khác loại: cây quyết định độ sâu 3, Logistic Regression và Gaussian Naive Bayes. Cây chia không gian bằng điều kiện; Logistic Regression học ranh giới tuyến tính; Gaussian NB mô hình hóa phân bố đặc trưng theo lớp. Sự khác nhau về giả thiết học có thể tạo ra các dự đoán bổ sung cho nhau, nhưng không bảo đảm tổ hợp luôn tốt hơn từng mô hình.

Quy trình: học riêng ba mô hình trên train; lấy nhãn cho hard voting hoặc xác suất lớp cho soft voting; tổng hợp với trọng số bằng nhau; đánh giá trên test. Công thức ở mục 2.5 vẫn áp dụng. Hard và soft sử dụng cùng cấu hình mô hình cơ sở để việc đối chiếu không thay đổi đồng thời cả kiến trúc. Soft voting có thể bị ảnh hưởng bởi chất lượng xác suất của từng mô hình; bài chưa hiệu chuẩn xác suất [3].

## 2.11 Stacking

Stacking học một mô hình tầng hai để kết hợp đầu ra của các mô hình cơ sở [7]. Ba mô hình cơ sở giống phần Voting; mô hình tầng hai là Logistic Regression. Khác với Voting dùng quy tắc cố định, Stacking học cách kết hợp từ dữ liệu.

Quy trình trên train: (1) chia thành năm fold phân tầng; (2) trong từng fold, học các mô hình cơ sở trên bốn fold còn lại và dự đoán xác suất cho fold được giữ; (3) ghép các dự đoán ngoài fold (OOF) thành đầu vào tầng hai; (4) học tầng hai trên các đầu ra OOF và nhãn train; (5) học lại các mô hình cơ sở trên toàn train. Khi gặp test, ba mô hình cơ sở tạo đầu vào cho tầng hai dự đoán nhãn cuối.

Trong scikit-learn, với hai lớp và stack_method='predict_proba', một cột xác suất dư thừa được bỏ ở mỗi mô hình cơ sở. Ba cột còn lại tương ứng xác suất lớp 1 (lành tính), không phải mặc định là xác suất ác tính. StandardScaler nằm trong Pipeline của Logistic Regression nên mỗi lần fit chỉ học thống kê từ phần dữ liệu được phép học. Không dùng dự đoán in-sample để thay thế OOF; tập test không tham gia học tầng hai [3], [7].

## 4.10 Thiết kế thực nghiệm

Phần mở rộng dùng đúng mười lần chia phân tầng 75/25, seed 42–51 như thí nghiệm gốc. Trong mỗi seed, mọi mô hình dùng chung 426 quan sát train và 143 quan sát test. Ba kết quả gốc được giữ để đối chiếu; bảy cấu hình mới được khai báo trước lần chạy bổ sung và không được điều chỉnh theo điểm test.

Bộ cơ sở của Voting/Stacking gồm cây độ sâu 3 cố định, Logistic Regression có StandardScaler trong Pipeline và Gaussian NB. Ba mô hình này được đánh giá riêng để kiểm tra lợi ích của tổ hợp. Cây độ sâu 3 được ghi thành một dòng riêng, vì khác quy trình chọn độ sâu bằng CV của cây đơn trong thí nghiệm gốc. Cố định kiến trúc trước khi tạo OOF giúp không dùng fold được giữ để lựa chọn cấu hình cây.

| Nhóm | Cấu hình cố định |
|---|---|
| AdaBoost | Tối đa 51 cây độ sâu 1; learning_rate = 1; SAMME |
| Voting hard/soft | Cây độ sâu 3 + Logistic Regression chuẩn hóa + Gaussian NB; trọng số bằng nhau |
| Stacking | Cùng ba mô hình; OOF 5 fold phân tầng có trộn; predict_proba; tầng hai Logistic Regression; passthrough=False |
| Đối chứng cơ sở | Đánh giá riêng cây độ sâu 3, Logistic Regression và Gaussian NB |

Đây là khảo sát bổ sung sau khi đã xem kết quả thí nghiệm gốc, nên được diễn giải như đối chiếu mô tả, không phải xác nhận độc lập trên dữ liệu mới. Các mô hình chưa được tối ưu riêng với cùng ngân sách; bảng kết quả so sánh các cấu hình đã công bố, không tách riêng tác động nhân quả của tên phương pháp. Trung bình và SD mẫu dùng cùng quy ước với mục 4.7.

## 5.16 Code và kết quả

Tệp experiments/ensemble_families.py dựng các cấu hình bằng scikit-learn, lưu chỉ số của từng seed và tổng hợp kết quả. Đoạn mã sau minh họa cách gọi các mô hình từ hàm build_models; đầy đủ cấu hình và cách tạo OOF nằm trong mã nguồn đi kèm.

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from experiments.ensemble_families import build_models

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.25,
    stratify=data.target, random_state=42,
)
models = build_models(seed=42)
for name in ("AdaBoost", "Voting (hard)",
             "Voting (soft)", "Stacking"):
    model = models[name]
    model.fit(X_train, y_train)
    prediction = model.predict(X_test)
    print(name, (prediction == y_test).mean())
```

| Mô hình | Accuracy | Balanced accuracy | Recall ác |
|---|---:|---:|---:|
| Cây đơn (độ sâu CV) | 92,80 ± 1,84 | 92,30 ± 1,94 | 90,38 ± 4,66 |
| Manual Bagging | 94,76 ± 1,59 | 94,28 ± 1,75 | 92,45 ± 3,77 |
| Random Forest | 95,03 ± 1,85 | 94,47 ± 1,80 | 92,26 ± 3,26 |
| Cây đơn (độ sâu 3) | 92,94 ± 2,15 | 92,37 ± 2,41 | 90,19 ± 4,86 |
| Logistic Regression | 97,62 ± 0,82 | 97,41 ± 0,99 | 96,60 ± 2,32 |
| Gaussian NB | 94,20 ± 1,40 | 93,37 ± 1,81 | 90,19 ± 4,15 |
| AdaBoost | 96,43 ± 1,07 | 95,96 ± 1,13 | 94,15 ± 2,08 |
| Voting hard | 95,80 ± 1,23 | 95,15 ± 1,58 | 92,64 ± 3,72 |
| Voting soft | 95,66 ± 1,27 | 95,04 ± 1,63 | 92,64 ± 3,72 |
| Stacking | 96,64 ± 1,22 | 96,32 ± 1,28 | 95,09 ± 2,70 |

Trung bình tính theo %, SD mẫu theo điểm phần trăm, ddof=1; mười seed42–51.

Trong toàn bộ cấu hình khảo sát, Logistic Regression đạt accuracy trung bình cao nhất (97,62%). Kết quả này cho thấy các ensemble được xét chưa vượt qua mô hình đơn mạnh nhất. Đây là thứ hạng mô tả của lần khảo sát, chưa phải bằng chứng phương pháp đó luôn tốt nhất.

Voting hard đạt accuracy trung bình 95,80%, Voting soft đạt 95,66%, Stacking đạt 96,64% và AdaBoost đạt 96,43%. Cần đọc cùng recall ác tính và mức dao động; kết hợp thêm mô hình hoặc học thêm tầng hai không tự động bảo đảm cải thiện so với mô hình cơ sở mạnh.

Bagging học các mô hình trên bootstrap; AdaBoost cập nhật trọng số qua các vòng; Voting áp dụng quy tắc kết hợp cố định; Stacking học tầng kết hợp từ OOF. Các cấu hình sử dụng loại mô hình và chi phí khác nhau, vì vậy bảng minh họa hành vi của các hướng tiếp cận thay vì chứng minh một cơ chế tổ hợp vượt trội trong mọi điều kiện.

Các holdout có thể giao nhau; SD chỉ mô tả dao động. Khảo sát này chưa hiệu chuẩn xác suất, kiểm định thống kê hay đánh giá trên dữ liệu ngoài độc lập.
