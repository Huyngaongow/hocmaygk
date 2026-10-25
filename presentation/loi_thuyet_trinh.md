# Lời thuyết trình — Đề 5: Ensemble Learning

26 slide: 24 trang chính và 2 trang phụ lục. Gợi ý khoảng 15–20 phút cho phần chính, rút gọn phần mở rộng khi cần.

Trước khi trình bày: bổ sung tên thành viên và lớp tại slide 1.

## Slide 01 — 

Mở đầu: Một cây quyết định có thể thay đổi đáng kể khi dữ liệu huấn luyện thay đổi. Ensemble Learning kết hợp nhiều mô hình để giảm tác động của những sai lệch riêng. Bài này giới thiệu các họ phương pháp, sau đó đi sâu vào bootstrap và hard voting qua Bagging tự triển khai. Mã cây cơ sở dùng scikit-learn; phần lấy mẫu và tổng hợp phiếu do nhóm tự viết. Trước khi nộp, điền tên thành viên và lớp trên trang bìa. Gợi ý thời lượng phần chính khoảng 15–20 phút; hai trang cuối là phụ lục.

## Slide 02 — Nhiều mô hình chỉ hữu ích khi có sự đa dạng

Ba phiếu trên trang chỉ minh họa ý tưởng, không phải dự đoán thật của chương trình. Nếu các cây cùng mắc một lỗi thì thêm cây không giải quyết được vấn đề. Hai yếu tố cần cân bằng là chất lượng mô hình cơ sở và tính đa dạng của chúng. Chúng ta sẽ lần lượt trả lời: ensemble kết hợp như thế nào; bootstrap tạo đa dạng ra sao; mã thực hiện phần nào; và kết quả trên dữ liệu độc lập có cải thiện hay không.

## Slide 03 — Bốn cách kết hợp thường gặp

Đây là các hướng tiếp cận phổ biến, không phải bốn nhóm tách rời tuyệt đối: Bagging cũng cần một quy tắc tổng hợp như voting. Bagging tạo đa dạng bằng lấy mẫu; Boosting xây dãy mô hình để xử lý sai sót; Voting có thể kết hợp các mô hình khác loại; Stacking học bộ kết hợp từ dự đoán ngoài mẫu. Trọng tâm triển khai của bài là Bagging, nhưng cần hiểu vị trí của nó trong toàn bộ Ensemble Learning. Random Forest là một mở rộng của ý tưởng Bagging cây với ngẫu nhiên hóa đặc trưng.

## Slide 04 — Đa dạng giúp giảm phương sai

Công thức này giải thích trực giác giảm phương sai khi lấy trung bình các dự đoán số. Giả thiết các mô hình có phương sai như nhau σ bình phương và tương quan cặp chung rho. Với 51 mô hình, rho bằng 0,2 cho phương sai trung bình khoảng 0,216 lần phương sai riêng, còn rho bằng 0,8 chỉ giảm xuống khoảng 0,804. Đây không phải công thức trực tiếp của tỷ lệ lỗi phân lớp. Với hard voting, hiệu quả còn phụ thuộc mô hình cơ sở và cấu trúc lỗi. Không thể nói ensemble luôn tốt hơn.

## Slide 05 — Hard Voting và Soft Voting có thể cho kết quả khác

Đây là ví dụ tính tay giả định. Hard voting chỉ dùng nhãn cuối cùng, nên hai trong ba mô hình chọn ác tính thì cả tổ hợp chọn ác tính. Soft voting lấy trung bình xác suất: 0,51 cộng 0,51 cộng 0,01 bằng 1,03; chia ba xấp xỉ 0,343. Xác suất lành tính trung bình khi đó xấp xỉ 0,657, nên chọn lành tính. Với trọng số, thay trung bình đều bằng tổng có trọng số chuẩn hóa. Soft voting cần xác suất đáng tin cậy; không tự động tốt hơn hard voting. Trong mã, ManualBagging dùng hard voting; sklearn Random Forest dùng trung bình xác suất.

## Slide 06 — Bagging: lấy mẫu lại, học độc lập, rồi tổng hợp

Bagging là viết tắt của bootstrap aggregating. Mỗi cây nhận 426 lượt lấy mẫu từ 426 mẫu train; một quan sát có thể lặp lại nhiều lần, một số quan sát không xuất hiện. Không chia train thành 51 tập rời nhau. Các cây có thể học song song về mặt thuật toán; bản mã minh họa đang huấn luyện tuần tự để đơn giản và tiết kiệm tài nguyên. Test hoàn toàn không tham gia bootstrap. Sau huấn luyện, gửi cùng một quan sát mới qua tất cả các cây rồi đếm phiếu. Bằng cách thay đổi mẫu, các cây có thể học những ranh giới quyết định khác nhau.

