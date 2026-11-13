# Grounding test — kết quả chấm của học viên

Người chấm: **Phạm Tuấn Anh**. Ngày ghi nhận: 13/11/2026.

Điểm và lý do do học viên gửi qua chat; Codex chỉ ghi lại và tính tổng hợp. Một điểm cho cả bộ top-3. Học viên là tác giả bài làm, không phải người chấm độc lập/mù.

| Câu | A /2 | B /2 | C /2 | Lý do của học viên |
|---|---:|---:|---:|---|
| q16 | 2 | 2 | 2 | Cả 3 chiến lược đều có chunk (A ở rank 3, B và C ở rank 2) trích xuất nguyên văn đủ bốn sản phẩm bổ trợ của Energy Data and Analytics Hub (Tracking SDG 7, Multi-Tier Framework, RISE, Energy Demand Estimation) kèm đúng nguồn trang 23. |
| q17 | 1 | 0 | 0 | A có chunk rank 2 đúng trang 31 nhắc tới chủ đề chuyển dịch/tái sử dụng nhà máy than (coal plant repurposing) nhưng bị cắt trước đoạn liệt kê khung phân tích và ba phương án chuyển đổi công năng nên chỉ đạt 1 điểm. B và C hoàn toàn không truy xuất được trang 31 hay bất kỳ thông tin nào về tái sử dụng nhà máy than nên đạt 0 điểm. |
| q18 | 1 | 2 | 2 | A có chunk rank 2 đúng trang 41 và nêu đúng tên nghiên cứu đầu tiên tại Kazakhstan, nhưng bị cắt giữa câu trước phần giải thích nguyên nhân (trợ cấp nhiên liệu và quy trình cấp phép thuộc nhiều cơ quan) nên đạt 1 điểm. B và C đều có chunk rank 1 chứa trọn vẹn bằng chứng trả lời đủ cả hai ý và đúng section Accelerating Decarbonization nên đạt 2 điểm. |
| q19 | 1 | 0 | 0 | A có chunk rank 2 (trang 49) nhắc tên workstream (6) Financial Innovation for Electricity Access nhưng thiếu nội dung định hướng tài chính bổ sung và không cạnh tranh với thị trường tư nhân nên đạt 1 điểm. B và C không truy xuất được chunk nào liên quan đến sáng kiến này nên đạt 0 điểm. |
| q20 | 1 | 1 | 1 | Cả 3 chiến lược đều lấy được chunk rank 1 ở trang 62 đúng chủ thể dự án điện mặt trời nổi tại Tajikistan, nhưng đều thiếu điều kiện thứ tự thực hiện sau khi đánh giá kỹ thuật hoàn tất (A bị cắt ngay trước vế điều kiện once the technical assessment is completed, còn B và C chỉ chứa 2 câu đầu mô tả đánh giá kỹ thuật hiện tại) nên cùng đạt 1 điểm. |

## Tổng hợp

| Strategy | Điểm 0 | Điểm 1 | Điểm 2 | Tổng điểm | Trung bình /2 |
|---|---:|---:|---:|---:|---:|
| A | 0 | 4 | 1 | 6 | 1.2 |
| B | 2 | 1 | 2 | 5 | 1.0 |
| C | 2 | 1 | 2 | 5 | 1.0 |

Trung bình = tổng điểm / 5. Giữ nguyên các nhãn 1 của học viên cho bằng chứng một phần; không tự chuyển từ Hit@3 hoặc similarity sang điểm grounding.

Các điểm này đánh giá mức hỗ trợ của top-3, không phải độ chính xác câu trả lời LLM. Không chỉnh cấu hình hoặc chọn lại C theo test. Nguồn: [trace test](../results/test/traces.jsonl) và [báo cáo evidence của học viên](test_evidence_review_student.md).
