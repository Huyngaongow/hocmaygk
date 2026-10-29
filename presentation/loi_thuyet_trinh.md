# Lời thuyết trình — Đề 5: Ensemble Learning

24 slide: 20 slide chính và 4 slide dự phòng. Gợi ý luyện tập 15–18 phút; thời lượng thực tế theo giảng viên.

Phân chia gợi ý: Nguyễn Nghĩa Hiếu slide 1–11; Trần Quốc Bảo slide 12–20; cả hai tham gia hỏi đáp. Đây là phương án luyện tập, không phải xác nhận lịch sử đóng góp.

Nguồn số liệu: outputs/results.json, outputs/extensions/analysis.json và controlled_comparison.json. Các khảo sát bổ sung chỉ dùng train seed 42.

## Slide 01 — 

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Mở đầu bằng câu hỏi: khi một cây quyết định nhạy với dữ liệu, kết hợp nhiều cây có giúp cải thiện dự đoán không? Ba câu hỏi chính là: Bagging có cải thiện so với cây đơn; tăng số cây có tiếp tục có lợi; và đa dạng hơn có đủ giúp tổ hợp tốt hơn? Báo cáo tập trung vào Bagging. Nhóm tự triển khai bootstrap, hard voting và OOB; cây cơ sở dùng scikit-learn. Sơ đồ trên bìa minh họa cơ chế kết hợp, không biểu diễn những cây đã học cụ thể. Bộ slide gồm 20 trang chính và 4 trang dự phòng cho hỏi đáp. Thời lượng luyện tập gợi ý là 15–18 phút, không phải quy định của đề bài.

## Slide 02 — Bagging trong bức tranh học tổ hợp

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Bagging tạo nhiều mẫu bootstrap để học các mô hình cơ sở. Boosting xây dựng một chuỗi mô hình nhằm xử lý sai sót hoặc giảm hàm mất mát. Voting là quy tắc kết hợp nhãn hay xác suất; Stacking học một bộ kết hợp từ dự đoán ngoài fold. Các hướng này không hoàn toàn tách rời: Bagging cũng cần quy tắc tổng hợp. Bài chỉ thực nghiệm sâu Bagging và Random Forest. Boosting, Stacking được giới thiệu tổng quan; chi tiết minh họa nằm ở slide dự phòng 23.

## Slide 03 — Bagging = Bootstrap + Aggregating

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Mỗi bootstrap có N lượt lấy có hoàn lại, nên một quan sát có thể lặp hoặc không xuất hiện. Mỗi cây học trên bootstrap riêng rồi cùng dự đoán một quan sát mới. Các cây học độc lập về quy trình, không có nghĩa dự đoán của chúng độc lập thống kê. Mã minh họa huấn luyện tuần tự. Mô hình tham chiếu có N = 426, B = 51 và max_depth = 3. Số cây lẻ tránh hòa trong bài toán hai lớp; khi có nhiều lớp vẫn có thể hòa, mã chọn lớp đầu trong classes_.

## Slide 04 — Cùng 5 quan sát, tạo 3 bootstrap khác nhau

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Ví dụ gồm x = [1, 2, 3, 4, 5] và y = [1, 1, 0, 0, 0], với nhãn 1 là lành, nhãn 0 là ác. Các chỉ số hàng bắt đầu từ 0. Ba bootstrap được chọn cố định để dễ tính tay: h₁ vắng hàng 3, h₂ vắng hàng 2 và h₃ vắng hàng 0. Đây là dữ liệu giả lập, không đại diện cho một đặc trưng y tế cụ thể. Trong thí nghiệm chính, bootstrap vẫn được sinh ngẫu nhiên có hoàn lại theo seed.

## Slide 05 — Cây h₁ chọn ngưỡng làm giảm Gini nhiều nhất

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Bootstrap của h₁ có các giá trị [1, 1, 3, 5, 2], gồm ba nhãn lành và hai nhãn ác. Gini ban đầu bằng 0,48. Các ngưỡng ứng viên là 1,5; 2,5 và 4,0, cho Gini sau chia lần lượt 0,2667; 0 và 0,30. Ngưỡng 2,5 có mức giảm lớn nhất nên được chọn. h₂ thiếu x = 3 nên học ngưỡng 3,0; h₃ có ngưỡng 2,5. Phép tính được đối chiếu với cây một mức của scikit-learn, không phải bộ học cây do nhóm tự cài từ đầu.

