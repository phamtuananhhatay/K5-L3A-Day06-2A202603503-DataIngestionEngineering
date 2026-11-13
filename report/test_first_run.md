# Lần chạy test đầu tiên sau khi chốt cấu hình

**Cập nhật sau chạy:** Phạm Tuấn Anh đã gửi bản rà soát đầy đủ 15 lượt/45 chunk,
ngày 13/11/2026. Nhãn đủ/không đủ của học viên khớp baseline, nên điểm giữ nguyên.
Xem [báo cáo rà soát của học viên](test_evidence_review_student.md) và
`results/test/student_review/summary.json`. Các mục “chưa rà soát” bên dưới mô tả
thời điểm lưu kết quả tự động đầu tiên, không phải trạng thái hiện tại. Audit
coherence, metadata và grounding theo thang điểm của lab vẫn còn cần thực hiện.

Thời điểm hoàn tất: 2026-11-13 18:33:04 Asia/Saigon (11:33:04 UTC).
Được thực hiện sau yêu cầu của học viên và sau snapshot pipeline-pretest-v1.

## Phạm vi và bảo toàn cấu hình

- Kiểm tra 26 file trong snapshot trước khi tạo query đầu tiên: pass.
- Chạy q16–q20, mỗi câu cho A/B/C: 15 trace, 45 chunk top-3.
- Mỗi câu dùng cùng query vector cho cả ba chiến lược. A/B không filter, C áp dụng
  filter đã có trong câu hỏi. Không truyền expected_answer/gold/evidence vào query.
- Model, corpus, chunking, vector, SQL search và evaluator đã chốt không đổi.
  Chỉ mở rộng runner để cho phép `--split test`, kiểm tra snapshot và ghi kết quả riêng.
- Giữ nguyên C là lựa chọn từ dev; không chọn lại hoặc chỉnh tham số bằng kết quả test.
- Cơ sở dữ liệu chỉ được đọc, không nạp lại model/vector hay sửa benchmark.

## Kết quả tự động ban đầu

| Strategy | Hit@1 | Evidence Hit@3 | Top-3 khớp filter yêu cầu |
|---|---|---|---|
| A | 0/5 (0%) | 1/5 (20%) | 1/2 |
| B | 1/5 (20%) | 2/5 (40%) | 1/2 |
| C | 1/5 (20%) | 2/5 (40%) | 2/2 |

Đây là matching tự động bảo thủ: một chunk đúng nguồn/trang phải chứa toàn bộ
quote đã ghi hoặc alternative đã được benchmark ghi nhận. Không ghép nhiều chunk
để tính hit chính. Chưa rà soát ngữ nghĩa tương đương và chưa chấm grounding/coherence
thủ công của test. Không so sánh trực tiếp baseline test này với dev đã bổ sung
evidence tương đương mà không nêu khác biệt về mức rà soát.

A/B không áp dụng filter, nên cột cuối chỉ đo mức khớp phạm vi câu hỏi yêu cầu.
Với 5 câu test, mỗi câu tương ứng 20 điểm phần trăm; kết quả không cho phép suy rộng
chiến lược tốt nhất tổng quát. Điểm similarity không phải xác suất trả lời đúng.
Phí dịch vụ API 0 USD, không gồm điện/phần cứng/mạng.

## Đầu ra

- results/test/pretest_verification.json: thời điểm kiểm tra, hash snapshot và C đã chọn.
- results/test/traces.jsonl: query, applied/requested filter, text/ID/score/metadata,
  gold và nhãn tự động của từng lượt.
- results/test/summary.json và comparison.md: metric tổng hợp và từng câu.
- results/test/manual_review_queue.json: các lượt không hit theo matching ban đầu.
- results/test/run.log: tiến độ q16–q20.
- results/test/validation.json: kiểm tra số trace, split, filter và metric sau chạy.

Lệnh đã dùng từ starter/:

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 -m src.run --split test
```

Runner từ chối ghi đè khi results/test/summary.json đã tồn tại, để bảo toàn lần
đánh giá holdout đầu tiên. Không xóa kết quả này để chạy lại như một test chưa từng xem.
Rà soát test tiếp theo phải theo evidence_policy.json đã chốt, ghi reviewer và giữ
baseline; không sửa cấu hình hoặc lựa chọn strategy theo kết quả đó.
