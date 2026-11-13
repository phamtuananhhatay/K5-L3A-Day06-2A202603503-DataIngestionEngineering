# Coherence — kết quả chấm của học viên

Người chấm: **Phạm Tuấn Anh**. Ngày ghi nhận: 13/11/2026.

Điểm và lý do do học viên gửi trong chat. Codex chỉ ghi lại, đối chiếu mẫu và tính tổng; không thay điểm của học viên.

## Phương pháp và mẫu

Dùng cùng 10 vị trí nguồn đã chọn trước khi nhận điểm: 10 trang corpus đầu theo thứ tự tăng dần, anchor ở đoạn chính. Nếu có overlap, lấy chunk bao phủ anchor với start_char nhỏ nhất. Không đổi mẫu sau khi nhận điểm. C dùng cùng chunk B nên học viên cho cùng điểm.

Thang 0–2: 0 = khó hiểu do cắt ý/thiếu chủ thể; 1 = hiểu một phần, thiếu ngữ cảnh; 2 = tự hiểu được và giữ trọn ý. Mẫu nằm trong [coherence_samples_for_student.md](coherence_samples_for_student.md).

| Mẫu | PDF | A /2 | B /2 | C /2 | Lý do A của học viên | Lý do B/C của học viên |
|---|---:|---:|---:|---:|---|---|
| 01 | 23 | 1 | 2 | 2 | Giữ được hai câu đầu trọn vẹn nhưng câu thứ ba bị cắt giữa từ (to prepare chil), gây cụt ý. | Tách đúng ranh giới đoạn văn gồm hai câu hoàn chỉnh, rõ chủ thể và giữ trọn ý. |
| 02 | 24 | 1 | 2 | 2 | Nêu được định nghĩa SDG 7 và Indicator 7.1.1 nhưng bị cắt cụt ở cuối danh sách ngay sau Proportion of (mất nội dung Indicator 7.1.2 và các target còn lại). | Tách trọn đoạn mở đầu giới thiệu SDG 7, mục tiêu năm 2030 và tên Target 7.1 thành một khối mạch lạc, không bị cắt ngang câu. |
| 03 | 25 | 1 | 2 | 2 | Bắt đầu lửng lơ giữa câu (for electricity access...) vì thiếu vế đầu của câu ở trang trước, đồng thời phần giới thiệu RISE ở cuối bị cắt ngay sau RISE is the. | Bắt đầu đúng đầu câu định nghĩa RISE và kết thúc trọn vẹn đoạn văn mô tả chu kỳ xuất bản cùng nền tảng trực tuyến. |
| 04 | 27 | 1 | 2 | 2 | Giữ trọn câu đầu tiên nhưng câu thứ hai bị cắt ngang giữa cụm từ (in a Paris Agr). | Tách đúng một câu hoàn chỉnh mở đầu section, đầy đủ chủ thể và ý nghĩa. |
| 05 | 28 | 1 | 2 | 2 | Mở đầu bằng phần đuôi của câu từ trang trước (such technologies...), sau đó nêu trọn câu ví dụ ở Kenya và Niger nhưng câu thứ ba bị cắt cụt ở cuối (in collaboration w). | Tách đúng ranh giới đoạn nên vẫn còn phần đuôi câu trang trước ở đầu chunk, nhưng giữ trọn vẹn câu ví dụ về Kenya và Niger mà không bị cắt ngang từ. |
| 06 | 29 | 1 | 2 | 2 | Mở đầu bằng phần đuôi câu từ trang trước (for implementing...) và bị cắt ngang từ ở mục liệt kê thứ hai (regional trad), thiếu mục (3). | Bắt đầu đúng đầu câu chủ đề về chương trình MARCOT trong FY2021 và liệt kê trọn vẹn cả ba mục tiêu chiến lược. |
| 07 | 30 | 1 | 2 | 2 | Giữ trọn câu đầu về chương trình tại Sudan nhưng câu thứ hai bị cắt ngang từ ở cuối (deliver posi). | Tách trọn vẹn câu giới thiệu đầu tiên của hộp thông tin về Sudan, đầy đủ chủ thể, mốc thời gian và mục tiêu. |
| 08 | 31 | 1 | 2 | 2 | Giữ trọn đoạn văn về diễn đàn tri thức trực tuyến của ESRF nhưng dính thêm tiêu đề mục mới và một từ Coal rời rạc ở cuối. | Tách sạch toàn bộ đoạn văn về diễn đàn tri thức của ESRF, không dính chữ thừa từ tiêu đề tiếp theo. |
| 09 | 32 | 1 | 2 | 2 | Giữ trọn hai câu đầu nhưng câu thứ ba bị cắt lửng ở cuối (actions needed). | Tách trọn đoạn mở đầu gồm hai câu hoàn chỉnh về chương trình Gender and Energy của ESMAP. |
| 10 | 33 | 1 | 2 | 2 | Giữ trọn tiểu mục về bình đẳng giới trong thủy điện nhưng dính thêm tiêu đề bị cắt cụt của tiểu mục tiếp theo (IN THE OFF). | Tách trọn vẹn toàn bộ đoạn văn của tiểu mục Getting to Gender Equality in Hydropower, đứng độc lập và giữ trọn ý. |

## Tổng hợp

| Strategy | Mẫu | Điểm 0 | Điểm 1 | Điểm 2 | Tổng điểm | Trung bình /2 |
|---|---:|---:|---:|---:|---:|---:|
| A | 10 | 0 | 10 | 0 | 10 | 1.0 |
| B | 10 | 0 | 0 | 10 | 20 | 2.0 |
| C | 10 | 0 | 0 | 10 | 20 | 2.0 |

Trung bình = tổng điểm / 10. ID chunk đầy đủ, trang, offset và từng nhãn được lưu tại results/coherence/reviewed_samples.jsonl. Nhãn gốc của học viên ở results/coherence/student_scores.json.

## Nhận xét và giới hạn

Trên 10 mẫu này, học viên đánh giá B/C giữ ý tốt hơn A. A thường bị cắt giữa từ, thiếu đầu câu hoặc dính một phần heading tiếp theo. Điểm B/C giống nhau phản ánh dùng chung chunk, không phải hai bộ quan sát độc lập.

Điểm 2 của B/C là đánh giá của học viên trên mẫu đã chọn, không chứng minh toàn corpus không có lỗi. Riêng mẫu 05 vẫn giữ phần đuôi câu trang trước; học viên chấp nhận vì câu ví dụ chính đầy đủ. Một số chunk khác vẫn có header/footer. Chỉ lấy 10 trang đầu, chưa đại diện mọi section. Học viên là tác giả bài làm, đã thấy nội dung pipeline/dev và cách chia; không gọi đây là chấm mù độc lập.

Không dùng điểm coherence để chọn lại chiến lược sau test; cấu hình và lựa chọn C giữ nguyên.
