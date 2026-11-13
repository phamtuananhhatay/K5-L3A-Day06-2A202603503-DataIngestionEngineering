# Đánh giá tự động và chạy dev A/B/C

**Ghi chú phiên bản:** các số liệu dưới đây là baseline matching toàn quote ban đầu,
được giữ nguyên để kiểm toán. Kết quả sau rà soát evidence và chốt cấu hình xem
`dev_evidence_review_and_freeze.md` và `../results/dev/reviewed/comparison.md`.

## Phạm vi đã hoàn thành

Triển khai evaluation.py, runner src/run.py và phân tích chẩn đoán dev.
Chạy 15 câu q01–q15, mỗi câu cho A/B/C: 45 lượt, mỗi lượt top-3 (135 bản ghi chunk).
Không chạy q16–q20, không dùng kết quả test để sửa cấu hình. Không thay corpus,
benchmark, chunking, model hoặc database trong lần đánh giá này.

## Cách chấm

Hit@1: chunk hạng 1 đúng source/page và chứa toàn bộ quote evidence đã ghi.
Evidence Hit@3: có ít nhất một chunk trong top-3 đáp ứng điều kiện đó.
NFC và khoảng trắng được chuẩn hóa, không sửa dấu câu, không tự ghép nhiều chunk.
Alternative gold đã ghi cũng được chấp nhận. Báo số đúng/tổng câu, không chỉ tỷ lệ.

Đây là **kết quả tự động theo quote nguyên văn, chưa phải chấm tương đương ngữ nghĩa
hoàn chỉnh**. Quote có thể chứa phần ngữ cảnh dài hơn yêu cầu tối thiểu; chunk có
bằng chứng tương đương vẫn có thể bị đánh trượt. Các trường hợp này cần người đọc
xác minh và ghi nhận nhất quán cho A/B/C, không tự thay nhãn bằng similarity hoặc
đúng trang. Chưa thực hiện audit coherence/metadata/grounding thủ công của toàn lab.

## Kết quả thực chạy

| Strategy | Hit@1 | Evidence Hit@3 | Top-3 khớp filter câu hỏi yêu cầu |
|---|---|---|---|
| A | 5/15 (33,3%) | 7/15 (46,7%) | 3/6 |
| B | 7/15 (46,7%) | 9/15 (60,0%) | 3/6 |
| C | 8/15 (53,3%) | 9/15 (60,0%) | 6/6 |

A/B không áp dụng filter, nên cột cuối mô tả mức tuân thủ phạm vi được yêu cầu,
không khẳng định A/B có bật filter. C áp dụng filter và đạt 6/6 trên dev.
Chi phí dịch vụ 0 USD vì embedding local; không gồm điện/phần cứng/mạng.

Theo tiêu chí đã chốt (dev Hit@3, tiếp theo Hit@1), **C được chọn trong kết quả tự động
hiện tại**. B/C hòa Hit@3 nhưng C hơn Hit@1, không cần dùng tie-break tài nguyên.
Lựa chọn này có giới hạn do matching bảo thủ, một corpus và mẫu dev nhỏ; không
khẳng định C tốt nhất tổng quát hoặc coi kết quả dev là đánh giá độc lập.

## Phân tích lỗi tự động

| Loại trường hợp | A | B | C |
|---|---:|---:|---:|
| Có hit trong top-3 | 7 | 9 | 9 |
| Có chunk chứa đủ quote trong index nhưng top-3 không lấy được | 5 | 5 | 5 |
| Không có chunk đủ toàn bộ quote trong phạm vi hợp lệ | 3 | 1 | 1 |

Đối chiếu toàn index chỉ dùng dev/gold sau retrieval để chẩn đoán; không đổi query,
filter hay nhãn hit, không chạy thêm tìm kiếm. Các trường hợp quote không nằm trọn
chunk: q02 ở A/B/C; q07 và q15 ở A. Các số trên vẫn có thể đánh giá thấp bằng chứng
tương đương, không thay thế audit ngữ nghĩa.

Ví dụ:

- q02, PDF 24: cả A/B/C đều trả được trang 24 nhưng không chunk nào chứa toàn bộ
  evidence đã ghi. Đúng trang không đủ để chấm hit. Cần đọc các phần được chia và
  kiểm tra evidence tương đương, không tự đổi sang ghép chunk cho metric chính.
- q15, PDF 61: A trả trang 61 nhưng quote bị cắt theo ranh giới; B/C chứa đủ và hit@1.
  Đây là ví dụ cấu trúc chunk có ảnh hưởng ở corpus này.
- q01, PDF 65: C có trả trang 65 nhưng chunk được xếp hạng không chứa đủ quote cơ chế
  phát điện. Một chunk khác trong index có quote đầy đủ; trường hợp này thuộc lỗi
  lấy đúng đoạn, không thể suy hit từ số trang.
- q11, PDF 47: A hit trong top-3 nhưng không ở top-1; B/C đưa chunk đủ quote lên top-1.

## Kiểm tra và tái lập

6 unittest evaluation pass: Unicode/whitespace, đúng nguồn/trang và đủ evidence,
alternative gold, giới hạn top-3, tổng hợp tử/mẫu/N/A và chống đếm lặp,
filter compliance (không mặc định pass khi kết quả rỗng).
Runner xác nhận snapshot thực tế database trước khi truy xuất. Cùng câu hỏi dùng
chung vector cho A/B/C. Không đưa answer, gold page/source hoặc quote vào query.
analyze_dev.py đối chiếu số trace, ID, metric và ghi hash cấu hình trong selection.json.

Từ thư mục starter/:

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 -m src.run --split dev
.\.venv\Scripts\python.exe -X utf8 scripts/analyze_dev.py
```

Output trong results/dev/: comparison.md, traces.jsonl, summary.json, run.log,
manual_review_queue.json, failure_analysis.json, selection.json. Trace có query,
filter yêu cầu/áp dụng, text/ID/score/metadata top-3, gold và nhãn tự động từng chunk.
Không có nhãn thủ công giả; người chấm độc lập chưa tham gia.

benchmark/manifest.json giữ nguyên snapshot chuẩn bị ban đầu; trường retrieval_executed=false
trong file đó mô tả thời điểm chốt dữ liệu. Lần chạy dev thực tế được ghi ở
results/dev/summary.json, không sửa snapshot để tránh che lịch sử benchmark.
