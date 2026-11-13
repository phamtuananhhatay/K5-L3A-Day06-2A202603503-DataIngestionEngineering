# Rà soát evidence dev và chốt cấu hình trước test

## Hai phần đã hoàn thành

1. Rà soát 15 câu dev × 3 strategy × top-3 = 135 chunk trong 45 trace, đối chiếu
   câu hỏi/đáp án/quote gốc và nội dung thực tế. Không chạy lại truy xuất, không đọc
   kết quả test. Chứng minh mỗi chunk khớp đúng lát cắt trang PDF gốc theo offsets.
2. Chọn C theo quy tắc dev đã chốt và lưu snapshot có hash để kiểm tra trước test.
   Không thay đổi model, query, filter, corpus, chunking hoặc nội dung questions.json.

**Người rà soát và xác nhận kết quả cuối cùng: học viên (tác giả bài lab).**
Ngày 2026-11-13, học viên thông báo đã tự rà soát và thu được kết quả giống phần
rà soát do Codex hỗ trợ trước đó. Bảng kết quả và các kết luận evidence dưới đây
được ghi nhận là **kết quả rà soát của học viên**, phù hợp với xác nhận này.

Codex hỗ trợ rà soát ban đầu, đối chiếu nguồn và tổng hợp báo cáo. Học viên xác nhận
kết quả sau khi đã có bản rà soát hỗ trợ; không mô tả đây là chấm mù hoặc chấm bởi
người đánh giá độc lập với tác giả. Xác nhận này thuộc phần evidence dev, chưa phải
nhãn audit coherence hoặc grounding của các bước sau.

## Chính sách evidence

Chấp nhận một chunk ở nguồn/trang hợp lệ có đầy đủ ý cần trả lời, kể cả bằng chứng
tương đương đã được ghi nhận. Giữ đủ đơn vị, thời gian, điều kiện và ngoại lệ. Có thể
bỏ câu dẫn thừa nếu chủ thể và nội dung vẫn xác định được từ chunk và câu hỏi rõ ràng.
Không ghép nhiều chunk để tính hit chính, không suy hit từ đúng trang hoặc score.
Chính sách lưu trong benchmark/evidence_policy.json và áp dụng nhất quán A/B/C.

Hai evidence được thêm **sau khi xem dev và trước test**, công khai trong
benchmark/dev_evidence_additions.json; đây là bổ sung cách chấm dev, không tuyên bố
chấm mù độc lập. Benchmark gốc và kết quả baseline không bị sửa hay ghi đè.

| Câu | Chứng cứ được chấp nhận | Kết luận thay đổi |
|---|---|---|
| q02, PDF 24 | Hai dòng Indicator 7.1.1 và 7.1.2, đủ tỷ lệ dân số có điện và sử dụng nhiên liệu/công nghệ sạch; không cần lặp câu dẫn Target 7.1 | B/C rank 1 từ miss thành hit |
| q15, PDF 61 | Đoạn bắt đầu “suggests that…” vẫn nêu SENELEC, rooftop solar, khoảng 4,5 triệu euro trong 20 năm, hoàn vốn 5 năm và tính ước tính | A rank 1 từ miss thành hit |

Đã đọc lại và xem ảnh render PDF 24 và 61 để xác minh thứ tự văn bản và ngữ cảnh.
Các evidence ngắn hơn đều là đoạn nguyên văn liên tục của trang gốc. Không thêm
nguồn giả hay dữ kiện mới. B/C q15 vốn đã hit, A q02 vẫn miss vì không một chunk
được lấy nào có trọn cả hai chỉ số.

## Những trường hợp giữ nguyên

- q01: A/C trả trang 65 nhưng chỉ đoạn dự án/technical assistance; thiếu cơ chế
  hai hồ khác cao độ, nước chảy qua turbine. B không lấy được đoạn cơ chế. Giữ miss.
- q03: các đoạn không có đủ 21 quốc gia và Nigeria/Liberia trong FY2021. Giữ miss.
- q07: A có bằng chứng từng phần qua hai chunk, nhưng không có một chunk đủ ba
  rào cản. B/C lấy khoản tài trợ hoặc header, không phải đoạn rào cản. Giữ miss.
- q08: có đoạn về lợi ích GDU nhưng không định nghĩa dùng nhiệt trực tiếp so với
  chuyển đổi thành điện. Giữ miss.
