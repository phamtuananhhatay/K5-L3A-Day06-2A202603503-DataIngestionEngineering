# Báo cáo nhiệm vụ 2: bộ câu hỏi và gold evidence

Ngày chuẩn bị: 2026-11-13 (Asia/Saigon). Phiên bản: `esmap-benchmark-v1`.

## Kết quả

Hoàn thành dữ liệu benchmark tối thiểu: 20 câu, 15 dev/5 test, 8 câu có filter
(6 dev/2 test), đủ thông tin bắt buộc và evidence đã đối chiếu với nguồn.
Chưa chạy retrieval, chưa tạo Hit@1/Hit@3 hoặc nhãn coherence/grounding.

| Mục nguồn | Dev | Test | Tổng |
|---|---:|---:|---:|
| Energy Data | 2 | 1 | 3 |
| Foundations of Energy Transition | 3 | 1 | 4 |
| Accelerating Decarbonization | 3 | 1 | 4 |
| Clean Cooking | 2 | 0 | 2 |
| Electricity Access | 3 | 1 | 4 |
| Renewable Energy | 2 | 1 | 3 |
| **Tổng** | **15** | **5** | **20** |

## Đã làm như thế nào

1. Đọc lại BENCHMARK.md và corpus 38 trang đã chọn. Không lấy thông tin ngoài corpus
   để làm đáp án bắt buộc; mốc thời gian trong câu hỏi được giới hạn theo báo cáo 2021.
2. Giữ câu q01 về cơ chế phát điện thủy điện tích năng của người học. Thêm `Chỉ xét mục
   Renewable Energy` để filter xuất phát từ yêu cầu trước truy xuất. Không mở rộng
   câu hỏi sang chu trình bơm nước vì đoạn evidence không mô tả bước đó.
3. Soạn q02–q20 từ các đoạn văn cụ thể. Có câu trực tiếp, diễn đạt lại, cơ chế và
   điều kiện/ngoại lệ. Giữ các yếu tố dễ sai như EAP bị loại trừ, USD/euro, thời hạn
   20 năm, điều kiện 40% và việc chờ hoàn tất đánh giá kỹ thuật.
4. Lấy evidence nguyên văn từ trang chuẩn hóa, chỉ gộp khoảng trắng. Mỗi câu có
   `id`, `split`, `question`, `expected_answer`, `gold_source_id`, `gold_page`,
   `evidence_quote`, `filter`; thêm provenance của filter và ghi chú kiểm chứng.
5. Đối chiếu câu hỏi/đáp án với từng quote khi soạn. Đáp án là diễn giải tiếng Việt
   của bằng chứng tiếng Anh, không lấy kiến thức bên ngoài thay cho bằng chứng.
6. Chia q01–q15 dev, q16–q20 test trước khi chạy bất kỳ truy xuất nào trong nhiệm vụ này.
   Dùng 20 trang gold khác nhau để tránh lặp trang giữa hai tập. Có 5/6 nhóm nội dung
   trong test; Clean Cooking chưa có test, là hạn chế độ phủ được khai báo.
7. Ghi rõ phạm vi section trong tám câu filter. Những câu còn lại có `filter: null`.
   Mọi giá trị section đều có thật trong metadata corpus.
8. Quét toàn bộ corpus tìm evidence trùng nguyên văn ở các trang khác; không thấy
   bản sao nào của các quote đã chọn. Trường `alternative_gold_evidence` hiện rỗng.
   Không khẳng định đã tìm hết bằng chứng tương đương về ngữ nghĩa.
9. Viết validator kiểm tra lại evidence trên cả JSONL và PDF gốc, cùng checksum file,
   số câu, ID, split và tính hợp lệ của filter. Kiểm tra toàn bộ 20 câu đều pass.
10. Lưu SHA-256 của questions/corpus/PDF và split trong benchmark/manifest.json,
    cùng tiêu chí chọn cấu hình trước khi đánh giá test.

## Danh sách câu hỏi

