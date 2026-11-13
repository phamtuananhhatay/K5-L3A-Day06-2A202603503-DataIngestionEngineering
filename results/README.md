# Danh mục kết quả để chấm bài

| Nội dung | Kết quả chính | Minh chứng chi tiết |
|---|---|---|
| Corpus | task1_audit.json | task1_source_verification.json, ingestion_check.json, ingestion.log |
| Benchmark | task2_validation.json | ../benchmark/questions.json và manifest.json |
| Chunking | chunking/summary.json | chunks_A.jsonl, chunks_B.jsonl, page65_comparison.md |
| Embedding thật | embeddings/summary.json | vectors_A.npz, vectors_B.npz, embedding.log |
| Lưu pgvector | storage_check.json | 507 bản ghi, nạp lại không trùng, loại chunk cũ |
| Tìm kiếm thử | search/check_summary.json | smoke_traces.json, example_C.json |
| Dev baseline | dev/summary.json | dev/traces.jsonl, comparison.md, run.log |
| Dev sau review | dev/reviewed/summary.json | reviewed/traces.jsonl, chunk_review.jsonl, review_decisions.json |
| Test lần đầu | test/summary.json | test/traces.jsonl, pretest_verification.json, validation.json, run.log |
| Test học viên rà soát | test/student_review/summary.json | chunk_reviews.jsonl; nhãn khớp baseline |
| Metadata | test/student_review/metadata_audit.json | 45 bản ghi nguồn/trang/section |
| Grounding | test/student_review/grounding_summary.json | grounding_scores.json, điểm/lý do do học viên gửi |
| Coherence | coherence/summary.json | student_scores.json, reviewed_samples.jsonl, samples.json |

Baseline giữ nguyên lịch sử. Dev sau rà soát và test học viên xác nhận dùng trong
bảng kết quả cuối; không cộng trùng hoặc thay kết quả tự động thành nhãn thủ công.
Các trường `test_executed=false`/`scores_exist=false` trong snapshot cũ mô tả thời
điểm tạo snapshot, không phải trạng thái toàn bài hiện tại. Xem báo cáo cuối để biết
trình tự thực hiện. Grounding/metadata/coherence ghi Phạm Tuấn Anh là người chấm.

Các file NPZ chứa vector float32 và chunk_ids, không cần pickle khi đọc. PDF gốc,
model và database volume không đóng gói; link tải/hash/lệnh dựng lại ở README và
data/README.md. Nội dung text trích từ báo cáo có attribution ở data/ATTRIBUTION.md.