## Slide 06 — Mẫu x = 2,8 nhận hai phiếu ác và một phiếu lành

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Đưa cùng quan sát mới x = 2,8 qua ba cây. Với h₁ và h₃, giá trị này lớn hơn ngưỡng 2,5 nên dự đoán ác, nhãn 0. Với h₂, 2,8 nhỏ hơn hoặc bằng ngưỡng 3,0 nên dự đoán lành, nhãn 1. Tổ hợp có hai phiếu ác và một phiếu lành, vì vậy chọn nhãn 0. Đây chỉ là minh họa quy tắc đa số. Mẫu mới chưa có nhãn thật, nên chưa thể kết luận dự đoán đúng hay sai; tỷ lệ phiếu cũng chưa phải xác suất bệnh.

## Slide 07 — Hard và soft voting có thể chọn khác lớp

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Đây là ví dụ giả định để phân biệt hai quy tắc tổng hợp, khác với ví dụ tính tay trước. Hard voting chỉ đếm nhãn nên chọn ác với hai trong ba phiếu. Soft voting lấy trung bình xác suất: (0,51 + 0,51 + 0,01)/3 ≈ 0,3433 cho lớp ác, tương ứng khoảng 0,6567 cho lớp lành, nên chọn lành. Hai quy tắc có thể cho kết quả khác; soft không tự động tốt hơn hard. Phần đối chứng ở slide 17 kiểm tra chúng trên cùng các cây đã học thực tế.

## Slide 08 — OOB chỉ dùng phiếu của cây chưa học quan sát đó

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Mỗi quan sát chỉ nhận phiếu OOB từ các cây chưa lấy nó vào bootstrap. Hàng chưa có phiếu được giữ không xác định, tránh dùng argmax trên hàng toàn 0. Lần tham chiếu có coverage 100% và 401/426 dự đoán đúng. Với N = 426, xác suất vắng trong một bootstrap khoảng 36,74%. Số quan sát khác nhau kỳ vọng là 269,47, thực tế trung bình 268,04; số phiếu OOB kỳ vọng mỗi mẫu là 18,74, thực tế 18,91. Coverage khác accuracy. OOB được tính sau chọn độ sâu nên chưa độc lập hoàn toàn với tuning.

## Slide 09 — 569 mẫu: học trên train, đánh giá trên test

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Dữ liệu gồm 569 quan sát, 212 mẫu ác và 357 mẫu lành, với 30 đặc trưng số đã trích xuất từ nhân tế bào. Ác tính có nhãn 0 và được quy ước là lớp dương. Seed 42 chia có phân tầng theo tỷ lệ 75/25: train 426 gồm 159 ác, 267 lành; test 143 gồm 53 ác, 90 lành. Chỉ trên train, CV phân tầng năm fold thử độ sâu 2–6; độ sâu 3 đạt balanced accuracy CV cao nhất, 93,73%. Độ sâu được chọn bằng cây đơn rồi dùng chung cho ba mô hình; chưa tối ưu riêng từng ensemble. Test không tham gia lựa chọn. Mỗi seed 42–51 lặp lại quy trình này.

## Slide 10 — Bootstrap được triển khai trực tiếp trong Python

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Đoạn trích nằm trong phương thức fit; X ở đây chỉ chứa train. Nhãn encoded được tạo bằng np.unique(y, return_inverse=True), giúp đưa các lớp về chỉ số liên tiếp. Bộ sinh rng khởi tạo từ random_state, rồi sinh n_samples chỉ số có hoàn lại và seed cho từng cây. Mỗi cây học X và nhãn trên cùng chỉ số bootstrap. Mã đầy đủ còn lưu estimators_samples_ để truy vết và tính OOB. Cây DecisionTreeClassifier dùng thư viện; phần nhóm tự triển khai là tổ chức lấy mẫu, nhiều cây và quản lý phiếu.

