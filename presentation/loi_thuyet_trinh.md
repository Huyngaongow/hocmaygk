# Lời thuyết trình — Đề 5: Ensemble Learning

26 slide: 24 trang chính và 2 trang phụ lục. Gợi ý khoảng 15–20 phút cho phần chính; thời lượng thực tế theo giảng viên. Nói ngắn phần mở rộng ở slide 10–11 khi cần.

Thông tin bìa lấy từ report/group_info.json. Ví dụ slide 7–9 cùng một bộ dữ liệu giả lập và có mã tái lập. Các bảng thực nghiệm thuộc chạy đủ 10 seed.

## Slide 01 — 

Mở đầu: Một cây quyết định có thể thay đổi đáng kể khi dữ liệu huấn luyện thay đổi. Ensemble Learning kết hợp nhiều mô hình để giảm tác động của những sai lệch riêng. Bài này giới thiệu các họ phương pháp, sau đó đi sâu vào bootstrap và hard voting qua Bagging tự triển khai. Mã cây cơ sở dùng scikit-learn; phần lấy mẫu và tổng hợp phiếu do nhóm tự viết. Thông tin thành viên và giảng viên được lấy thống nhất từ report/group_info.json. Gợi ý thời lượng phần chính khoảng 15–20 phút; hai trang cuối là phụ lục.

## Slide 02 — Nhiều mô hình chỉ hữu ích khi có sự đa dạng

Ba phiếu trên trang chỉ minh họa ý tưởng, không phải dự đoán thật của chương trình. Nếu các cây cùng mắc một lỗi thì thêm cây không giải quyết được vấn đề. Hai yếu tố cần cân bằng là chất lượng mô hình cơ sở và tính đa dạng của chúng. Chúng ta sẽ lần lượt trả lời: ensemble kết hợp như thế nào; bootstrap tạo đa dạng ra sao; mã thực hiện phần nào; và kết quả trên dữ liệu độc lập có cải thiện hay không.

## Slide 03 — Bốn cách kết hợp thường gặp

Đây là các hướng tiếp cận phổ biến, không phải bốn nhóm tách rời tuyệt đối: Bagging cũng cần một quy tắc tổng hợp như voting. Bagging tạo đa dạng bằng lấy mẫu; Boosting xây dãy mô hình để xử lý sai sót; Voting có thể kết hợp các mô hình khác loại; Stacking học bộ kết hợp từ dự đoán ngoài mẫu. Trọng tâm triển khai của bài là Bagging, nhưng cần hiểu vị trí của nó trong toàn bộ Ensemble Learning. Random Forest là một mở rộng của ý tưởng Bagging cây với ngẫu nhiên hóa đặc trưng.

## Slide 04 — Vì sao Bagging có thể ổn định hơn?

Phần chính chỉ cần hiểu rằng cây quyết định có thể thay đổi khi dữ liệu train đổi; lấy nhiều bootstrap và tổng hợp giúp giảm dao động khi các cây không mắc lỗi quá giống nhau. Công thức bổ sung nếu được hỏi: Var(trung bình) = σ²[ρ + (1−ρ)/B], với B là số mô hình, σ² là phương sai chung, ρ là tương quan cặp chung. Với B=51, ρ=0,2 cho khoảng 0,216σ²; ρ=0,8 cho khoảng 0,804σ². Công thức áp dụng cho trung bình dự đoán số dưới các giả thiết trên, không phải công thức trực tiếp của lỗi hard voting. Không cần chứng minh công thức trong phần thuyết trình chính và không kết luận ensemble luôn tốt hơn.

## Slide 05 — Hard Voting và Soft Voting có thể cho kết quả khác

Đây là ví dụ tính tay giả định. Hard voting chỉ dùng nhãn cuối cùng, nên hai trong ba mô hình chọn ác tính thì cả tổ hợp chọn ác tính. Soft voting lấy trung bình xác suất: 0,51 cộng 0,51 cộng 0,01 bằng 1,03; chia ba xấp xỉ 0,343. Xác suất lành tính trung bình khi đó xấp xỉ 0,657, nên chọn lành tính. Với trọng số, thay trung bình đều bằng tổng có trọng số chuẩn hóa. Soft voting cần xác suất đáng tin cậy; không tự động tốt hơn hard voting. Trong mã, ManualBagging dùng hard voting; sklearn Random Forest dùng trung bình xác suất.

## Slide 06 — Bagging: lấy mẫu lại, học độc lập, rồi tổng hợp