## Slide 07 — Ví dụ bootstrap: 5 quan sát, 5 lượt lấy mẫu

Chỉ số 0 xuất hiện hai lần trong mẫu của cây 1, trong khi chỉ số 3 không có mặt. Các quan sát không được chọn gọi là out-of-bag đối với cây đó. Với một quan sát cố định, xác suất không chọn ở một lượt là 1 trừ 1/N; qua N lượt độc lập là lũy thừa N. Khi N lớn, xác suất tiến đến e mũ âm một, khoảng 36,8%. Với N bằng 5 trong ví dụ nhỏ, xác suất chính xác là 0,8 mũ 5 bằng 32,768%, không phải đúng 36,8%. Bản nâng cấp tính hard-vote OOB chỉ từ cây chưa thấy mẫu, đồng thời vẫn dùng test riêng để đánh giá. Điểm OOB không độc lập với bước chọn độ sâu trên train.

## Slide 08 — Một cây học phép chia như thế nào?

Đây là dữ liệu một chiều giả lập để có thể tính tay, không phải các quan sát của Breast Cancer. Cây 1 dùng bootstrap [0,0,2,4,1], tức là các cặp (1,lành), (1,lành), (3,ác), (5,ác), (2,lành). Gini trước chia bằng 0,48. Với ngưỡng 2,5, nhánh trái có ba mẫu đều lành, nhánh phải có hai mẫu đều ác. Gini mỗi nhánh bằng 0; trung bình có trọng số 3/5 nhân 0 cộng 2/5 nhân 0 cũng bằng 0. Mức giảm là 0,48. Thực tế cây thử các ngưỡng trên nhiều đặc trưng và lặp lại các phép chia đến điều kiện dừng. Trong thí nghiệm độ sâu tối đa là 3.

## Slide 09 — Từ phiếu riêng lẻ đến quyết định của tổ hợp

I là hàm chỉ thị: đúng thì nhận 1, sai thì nhận 0. Cộng theo tất cả cây cho từng lớp c. Với ba dự đoán giả định [0,1,0], lớp 0 có hai phiếu còn lớp 1 có một phiếu, nên argmax chọn 0, tức ác tính. Đây là ví dụ riêng để tính phép tổng hợp, không khẳng định là đầu ra của ba cây trong ví dụ chia nút trước đó. Trong triển khai dùng 51 cây cho hai lớp nên không hòa phiếu. Nếu áp dụng đa lớp thì số cây lẻ vẫn có thể hòa; hàm argmax khi hòa chọn chỉ số lớp đầu tiên.

## Slide 10 — Boosting: mô hình sau tập trung vào sai sót trước

AdaBoost là ví dụ để giải thích Boosting chứ chưa được triển khai trong mã thực nghiệm này. Nhãn và dự đoán trong công thức cập nhật cổ điển được mã hóa âm một và dương một. Sai số epsilon là tổng trọng số của các mẫu sai, không nhất thiết là tỷ lệ đếm mẫu. Nếu epsilon bằng 0,2, trọng số mô hình alpha bằng một nửa log tự nhiên của bốn, khoảng 0,693. Nhóm sai nhân hai, nhóm đúng nhân một phần hai; chuẩn hóa xong tổng trọng số nhóm sai tăng từ 0,2 lên 0,5. Gradient Boosting lại xây mô hình theo hướng giảm loss, thường khớp gradient âm; không mô tả mọi Boosting bằng duy nhất cập nhật AdaBoost này.

## Slide 11 — Stacking học một mô hình để kết hợp các mô hình

OOF nghĩa là out-of-fold. Chia train thành K fold. Với mỗi mô hình cơ sở, huấn luyện trên K trừ một fold và dự đoán fold còn lại; ghép các dự đoán để mỗi mẫu train có một dự đoán từ mô hình chưa thấy nó. Các cột OOF này, cùng nhãn train, huấn luyện meta-model. Khi dự đoán dữ liệu mới, mô hình cơ sở được huấn luyện lại trên toàn train, tạo đầu vào cho meta-model đã học. Nếu dùng dự đoán in-sample quá tốt để học meta-model thì tầng hai có thể học một tín hiệu không phản ánh khả năng tổng quát. Stacking ở đây là nội dung lý thuyết mở rộng, chưa chạy thực nghiệm.

## Slide 12 — Bài toán: phân loại mẫu khối u vú