## Slide 11 — Hard voting đếm phiếu rồi ánh xạ về nhãn gốc

Người nói gợi ý: Nguyễn Nghĩa Hiếu.

Các cây học nhãn mã hóa nên predict trả về chỉ số cột lớp. np.add.at cộng một phiếu vào đúng hàng và cột; argmax chọn lớp nhiều phiếu nhất, rồi self.classes_ ánh xạ về nhãn gốc. Trong mã đầy đủ, votes và predict là hai phương thức riêng; slide gộp để giải thích. Bộ mã đạt 26/26 kiểm thử, gồm hard/soft khác nhãn, cây học một lớp và phép đo bất đồng. Chuyển lời cho thành viên thứ hai: từ cơ chế đã kiểm chứng, phần tiếp theo xem các cây hoạt động ra sao trên dữ liệu thực.

## Slide 12 — Seed 42: Bagging đúng thêm 1/143 mẫu test

Người nói gợi ý: Trần Quốc Bảo.

Hàng của ma trận là nhãn thật, cột là dự đoán. Bagging có TP = 49, FN = 4, FP = 3 và TN = 87; cây đơn có TP = 48, FN = 5, FP = 3 và TN = 87. Bagging đúng 136/143, cây đơn đúng 135/143, chênh khoảng 0,70 điểm phần trăm accuracy. Precision ác của Bagging là 94,23%, F1 ác là 93,33%; xem phụ lục chỉ số khi được hỏi. Random Forest có cùng chỉ số tổng hợp ở seed 42 nhưng sai trên những quan sát khác: hai mô hình khác dự đoán ở hàng 291 và 128. Không suy ra tương đương từ điểm tổng hợp. ManualBagging dùng toàn bộ đặc trưng và hard voting; RF sklearn dùng ngẫu nhiên hóa đặc trưng và trung bình xác suất.

## Slide 13 — Bagging cao hơn cây đơn ở 9/10 lần chia

Người nói gợi ý: Trần Quốc Bảo.

Trung bình được trình bày theo phần trăm; SD mẫu theo điểm phần trăm. Mỗi seed đều chia lại 75/25 có phân tầng và chọn độ sâu trên train. Khi so accuracy trong cùng seed, Bagging cao hơn cây đơn 9 lần, bằng 1 lần, thấp hơn 0 lần; chênh lệch trung bình khoảng +1,96 điểm phần trăm. So với RF, các số tương ứng là 2, 4 và 4, chênh lệch trung bình −0,28 điểm phần trăm. Các holdout có thể giao nhau, nên không coi là mười phép thử độc lập hay suy ra giá trị p từ số lần thắng.

## Slide 14 — Tăng số cây có lợi, nhưng chưa tăng mãi

Người nói gợi ý: Trần Quốc Bảo.

Khảo sát chỉ dùng 426 mẫu train của seed 42, với năm fold ngoài. Trong phần học của mỗi fold, CV năm fold chọn độ sâu bằng cây đơn; các độ sâu là [2, 6, 2, 2, 6]. Các cấu hình B = [1, 5, 11, 21, 51, 101] dùng chung độ sâu và chuỗi seed tương ứng. Balanced accuracy trung bình tăng đến 95,26% ở 51 cây, rồi còn 95,07% ở 101 cây. SD tại 51 cây là 2,45 điểm phần trăm, không phải khoảng tin cậy. Đây là khảo sát bổ sung, chưa chứng minh 51 tối ưu tổng quát.

## Slide 15 — Tổ hợp 51 cây vẫn có thể dự đoán sai

Người nói gợi ý: Trần Quốc Bảo.

Quan sát được chọn có chỉ số test 2, tức mẫu thứ ba khi bắt đầu đếm từ 0, tương ứng hàng dữ liệu 291. Nhãn thật là lành tính, nhãn 1. Bagging nhận 27 phiếu ác và 24 phiếu lành, nên chọn nhãn 0 và tạo lỗi dương tính giả. Biên phiếu bằng 3/51 ≈ 0,0588; chênh lệch hai tỷ lệ là 5,88 điểm phần trăm, chưa phải xác suất bệnh đã hiệu chỉnh. RF dự đoán đúng mẫu này nhưng sai hàng 128, nên tổng FP vẫn bằng 3. Truy vết hai cây ở slide 21.