Bagging là viết tắt của bootstrap aggregating. Mỗi cây nhận 426 lượt lấy mẫu từ 426 mẫu train; một quan sát có thể lặp lại nhiều lần, một số quan sát không xuất hiện. Không chia train thành 51 tập rời nhau. Các cây có thể học song song về mặt thuật toán; bản mã minh họa đang huấn luyện tuần tự để đơn giản và tiết kiệm tài nguyên. Test hoàn toàn không tham gia bootstrap. Sau huấn luyện, gửi cùng một quan sát mới qua tất cả các cây rồi đếm phiếu. Bằng cách thay đổi mẫu, các cây có thể học những ranh giới quyết định khác nhau.

## Slide 07 — Ví dụ bootstrap: 5 quan sát, 5 lượt lấy mẫu

Ba trang 7–9 dùng xuyên suốt cùng một ví dụ giả lập: x=[1,2,3,4,5], nhãn=[lành,lành,ác,ác,ác]. Ba bootstrap được chọn cố định để nhìn rõ sự khác nhau giữa cây; trong Bagging thực nghiệm, chúng được lấy ngẫu nhiên. Chỉ số 0 xuất hiện hai lần trong mẫu h1; chỉ số 3 vắng ở h1, chỉ số 2 vắng ở h2, chỉ số 0 vắng ở h3. Các mẫu vắng được gọi là OOB đối với cây tương ứng. Chạy python examples/toy_bagging.py --output-dir outputs/toy để tái lập toàn bộ bảng, ngưỡng và phiếu. Với N=5, xác suất một mẫu vắng là (4/5)^5=32,768%; khi N lớn mới gần 36,8%. Các bản bootstrap cụ thể được chọn để dạy cơ chế, không dùng làm thực nghiệm đánh giá hiệu năng.

## Slide 08 — Một cây học phép chia như thế nào?

Đây vẫn là dữ liệu giả lập từ slide 7, không phải quan sát Breast Cancer. Cây h1 nhận (1,lành),(1,lành),(3,ác),(5,ác),(2,lành), nên Gini=1−(3/5)^2−(2/5)^2=0,48. Ngưỡng 2,5 là trung điểm giữa 2 và 3: trái có ba mẫu lành, phải có hai mẫu ác; Gini sau chia=(3/5)×0+(2/5)×0=0. Mức giảm 0,48. Vì Gini không âm, đây là phép chia tối ưu của nút. h2 thiếu x=3 nên ranh giới giữa x=2 và x=4 là 3; h3 có ranh giới 2,5. Mỗi cây ví dụ chỉ sâu một mức; mô hình thật được chọn max_depth bằng CV. Mã ví dụ dùng sklearn tính ngưỡng rồi xuất JSON để đối chiếu phép tính tay.

## Slide 09 — Cùng một mẫu mới, ba cây cho hai phía phiếu

Đây là dự đoán thật của ba cây một mức đã học từ chính ba bootstrap ở slide 7. h1 và h3 có ngưỡng 2,5 nên x=2,8 đi sang phải và nhận nhãn ác. h2 có ngưỡng 3 nên x=2,8 đi sang trái và nhận nhãn lành. Hai phiếu ác thắng một phiếu lành. Công thức H(x)=argmax_c Σ_b I[h_b(x)=c]: I là hàm chỉ thị, đếm số cây chọn từng lớp rồi lấy lớp có phiếu lớn nhất. Mẫu mới x=2,8 chưa có nhãn thật nên không kết luận dự đoán đúng hay sai; đây là dữ liệu giả lập, không phải một bệnh nhân. Tỷ lệ 2/3 cũng không phải xác suất bệnh đã hiệu chỉnh. Dùng python examples/toy_bagging.py --output-dir outputs/toy để kiểm tra. Khi hai lớp và 51 cây thì không hòa; đa lớp vẫn có thể hòa, mã chọn lớp đầu trong classes_.

## Slide 10 — Boosting: học tiếp từ những sai sót trước

Đây là tổng quan để phân biệt Boosting với Bagging; phần chính không cần đi sâu công thức. AdaBoost chưa được triển khai trong mã thực nghiệm này. Số 20%→50% là ví dụ cập nhật trọng số, không phải accuracy hay phần trăm mẫu bị thay nhãn. Nếu được hỏi phép tính: với sai số có trọng số ε=0,2, α=½ln((1−ε)/ε)=0,693; nhóm sai nhân exp(α)=2, nhóm đúng nhân exp(−α)=0,5; sau chuẩn hóa, khối lượng trọng số nhóm sai là 0,2×2/(0,2×2+0,8×0,5)=0,5. Nhãn trong cập nhật cổ điển mã hóa −1,+1. Gradient Boosting giảm loss qua chuỗi mô hình, không dùng nguyên xi quy tắc AdaBoost này. Có thể nói ngắn slide 10–11 để dành thời gian cho Bagging tự triển khai.

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

## Slide 22 — Demo: hiểu cơ chế trước, xem kết quả sau