Dữ liệu Breast Cancer Wisconsin Diagnostic có 569 quan sát và 30 đặc trưng số trích từ ảnh nhân tế bào. Hai nhãn của thư viện là 0 cho malignant, tức ác tính, và 1 cho benign, tức lành tính. Tổng thể có 212 mẫu ác tính và 357 mẫu lành tính. Bài không huấn luyện trực tiếp từ ảnh; đầu vào là bộ đặc trưng đã được chuẩn bị. Các cây không yêu cầu chuẩn hóa thang đo như một số phương pháp khoảng cách. Đây là minh họa học thuật, không phải một hệ thống chẩn đoán đã được xác thực.

## Slide 13 — Thiết kế thí nghiệm giữ test ngoài quá trình chọn độ sâu

Chia dữ liệu bằng train_test_split với stratify bằng nhãn và random_state 42. Test có 53 ca ác tính và 90 ca lành tính. Trong train, thử max_depth từ 2 đến 6 bằng StratifiedKFold năm fold, chọn theo balanced accuracy trung bình. Độ sâu 3 đạt khoảng 93,73%, cao nhất trong các ứng viên. Biểu đồ cột chỉ thể hiện phần vượt 90% để nhìn khác biệt; đây không phải trục bắt đầu từ 0. Độ sâu được chọn trên cây đơn và dùng chung cho Bagging và Random Forest. Thiết kế giúp minh họa đơn giản nhưng không phải tìm cấu hình tối ưu riêng cho từng mô hình. Test chỉ được xem sau khi chốt cấu hình.

## Slide 14 — Tự viết hai phần cốt lõi: bootstrap và voting

Đây là mã trích lược từ ensemble_model.py để vừa slide; dấu ba chấm thay phần cấp seed riêng cho mỗi cây. de_5_ensemble_learning.py điều phối thí nghiệm và xuất báo cáo. rng.integers tạo N chỉ số trong khoảng từ 0 đến N trừ một, cho phép trùng chỉ số. encoded là nhãn đã ánh xạ sang chỉ số lớp bởi np.unique. Mỗi cây dùng các hàng X và nhãn theo cùng indices. Phần voting khởi tạo ma trận số quan sát nhân số lớp, rồi np.add.at tăng một ở ô tương ứng với từng dự đoán của từng cây. Cuối cùng argmax lấy lớp có nhiều phiếu, rồi ánh xạ về nhãn gốc. Mã kiểm tra dữ liệu, hỗ trợ nhãn không liên tiếp và tương thích clone/CV của sklearn. Không nhận phần cài cây quyết định là tự viết.

## Slide 15 — Bagging tự viết và Random Forest khác nhau ở đâu?

Cả hai phương pháp sử dụng bootstrap nhưng Random Forest ngẫu nhiên hóa cả việc chọn đặc trưng ở từng phép chia. Với mặc định max_features bằng sqrt và 30 đặc trưng, giá trị mục tiêu là 5. Thư viện có thể xem thêm đặc trưng để tìm phép chia hợp lệ, nên không hiểu là giới hạn cứng tuyệt đối trong mọi trường hợp. Khác biệt quan trọng nữa là quy tắc kết hợp: ManualBagging đếm nhãn cứng, RandomForestClassifier lấy trung bình xác suất của các cây rồi chọn lớp lớn nhất. Vì vậy không mô tả thí nghiệm như thể chỉ thay đổi một yếu tố đặc trưng. Đây là hai baseline để đối chiếu, không phải nghiên cứu tách riêng tác động từng thành phần.

## Slide 16 — Bagging cải thiện nhẹ trên lần chia test này

Bảng này chỉ thuộc seed tham chiếu 42: cây đơn đạt accuracy 94,41%, Bagging và Random Forest cùng đạt 95,10%. Precision, recall và F1 lấy ác tính làm lớp dương, mặc dù mã nhãn là 0. Accuracy của Bagging tương đương đúng 136 trên 143 mẫu, cao hơn cây đơn đúng một mẫu. Mức chênh là khoảng 0,70 điểm phần trăm, không phải 0,70% cải thiện tương đối. Hai mô hình có cùng chỉ số tổng hợp không đủ để suy ra giống nhau trên mọi quan sát. Bản nâng cấp còn chạy 10 seed và sẽ báo cáo ở trang tiếp theo; không trộn điểm seed 42 với điểm trung bình nhiều split.

## Slide 17 — Đánh giá lại trên 10 lần chia phân tầng