- q13: đoạn về ESRF, Data Hub hoặc testbed không trả lời ba nguồn lực của End User
  Subsidy Lab. Giữ miss.
- Các hit ban đầu đã đối chiếu với đầy đủ con số/điều kiện và vẫn được giữ.
  Mọi rank không hit có lý do theo câu trong review_decisions và chunk_review.jsonl.

## Kết quả sau rà soát

**Kết quả do học viên tự rà soát và xác nhận**, trùng với kết quả Codex hỗ trợ trước đó:

| Strategy | Hit@1 baseline → reviewed | Evidence Hit@3 baseline → reviewed | Filter tuân thủ |
|---|---|---|---|
| A | 5/15 → **6/15 (40,0%)** | 7/15 → **8/15 (53,3%)** | 3/6 |
| B | 7/15 → **8/15 (53,3%)** | 9/15 → **10/15 (66,7%)** | 3/6 |
| C | 8/15 → **9/15 (60,0%)** | 9/15 → **10/15 (66,7%)** | 6/6 |

C được chọn: hòa B về Hit@3 nhưng cao hơn Hit@1, đúng quy tắc lựa chọn ban đầu.
Không cần tie-break tài nguyên. Chỉ có 3 nhãn chunk thay đổi, từ 2 câu có evidence
bổ sung. Kết quả này không phải độ chính xác câu trả lời LLM hoặc kết luận tổng quát.

## Cấu hình đã chốt

- A: fixed-size 500 ký tự, overlap 50; 237 vector.
- B: paragraph/heading heuristic, tối đa 500 ký tự, không overlap; 270 vector.
- C: dùng chính vector B, chỉ áp dụng filter do câu hỏi/ngữ cảnh cung cấp trước.
- Model: intfloat/multilingual-e5-small, ONNX FP32 CPU, revision
  614241f622f53c4eeff9890bdc4f31cfecc418b3; 384 chiều, query/passage prefix
  theo embedding_config.json, masked mean pooling và chuẩn L2; không truncate âm thầm.
- Vector store: PostgreSQL + pgvector, public.day6_chunks; exact cosine top-3,
  filter trước xếp hạng, tie-break chunk_id. Không ANN, không reranker hoặc hybrid.
- Corpus 38 trang và benchmark gốc 15 dev/5 test giữ nguyên. Các bước review/dev
  không thay tham số để cải thiện điểm. Không chạy 5 câu test trong công việc này.

## File bàn giao và cách kiểm chứng

- benchmark/evidence_policy.json: tiêu chí ngữ nghĩa đã chốt.
- benchmark/dev_evidence_additions.json: hai evidence bổ sung và lý do.
- results/dev/review_decisions.json: quyết định tất cả 45 lượt.
- results/dev/reviewed/chunk_review.jsonl: 135 quyết định rank-level, nhãn trước/sau,
  nguồn, matched evidence và lý do; xác nhận lát cắt PDF.
- results/dev/reviewed/traces.jsonl, summary.json, comparison.md, selection.json:
  kết quả sau review, tách khỏi baseline.
- artifacts/frozen_pipeline.json: snapshot trước test, lựa chọn C, thông số và
  SHA-256 của 26 file cấu hình/code/dữ liệu/kết quả liên quan.

Các file JSON/JSONL và snapshot giữ nguyên thông tin reviewer ở thời điểm Codex
hỗ trợ tạo chúng để bảo toàn lịch sử và mã băm. Xác nhận rà soát sau đó của học viên
được ghi bổ sung trong báo cáo này; không ghi đè thông tin tác giả của các bản ghi cũ.
Do kết quả học viên trùng khớp, không thay nhãn, metric, cấu hình hoặc lựa chọn C.

Từ thư mục gốc repo, kiểm tra snapshot (không query hoặc inference):

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/freeze_configuration.py
```

Đã chạy: 26/26 file khớp hash. Script tạo snapshot chỉ dùng một lần với --create,
từ chối ghi đè. Những file đã hash không nên tạo lại/sửa sau chốt mà không ghi nhận
phiên bản. Việc kiểm tra hash giúp phát hiện thay đổi, không khóa quyền sửa file của hệ điều hành.

Bước tiếp theo là triển khai/chạy test theo snapshot này khi được yêu cầu. Nếu có
đánh giá bằng chứng tương đương trên test, dùng cùng chính sách, khai báo reviewer và
giữ nguyên trace; không chỉnh cấu hình hoặc chọn lại strategy từ kết quả test.