## Slide 16 — Mẫu sai nằm giữa các vùng trung tâm của hai lớp

Người nói gợi ý: Trần Quốc Bảo.

Ba đặc trưng được chọn từ tần suất xuất hiện tại nút gốc trên train: worst perimeter ở 16 cây, worst concave points ở 14 cây và worst radius ở 9 cây. Giá trị của mẫu 291 lần lượt là 109,10; 0,14890 và 16,25, đều nằm giữa trung vị hai lớp, đồng thời giữa Q3 lớp lành và Q1 lớp ác. Hộp biểu diễn Q1–Q3, vạch là trung vị, hình thoi là mẫu lỗi. Mỗi hàng có thang đo riêng, không so chiều dài giữa các đặc trưng. Phân tích này chưa xác định nguyên nhân y khoa.

## Slide 17 — Hard/soft gần nhau; sqrt chưa cải thiện

Người nói gợi ý: Trần Quốc Bảo.

Đối chứng 2 × 2 tách hai yếu tố: xét toàn bộ đặc trưng hoặc sqrt; hard voting hoặc trung bình xác suất. Chỉ dùng 426 mẫu train của seed 42, không dùng test 143. Cùng năm fold ngoài, trong phần học mỗi fold, CV năm fold chọn độ sâu bằng cây đơn rồi dùng chung cho bốn cấu hình. Giữ nguyên bootstrap và seed từng cây giữa hai nhóm đặc trưng; hard/soft dùng chính cùng các cây đã học. All hard/soft đều đạt 95,26 ± 2,45%; sqrt hard 93,62 ± 3,48%, sqrt soft 93,44 ± 3,77%. All hard/soft trùng nhãn trên 426 lượt dự đoán ngoài fold; sqrt khác ở một quan sát. Giữ hard và đổi all sang sqrt, BA giảm khoảng 1,63 điểm phần trăm. Chưa có kiểm định ý nghĩa thống kê. Đây là phân tích bổ sung sau thí nghiệm gốc, chưa tối ưu riêng mỗi biến thể.

## Slide 18 — Đa dạng hơn chưa đủ: cây cơ sở cũng phải đủ tốt

Người nói gợi ý: Trần Quốc Bảo.

D là tỷ lệ các cặp cây dự đoán khác nhãn, trung bình trên các quan sát và fold; chưa phải tương quan lỗi hay mức độc lập. Với hai lớp và 51 cây, D tối đa khoảng 50,98%. Ngẫu nhiên hóa đặc trưng làm tăng bất đồng nhưng giảm chất lượng cây cơ sở; balanced accuracy tổ hợp hard cũng giảm. Điều này chưa chứng minh xét toàn bộ đặc trưng luôn tốt hơn. Công thức phương sai σ²[ρ + (1 − ρ)/B] chỉ tạo trực giác khi các dự đoán số cùng phương sai và tương quan; không suy ρ từ D.

## Slide 19 — Tái lập được; kết luận có giới hạn

Người nói gợi ý: Trần Quốc Bảo.

Bộ mã có 26 kiểm thử giúp phát hiện lỗi cài đặt, không thay thế đánh giá ngoài mẫu. Gói nộp kèm chương trình, kết quả và báo cáo. Chạy thí nghiệm gốc để tạo results.json trước hai script bổ sung; dùng các phiên bản thư viện trong requirements.txt. Học tuần tự B cây có chi phí xấp xỉ B lần chi phí một cây; dự đoán K quan sát, độ sâu d có bậc O(KBd). Đây là phân tích cấu trúc, chưa đo thời gian thực. Demo nhanh lưu ở outputs/quick để giữ riêng kết quả mặc định.

## Slide 20 — Ba kết luận từ dữ liệu đã khảo sát

Người nói gợi ý: Trần Quốc Bảo.