Đánh giá bổ sung gồm các seed cố định từ 42 đến 51, không chọn seed có điểm đẹp nhất. Trong mỗi lần chạy, ba mô hình dùng cùng một train/test phân tầng; độ sâu được chọn lại bằng CV trên train của chính seed đó, sau đó dùng chung. Mỗi test có 143 mẫu nhưng các test giữa các seed có thể giao nhau. Trung bình accuracy của cây đơn, Bagging và Random Forest lần lượt là khoảng 92,80%, 94,76% và 95,03%. SD mẫu dùng ddof bằng 1; độ biến thiên accuracy tương ứng khoảng 1,84, 1,59 và 1,85 điểm phần trăm. Đây là thống kê mô tả chứ không phải khoảng tin cậy độc lập. RF có accuracy trung bình cao hơn nhẹ, Bagging có recall ác tính trung bình cao hơn nhẹ; chưa thể coi là bằng chứng một phương pháp luôn thắng.

## Slide 18 — Out-of-bag: chỉ bỏ phiếu cho mẫu cây chưa học

Tại seed 42, Bagging có accuracy hard-vote OOB bằng 401 chia 426, khoảng 94,13%, và coverage 100%. Mỗi mẫu nhận phiếu từ 8 đến 34 cây không thấy nó trong bootstrap, không phải cùng nhận đủ 51 phiếu. Mã tính mask không có mặt bằng bincount, rồi chỉ dự đoán các hàng đó để tích lũy phiếu OOB. Với số cây ít hơn có thể có mẫu không nhận phiếu: oob_decision_function_ đánh dấu NaN và điểm chỉ tính trên các mẫu được bao phủ. Quan trọng: độ sâu đã được chọn trên train bằng CV, nên điểm OOB tính sau đó không hoàn toàn độc lập với lựa chọn siêu tham số. OOB là chẩn đoán bổ sung, không thay thế kết quả test riêng và không phải xác suất chẩn đoán.

## Slide 19 — Nhìn vào ca bỏ sót, không chỉ accuracy

Trong ma trận này hàng là nhãn thật, cột là nhãn dự đoán; thứ tự cả hai trục là ác tính rồi lành tính. Vì ác tính là lớp dương, ô trên trái là TP, ô trên phải là FN. Cây đơn có TP 48 và FN 5; Bagging có TP 49 và FN 4. Cả hai có FP 3 và TN 87. Recall Bagging bằng 49 chia 53, khoảng 92,45%. Precision bằng 49 chia 52, khoảng 94,23%. Giảm được một ca bỏ sót trên tập test này là một quan sát thực nghiệm, chưa chứng minh lợi ích đáng tin cậy khi triển khai thực tế. Ma trận của Random Forest trùng các số đếm tổng hợp của Bagging trong lần chạy.

## Slide 20 — Phiếu bất đồng có thể dẫn đến dự đoán sai

Đây là trace thật của seed 42, không phải ví dụ giả định. Chương trình chọn mẫu test đầu tiên có phiếu chia hai phía, không chọn theo việc dự đoán đúng. Mẫu ở vị trí test 2 ứng với hàng 291 trong dữ liệu gốc; các chỉ số đều đếm từ 0, không phải mã bệnh nhân. Có 27 phiếu ác tính và 24 phiếu lành tính, nên hard voting chọn ác tính. Nhãn thật là lành tính, do đó đây là một dương tính giả. Có tổng 45 trong 143 mẫu test có bất đồng giữa cây. Tỷ lệ 27 trên 51 là tỷ lệ hard-vote, không phải xác suất bệnh đã hiệu chỉnh. Ví dụ cũ của quan sát test đầu tiên vẫn lưu trong worked_example: 0 phiếu ác và 51 phiếu lành, dự đoán đúng. Hai ví dụ cho thấy đồng thuận hoặc bất đồng đều phải kiểm tra bằng nhãn thật.

## Slide 21 — Kết quả có ích, nhưng phạm vi kết luận còn hẹp

Bản nâng cấp đã chạy 10 seed và báo cáo SD mẫu, nhưng các test có thể giao nhau nên chúng không phải mười tập kiểm định độc lập. Thiết kế chọn độ sâu bằng cây đơn có thể không phải tốt nhất cho Bagging hay Random Forest. OOB là đánh giá phụ vì depth đã chọn trên train trước đó. Nếu tuning riêng hoặc khảo sát số cây, phải dùng train/CV và giữ test ngoài lựa chọn cấu hình. Boosting và Stacking vẫn mới được giải thích lý thuyết, chưa phải mô hình đã đo trong bảng kết quả. Chưa có kiểm định ngoài trên quần thể độc lập; ứng dụng y tế cần dữ liệu và quy trình xác thực phù hợp hơn nhiều.