Mở terminal tại thư mục kho, dùng Python đã cài requirements.txt; trong cloud có thể thay python bằng .venv/bin/python. Chạy ví dụ nhỏ trước để thấy ba ngưỡng 2,5;3;2,5 và hai phiếu ác thắng một phiếu lành ở x=2,8. Sau đó chạy mô hình thật với --repeats 1 --output-dir outputs/quick. Demo một seed không tạo SD bằng 0; SD không xác định nên lưu null. Lệnh python de_5_ensemble_learning.py không có tham số chạy đủ 10 seed 42–51 vào outputs/. results.json lưu cấu hình, OOB, trace và số liệu; report.md giải thích thí nghiệm. Báo cáo bài viết hoàn chỉnh nằm ở report/Bao_cao_De_5_Ensemble_Learning.docx và PDF cùng tên, khác PDF slide ở thư mục gốc. Mỗi lần chạy thay thế các tệp cùng tên trong output-dir; thư mục quick giữ riêng demo. Các bảng nhiều seed trên slide lấy từ chạy đầy đủ, không suy từ demo một seed. Chuẩn bị sẵn output làm phương án dự phòng nếu buổi trình bày không chạy được máy.

## Slide 23 — Ba điều cần nhớ

Kết lại ba ý. Một: hiệu quả ensemble đến từ cả chất lượng mô hình cơ sở lẫn sự đa dạng. Hai: Bagging gồm lấy mẫu có hoàn lại, học độc lập và tổng hợp; ví dụ nhỏ đã nối đủ dữ liệu, ba bootstrap, ba cây và phiếu. Ba: seed tham chiếu đạt 95,10% accuracy và vẫn bỏ sót bốn ca ác tính; qua 10 holdout, accuracy trung bình của Bagging khoảng 94,76%, SD mẫu 1,59 điểm phần trăm. Chưa suy ra hiệu quả lâm sàng hoặc một phương pháp luôn thắng. Gợi ý tập luyện hai người: Nguyễn Nghĩa Hiếu trình bày trang 1–11, Trần Quốc Bảo trình bày trang 12–24; chuyển lời ở trang 12 từ ví dụ nhỏ sang bài toán thật. Đây là phương án chuẩn bị, không phải xác nhận lịch sử đóng góp. Cả hai cần hiểu code và sẵn sàng trả lời. Hai trang cuối dùng khi hỏi đáp.

## Slide 24 — Tài liệu tham khảo

Các nguồn 1 và 2 là các bài báo gốc về Bagging và Random Forest. Nguồn 6 cho AdaBoost và nguồn 7 cho Stacking. Tài liệu scikit-learn giải thích các lớp thư viện và đặc tính dataset. Số liệu thực nghiệm trong bài được lấy từ outputs/results.json của kho, không lấy từ các bài báo hoặc benchmark bên ngoài. Mã và requirements.txt đi kèm để tái lập; sử dụng cùng seed và phiên bản giúp giảm khác biệt do môi trường. Các URL có thể bấm trong PowerPoint. PDF đề bài yêu cầu đủ nguyên lý, quy trình, ứng dụng và mã nguồn; phần trình bày đã lần lượt bao phủ các nội dung này.

## Slide 25 — Câu hỏi thường gặp khi bảo vệ

Đây là phụ lục cho hỏi đáp, không bắt buộc trình bày hết. Nếu được hỏi số cây có tối ưu không, trả lời trung thực là chưa; 51 là cấu hình minh họa cố định, không chọn dựa trên test. Nếu được hỏi bootstrap có mất dữ liệu không, mỗi cây có thể không thấy một phần dữ liệu nhưng các cây sử dụng các mẫu khác nhau; không đảm bảo mọi mẫu đều được thấy ở mọi cây. Nếu được hỏi vì sao Random Forest bằng Bagging, các số liệu tổng hợp trùng nhau trong lần chạy không chứng minh hai mô hình tương đương. Nếu được hỏi có thể chẩn đoán không, trả lời chưa có kiểm định lâm sàng và thí nghiệm vẫn bỏ sót ca ác tính.

## Slide 26 — Cách tính chỉ số với ác tính là lớp dương

Dùng trang này khi cần giải thích cụ thể các con số. Quy ước dương là ác tính dù mã nhãn bằng 0. TP là ca ác được dự đoán ác; FN là ca ác bị dự đoán lành; FP là ca lành bị dự đoán ác; TN là ca lành được dự đoán lành. Tổng mẫu bằng 49 cộng 4 cộng 3 cộng 87 bằng 143. F1 là trung bình điều hòa của precision và recall, tương đương công thức hai TP chia hai TP cộng FP cộng FN. Balanced accuracy trung bình recall của hai lớp được dùng để chọn độ sâu trong CV, khác accuracy thường ở bảng test. Nếu mẫu test thiếu một lớp thì cần xem lại cách diễn giải; ở đây cả hai lớp đều có mặt.