Kết thúc bằng ba ý trả lời câu hỏi nghiên cứu. Bagging liên hệ bootstrap với tổng hợp dự đoán; cải thiện so với cây đơn trong các lần chia đã khảo sát; nhưng tăng số cây hoặc mức bất đồng chưa tự động tạo mô hình tốt hơn. Chưa thể khẳng định Bagging vượt trội nhất quán so với RF, 51 cây tối ưu tổng quát hay mô hình đủ hiệu quả lâm sàng. Phần trình bày chính dừng tại đây. Hai thành viên cùng tham gia hỏi đáp và chỉ mở slide dự phòng phù hợp với câu hỏi.

## Slide 21 — A. Cùng mẫu 291, hai cây đi tới hai nhãn

Người nói gợi ý: Cả hai — dự phòng khi hỏi đáp.

Các ngưỡng trên slide đã làm tròn để dễ đọc; JSON lưu giá trị đầy đủ. Mẫu có worst radius = 16,25; worst concave points = 0,14890; worst symmetry = 0,29620; mean concave points = 0,04819 và worst perimeter = 109,10. Theo hai chuỗi điều kiện khác nhau, cây thứ nhất đến lá chứa 18 lượt nhãn ác; cây thứ hai đến lá có 256 lượt lành và 3 lượt ác. Bootstrap có thể lặp hàng nên số lượt chưa phải số bệnh nhân khác nhau. Hai đường đi chỉ giải thích hai phiếu; tổ hợp cuối dùng đủ 51 cây.

## Slide 22 — B. Tính chỉ số với ác tính là lớp dương

Người nói gợi ý: Cả hai — dự phòng khi hỏi đáp.

TP và FN đọc từ hàng nhãn thật ác tính; FP và TN từ hàng nhãn thật lành tính. Với Bagging tại seed 42, TP = 49, FN = 4, FP = 3 và TN = 87. Balanced accuracy bằng (49/53 + 87/90)/2 ≈ 94,56%. Vì lớp dương có nhãn 0, các hàm tính precision, recall và F1 dùng pos_label = 0. Phân biệt accuracy test 95,10% với balanced accuracy CV 95,26% trên train: chúng thuộc hai quy trình khác nhau. Tỷ lệ phiếu cây chưa phải xác suất bệnh đã hiệu chỉnh.

## Slide 23 — C. Boosting và Stacking khác Bagging ở đâu?

Người nói gợi ý: Cả hai — dự phòng khi hỏi đáp.

Trong ví dụ AdaBoost nhị phân, sai số có trọng số bằng 0,2 cho alpha = 0,5 ln 4 ≈ 0,693. Nhóm sai nhân 2, nhóm đúng nhân 0,5; sau chuẩn hóa, nhóm sai mang 50% trọng số. Đây chưa phải accuracy tăng từ 20% lên 50%. Stacking dùng dự đoán ngoài fold để mỗi quan sát train nhận dự đoán từ mô hình chưa học nó, rồi học meta-model. Khi dự đoán dữ liệu mới, các mô hình cơ sở học lại trên toàn train. Nếu hỏi 51 cây: đó là cấu hình ban đầu, khảo sát bổ sung chưa chứng minh tối ưu tổng quát.

## Slide 24 — D. Tài liệu tham khảo và cách tái lập

Người nói gợi ý: Cả hai — dự phòng khi hỏi đáp.

Tài liệu: [1] https://doi.org/10.1007/BF00058655; [2] https://doi.org/10.1023/A:1010933404324; [3] https://scikit-learn.org/stable/modules/ensemble.html; [4] https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_breast_cancer.html; [5] https://scikit-learn.org/stable/modules/tree.html; [6] https://doi.org/10.1006/jcss.1997.1504; [7] https://doi.org/10.1016/S0893-6080(05)80023-1. Mã nhóm: https://github.com/Huyngaongow/hocmaygk. Dùng Python 3.12 và requirements.txt. Chạy thí nghiệm gốc trước hai phân tích bổ sung. Kiểm thử: python -m unittest discover -s tests -v. Ví dụ: python examples/toy_bagging.py. Demo nhanh: python de_5_ensemble_learning.py --repeats 1 --output-dir outputs/quick. Dùng Python trong venv đã cài thư viện; trên Windows có thể gọi trực tiếp .venv\Scripts\python.exe.