## Slide 22 — Demo nhanh hoặc chạy đầy đủ 10 seed

Mở terminal tại thư mục kho, dùng Python đã cài requirements.txt. Trên Windows có thể dùng py thay python. Thêm --repeats 1 --output-dir outputs/quick để demo nhanh vào thư mục riêng; khi đó summary chỉ có một lần chạy và SD là null, không phải 0. Lệnh không có tham số chạy 10 seed từ 42 đến 51. results.json có seed tham chiếu, OOB, ví dụ bất đồng và tổng hợp nhiều lần chạy; report.md giải thích kết quả. metrics.csv và predictions.csv thuộc seed tham chiếu, repeated_metrics.csv chứa từng seed, summary_metrics.csv chứa mean và SD. Mỗi lần chạy ghi đè các tệp cùng tên trong output-dir; outputs/quick giữ riêng kết quả demo và bảo toàn kết quả 10 seed trong outputs. Các slide này được tạo từ kết quả đầy đủ 10 seed, không được suy ra bảng đó từ demo một seed.

## Slide 23 — Ba điều cần nhớ

Kết lại ba ý. Một: hiệu quả ensemble đến từ cả chất lượng mô hình cơ sở lẫn sự đa dạng. Hai: Bagging gồm lấy mẫu có hoàn lại, học độc lập và tổng hợp; mã còn có OOB đúng theo các cây chưa thấy mẫu. Ba: seed tham chiếu đạt 95,10% accuracy và vẫn bỏ sót bốn ca ác tính; qua 10 holdout, accuracy trung bình của Bagging khoảng 94,76% với SD mẫu 1,59 điểm phần trăm. Các holdout có giao nhau nên không suy ra độ tin cậy độc lập hoặc hiệu quả lâm sàng. Nếu nhóm ba người, có thể chia trang 1–9, 10–15 và 16–24; đây chỉ là gợi ý, không phải phân công đã xác nhận. Hai trang cuối là phụ lục hỏi đáp và phép tính chỉ số.

## Slide 24 — Tài liệu tham khảo

Các nguồn 1 và 2 là các bài báo gốc về Bagging và Random Forest. Nguồn 6 cho AdaBoost và nguồn 7 cho Stacking. Tài liệu scikit-learn giải thích các lớp thư viện và đặc tính dataset. Số liệu thực nghiệm trong bài được lấy từ outputs/results.json của kho, không lấy từ các bài báo hoặc benchmark bên ngoài. Mã và requirements.txt đi kèm để tái lập; sử dụng cùng seed và phiên bản giúp giảm khác biệt do môi trường. Các URL có thể bấm trong PowerPoint. PDF đề bài yêu cầu đủ nguyên lý, quy trình, ứng dụng và mã nguồn; phần trình bày đã lần lượt bao phủ các nội dung này.

## Slide 25 — Câu hỏi thường gặp khi bảo vệ

Đây là phụ lục cho hỏi đáp, không bắt buộc trình bày hết. Nếu được hỏi số cây có tối ưu không, trả lời trung thực là chưa; 51 là cấu hình minh họa cố định, không chọn dựa trên test. Nếu được hỏi bootstrap có mất dữ liệu không, mỗi cây có thể không thấy một phần dữ liệu nhưng các cây sử dụng các mẫu khác nhau; không đảm bảo mọi mẫu đều được thấy ở mọi cây. Nếu được hỏi vì sao Random Forest bằng Bagging, các số liệu tổng hợp trùng nhau trong lần chạy không chứng minh hai mô hình tương đương. Nếu được hỏi có thể chẩn đoán không, trả lời chưa có kiểm định lâm sàng và thí nghiệm vẫn bỏ sót ca ác tính.

## Slide 26 — Cách tính chỉ số với ác tính là lớp dương

Dùng trang này khi cần giải thích cụ thể các con số. Quy ước dương là ác tính dù mã nhãn bằng 0. TP là ca ác được dự đoán ác; FN là ca ác bị dự đoán lành; FP là ca lành bị dự đoán ác; TN là ca lành được dự đoán lành. Tổng mẫu bằng 49 cộng 4 cộng 3 cộng 87 bằng 143. F1 là trung bình điều hòa của precision và recall, tương đương công thức hai TP chia hai TP cộng FP cộng FN. Balanced accuracy trung bình recall của hai lớp được dùng để chọn độ sâu trong CV, khác accuracy thường ở bảng test. Nếu mẫu test thiếu một lớp thì cần xem lại cách diễn giải; ở đây cả hai lớp đều có mặt.