| ID | Tập | PDF | Nội dung | Filter |
|---|---|---:|---|---|
| q01 | dev | 65 | Cơ chế phát điện thủy điện tích năng | Renewable Energy |
| q02 | dev | 24 | Hai chỉ số Target 7.1 | Energy Data |
| q03 | dev | 25 | Số nước MTF và báo cáo FY2021 | Không |
| q04 | dev | 29 | Số hoạt động MARCOT và ngoại lệ EAP | Foundations of Energy Transition |
| q05 | dev | 30 | Mốc cải cách trợ cấp xăng/diesel Sudan | Không |
| q06 | dev | 32 | Ba khía cạnh cải thiện bình đẳng giới | Không |
| q07 | dev | 38 | Rào cản chuỗi lạnh Bangladesh | Accelerating Decarbonization |
| q08 | dev | 40 | Định nghĩa sử dụng trực tiếp địa nhiệt | Không |
| q09 | dev | 43 | Tiết kiệm và điều kiện giảm CO2 ở Mexico | Không |
| q10 | dev | 46 | Sáu module nâng cao về nấu ăn sạch | Không |
| q11 | dev | 47 | Hai yếu tố quyết định mức trợ cấp RBF Rwanda | Clean Cooking |
| q12 | dev | 50 | Kịch bản GEP và hai mốc năm | Electricity Access |
| q13 | dev | 52 | Nguồn lực tập hợp bởi End User Subsidy Lab | Không |
| q14 | dev | 54 | Hệ thống điện/nước tại Haiti | Không |
| q15 | dev | 61 | Ước tính tiết kiệm, thời hạn và hoàn vốn Senegal | Không |
| q16 | test | 23 | Bốn sản phẩm của Data and Analytics Hub | Không |
| q17 | test | 31 | Ba công năng tái sử dụng nhà máy than | Không |
| q18 | test | 41 | Hai rào cản nhiệt địa nhiệt tại Kazakhstan | Accelerating Decarbonization |
| q19 | test | 55 | Tài chính bổ sung trong quan hệ thị trường tư nhân | Không |
| q20 | test | 62 | Điều kiện thực hiện bước môi trường/xã hội và tài chính tại Tajikistan | Renewable Energy |

## Kết quả kiểm chứng tự động

- 20/20 câu có evidence trong trang corpus được chỉ định.
- 20/20 câu có evidence trong trang PDF gốc được chỉ định.
- 15 dev, 5 test; 8 câu có filter, gồm 2 câu test.
- Không trùng ID, không trùng toàn bộ câu hỏi, không trùng trang gold giữa dev/test.
- Nguồn, section và checksum khớp snapshot; không có lỗi validator.

Đối chiếu ngữ nghĩa được thực hiện trong quá trình soạn bằng Codex, không phải
nhãn chấm độc lập do người học hoặc chuyên gia đã xác nhận. Người học nên đọc bản
QUESTIONS_REVIEW.md để hiểu và kiểm tra trước khi chạy thí nghiệm.

## Tiêu chí lựa chọn đã chốt

Dùng dev để chọn: Evidence Hit@3 cao hơn, tiếp theo Hit@1 cao hơn, thời gian ingest
thấp hơn, chi phí dịch vụ trả phí thấp hơn; nếu còn bằng nhau chọn thứ tự A/B/C.
Đo tài nguyên cùng máy và điều kiện. Sau khi cố định cấu hình mới đánh giá cả ba
trên test; không chọn lại hoặc tinh chỉnh theo test. Vẫn đánh giá đủ năm khía cạnh
của lab ở các bước sau, không dùng tiêu chí này thay audit thủ công.

## Giới hạn và tính trung thực

- Chỉ một báo cáo và năm câu test; không đại diện cho mọi tài liệu năng lượng.
- Chia tách theo trang gold, chưa độc lập theo tài liệu/chủ đề. q16 còn liên quan
  hệ sinh thái dữ liệu được hỏi ở dev. Test chưa có câu thuộc Clean Cooking.
- Tác giả câu hỏi đã đọc toàn bộ gold để xây bộ kiểm tra. Chưa dùng kết quả test
  để điều chỉnh hệ thống. Nếu dùng kết quả test để sửa sau này phải khai báo.
- Truy vấn tiếng Việt, nguồn tiếng Anh; kết quả phụ thuộc năng lực đa ngữ của model.
- Matching chuỗi không chứng minh đúng ngữ nghĩa. Khi chấm retrieval cần chấp nhận
  bằng chứng tương đương đã xác minh, dùng cùng cách chấm cho A/B/C.
- Không biến gold thành input truy xuất. Chỉ `question` và filter hợp lệ được dùng;
  các câu có filter cũng phải chạy không filter trong A/B theo thiết kế so sánh.
- AI được dùng để soạn dữ liệu và validator; không tạo số đo hoặc nhãn đánh giá giả.

## Chạy lại kiểm chứng

Từ thư mục gốc repo:

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/validate_benchmark.py
```

Đầu ra: results/task2_validation.json. Cần giữ nguyên PDF, corpus và snapshot v1.
Các hàm TODO của pipeline trong starter/src/ không được sửa trong nhiệm vụ này.
