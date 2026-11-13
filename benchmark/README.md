# Benchmark ESMAP 2021 — nhiệm vụ 2

**Cập nhật sau rà soát dev, trước test:** câu hỏi/split/gold gốc trong questions.json
vẫn giữ nguyên. Hai evidence tương đương cho q02/q15 được ghi riêng ở
`dev_evidence_additions.json`, phương pháp ở `evidence_policy.json`. Đã áp dụng cùng
tiêu chí cho cả A/B/C và lưu kết quả riêng trong `../results/dev/reviewed/`.
Reviewer là Codex, không phải người chấm độc lập. Cấu hình trước test được chốt trong
`../artifacts/frozen_pipeline.json`; chưa chạy test.

Bộ benchmark v1 có 20 câu hỏi tiếng Việt, đáp án tiếng Việt và bằng chứng nguyên văn
tiếng Anh từ corpus ESMAP 2021. Evidence chỉ gộp khoảng trắng/xuống dòng, không dịch.
Nguồn và quyền sử dụng: [data/ATTRIBUTION.md](../data/ATTRIBUTION.md).

## Đọc file nào?

- [QUESTIONS_REVIEW.md](QUESTIONS_REVIEW.md): bản dễ đọc, có đủ 20 câu, đáp án, trang,
  filter, đoạn bằng chứng và ghi chú kiểm chứng.
- [questions.json](questions.json): bản dữ liệu chính cho pipeline.
- [manifest.json](manifest.json): bản cố định v1, mã SHA-256, danh sách dev/test,
  tiêu chí chọn cấu hình và giới hạn thí nghiệm.
- [../results/task2_validation.json](../results/task2_validation.json): kết quả kiểm tra,
  chưa phải kết quả retrieval.
- [../report/task2_benchmark_review.md](../report/task2_benchmark_review.md): báo cáo cách làm.

## Chia tập và câu có filter

| Tập | ID | Số câu | Có filter |
|---|---|---:|---:|
| Dev | q01–q15 | 15 | 6 |
| Test | q16–q20 | 5 | 2 |
| Tổng | | 20 | 8 |

Câu filter: q01, q02, q04, q07, q11, q12, q18, q20. Tất cả đều nêu trực tiếp
`Chỉ xét mục <section>` trong câu hỏi; filter là input biết trước, không suy ra từ gold.
Câu không có filter dùng JSON `null`.

`q01` giữ ý câu người học đã viết, thêm phạm vi Renewable Energy để filter có căn cứ.
Các câu còn lại do Codex hỗ trợ soạn và đối chiếu nguồn; người học cần hiểu và kiểm tra
trước khi giải thích bài làm. Không ghi nhận đây là đánh giá độc lập của con người.

Chọn 20 trang gold khác nhau. Dev/test không dùng chung trang gold. Vẫn có liên hệ
chủ đề và từ vựng giữa hai tập vì cùng một báo cáo: ví dụ q16 liệt kê sản phẩm của Hub,
trong khi q02/q03 hỏi chi tiết liên quan. Không coi đây là tách độc lập theo tài liệu.
Việc đọc câu hỏi/đáp án test để soạn và xác minh dữ liệu không phải xem kết quả retrieval.
Chưa có kết quả truy xuất dùng để điều chỉnh bộ test hoặc cấu hình.

## Hợp đồng cho pipeline tương lai

1. Dùng cùng `questions.json` và corpus cho A/B/C, cùng model/store/metric cosine.
2. Chỉ gửi `question` làm query. A/B không áp dụng filter. C chỉ áp dụng `filter` nếu
   khác `null`; với câu không filter, C tìm không filter.
3. Không thêm `expected_answer`, `gold_source_id`, `gold_page`, `evidence_quote`,
   `verification_note` hoặc danh sách alternative vào query/filter.
4. Số trang là trang PDF vật lý bắt đầu từ 1; trang in trong phạm vi chọn bằng PDF trừ 8.
5. Đánh giá hit bằng nguồn/trang hợp lệ **và đủ evidence**, không chỉ đúng trang.
6. Chấp nhận mọi alternative gold đã ghi. Quét toàn corpus không tìm thêm bản sao
   nguyên văn của các quote v1; bằng chứng diễn đạt tương đương vẫn có thể tồn tại.
   Nếu phát hiện, kiểm chứng và ghi bổ sung nhất quán cho cả ba cấu hình; không chỉnh
   nội dung câu test để làm đẹp điểm. Nếu phát hiện sau khi xem kết quả, khai báo rõ.
7. Không suy nhãn coherence/grounding thủ công từ exact string match.

## Tiêu chí chọn cấu hình, chốt trước test

Chọn bằng dev: ưu tiên Evidence Hit@3 cao hơn, sau đó Hit@1 cao hơn. Nếu bằng điểm,
ưu tiên thời gian ingest thấp hơn (đo cùng máy và điều kiện), rồi chi phí dịch vụ trả phí
thấp hơn. Nếu tất cả bằng nhau, dùng thứ tự A, B, C để quyết định xác định được.
Vẫn báo cáo coherence, grounding, metadata, số chunk và các đánh đổi trong bài cuối.

Cố định cấu hình trước khi chạy test; đánh giá cả A/B/C trên test để báo cáo, không
dùng test để chọn lại cấu hình hoặc chỉnh tham số. Nếu chỉnh sau khi xem kết quả test,
ghi nhận rằng test đã được dùng để phát triển và không còn là holdout độc lập.

## Kiểm chứng

Từ thư mục gốc repo:

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/validate_benchmark.py
```

Cần PDF gốc tại đường dẫn trong `data/manifest.json`. Script kiểm tra trường bắt buộc,
ID, split, filter, nguồn/trang, evidence trong cả PDF và JSONL, mã băm snapshot và
trang gold không trùng dev/test. Kết quả lưu vào `results/task2_validation.json`.

Kiểm tra chuỗi chứng minh evidence có trong nguồn; nó không tự chứng minh đáp án
đúng về ngữ nghĩa. Phần đó được đối chiếu khi soạn và ghi trong `verification_note`.
Benchmark nhỏ, dùng một báo cáo, người soạn và người kiểm tra không độc lập, truy vấn
tiếng Việt trên văn bản tiếng Anh; cần nêu các giới hạn này khi diễn giải kết quả.

Nếu sửa câu hỏi/corpus sau khi chốt, validator sẽ báo sai mã băm. Trước thử nghiệm,
có thể sửa lỗi rồi tạo phiên bản snapshot mới có giải thích; không tự cập nhật mã băm
để che việc thay đổi test sau khi đã dùng kết quả. Bản Markdown là bản đọc của JSON;
nếu sửa dữ liệu phải đồng bộ cả hai.
