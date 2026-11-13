# Báo cáo cá nhân — Day 06: Data Ingestion Engineering

**Học viên:** Phạm Tuấn Anh · **MSSV:** 2A202603503 · **Lớp:** L3A

**Ngày thực hiện/đánh giá:** 13/11/2026

**Repo:** https://github.com/phamtuananhhatay/K5-L3A-Day06-2A202603503-DataIngestionEngineering

## 1. Mục tiêu và dữ liệu

Tôi xây pipeline truy xuất bằng chứng từ tài liệu, so sánh chunk kích thước cố định
(A), chunk theo cấu trúc văn bản (B), và B có metadata filter khi câu hỏi yêu cầu (C).
Mục tiêu là tìm đoạn đủ bằng chứng và truy về nguồn, chưa xây chatbot sinh câu trả lời.

Corpus là *Energy Sector Management Assistance Program (ESMAP). 2021. Annual Report
2021. Washington, DC: World Bank.* Đây là báo cáo thường niên có nội dung kỹ thuật và
chính sách năng lượng, thuộc loại dữ liệu được đề lab cho phép.
[Nguồn chính thức](https://documents.worldbank.org/en/publication/documents-reports/documentdetail/615511640189474271).

PDF có 82 trang vật lý, chọn 38 trang nội dung: **23–25, 27–35, 37–43, 45–47,
49–55, 57–65**. Sáu section: Energy Data; Foundations of Energy Transition;
Accelerating Decarbonization; Clean Cooking; Electricity Access; Renewable Energy.
Không tính bìa, mục lục, trang mở đầu thiên về hình, trang không có text và các phần
ngoài phạm vi chủ đề như tài chính. Không khẳng định mọi trang bị loại đều không hợp lệ.
Đánh số PDF từ 1; trang in Ả Rập trong phạm vi chọn bằng trang PDF trừ 8.

Quyền sử dụng được ghi ở PDF 2: CC BY 3.0 IGO, kèm ngoại lệ cho ảnh/thành phần bên
thứ ba. Tôi chỉ dùng text, ghi nguồn và adaptation; PDF gốc/model lớn không đưa vào
Git. Người chấm có link tải và SHA-256 trong [manifest](../../data/manifest.json),
[hướng dẫn dữ liệu](../../data/README.md) và [attribution](../../data/ATTRIBUTION.md).
File người học cung cấp trùng SHA-256 với PDF tải trực tiếp từ World Bank.

## 2. Đọc, chuẩn hóa và lưu trữ

Python 3.11.9 và pypdf 6.21.4 đọc theo trang; chuẩn hóa Unicode NFC, khoảng trắng
ngang và dòng trống, giữ nguồn/trang và log lỗi. 38 trang có **99.118 ký tự**, không
có lỗi trích xuất, không có trang trùng text sau chuẩn hóa. PDF 82 không có text và
đã bị loại; không cần OCR cho các trang được chọn. Còn header/footer, từ ngắt dòng
và nhãn biểu đồ; không sửa chúng sau khi đã chốt corpus. Text hai cột có thể mất
ranh giới đoạn nên chunking B dùng heuristic, không khẳng định khôi phục bố cục PDF.

Embedding thật chạy local bằng **intfloat/multilingual-e5-small**, ONNX FP32 CPU,
revision `614241f622f53c4eeff9890bdc4f31cfecc418b3`, vector **384 chiều**. Prefix
`passage: ` cho document, `query: ` cho query; masked mean pooling và chuẩn L2 theo
[model card](https://huggingface.co/intfloat/multilingual-e5-small). Giới hạn 512 token
gồm prefix/token đặc biệt, vượt giới hạn báo lỗi thay vì cắt âm thầm. Batch 8,
4 CPU threads; NumPy 2.4.6, ONNX Runtime 1.31.1, tokenizers 0.23.3. File model và
tokenizer được kiểm SHA-256. Không API key, không mock fallback.

PostgreSQL **16.16** + pgvector **0.8.7** chạy Docker trong Ubuntu WSL 2; Windows
Python kết nối `127.0.0.1:55433`, database `day6_lab`, bảng `public.day6_chunks`.
Dữ liệu bền vững trong Docker volume. Tìm **exact cosine top-3**, filter trước xếp
hạng, sắp distance tăng dần rồi chunk_id; score = 1 - cosine distance. Không ANN,
reranker hoặc hybrid. Chi phí dịch vụ **0 USD**, không bao gồm điện/mạng/phần cứng.

Mỗi chunk giữ `document_id`, `source`, `page`, `metadata.section`, `report_year`,
offset `start_char/end_char`, tham số chunking và model. Section string lấy từ mục lục
và khoảng trang đã kiểm chứng; năm integer 2021 từ báo cáo. Section có sáu giá trị
phân biệt; source/page dùng truy nguồn. Không tự suy metadata từ đáp án gold.

ID chunk được tạo ổn định từ nguồn/trang/text/offset/cấu hình. Upsert nhận snapshot
đầy đủ theo document và strategy, cập nhật rồi xóa chunk cũ trong cùng transaction;
không nạp từng phần document. Nạp lại A/B vẫn 237/270 bản ghi; roundtrip text,
metadata/vector khớp, thử thu nhỏ snapshot loại đúng chunk cũ và đã dọn dữ liệu thử.
Sai chiều bị từ chối. Có 507 bản ghi A/B; C dùng lại B, không nhập vector trùng.

## 3. Cấu hình và benchmark

| Strategy | Chunking | Giới hạn | Overlap | Filter |
|---|---|---:|---:|---|
| A | Cửa sổ ký tự cố định, không vượt trang | 500 ký tự | 50 | Không |
| B | Dòng trống/heading chữ hoa; đoạn dài ưu tiên ngắt câu, rồi từ, cuối cùng ngắt cứng | 500 ký tự | 0 | Không |
| C | Dùng nguyên chunk/vector B | 500 ký tự | 0 | Khi câu hỏi cung cấp |

A–B thay chiến lược chunking (gồm cách ngắt và overlap); **B–C chỉ thay filter**.
Corpus, model/revision, tokenizer, prefix, vector store, metric, top-k và câu hỏi
giữ nguyên. Câu không filter thì C cho kết quả giống B.

Benchmark có 20 câu tiếng Việt và evidence tiếng Anh: q01–q15 dev, q16–q20 test,
chốt trước retrieval; 8 câu filter, gồm 2 câu test. Mỗi câu có đáp án, nguồn/trang và
quote đã kiểm chứng trong PDF/corpus. Gold chỉ dùng chấm sau retrieval; query chỉ
nhận question, C thêm filter đầu vào. Không hỏi ngoài corpus cho metric bắt buộc.
Dev/test có trang gold khác nhau nhưng cùng báo cáo và có chủ đề gần nhau; test
không bao phủ Clean Cooking. Đây không phải chia độc lập theo tài liệu.

Tiêu chí chọn trước test: dev Evidence Hit@3 cao nhất, rồi Hit@1; nếu vẫn hòa mới
so thời gian ingest, chi phí, cuối cùng thứ tự A/B/C. Dev đã được rà soát và tôi xác
nhận kết quả. **C được chọn trước test**: hòa B về Hit@3 nhưng Hit@1 cao hơn.
[Snapshot trước test](../../artifacts/frozen_pipeline.json) ghi hash 26 file, model,
tham số và chính sách evidence. Kiểm tra pass trước khi query test; không chọn lại C.

Matching ban đầu yêu cầu toàn quote trong một chunk đúng nguồn/trang. Sau xem dev,
đã công khai nhận hai quote ngắn hơn cho q02/q15 nhưng vẫn đủ mọi ý/điều kiện theo
[chính sách](../../benchmark/evidence_policy.json). Áp dụng cùng A/B/C, giữ baseline.
Tôi đã tự rà soát và xác nhận kết quả dev sau phần hỗ trợ của Codex. Test được chạy
một lần theo cấu hình đã chốt; tôi rà soát đủ 15 lượt/45 chunk, nhãn hit khớp baseline,
không thêm evidence tương đương test, không sửa tham số. Không ghép nhiều chunk để
tính hit chính. Đây là quy trình có công khai lịch sử, không tuyên bố chấm mù độc lập.

## 4. Kết quả retrieval

Hit@1 = số câu có chunk đầu đủ evidence / tổng câu. Evidence Hit@3 = số câu có ít
nhất một chunk đủ evidence trong top-3 / tổng câu. Đúng trang hoặc score cao chưa đủ.

| Strategy | Split/phương pháp | Hit@1 | Evidence Hit@3 | Số chunk |
|---|---|---|---|---:|
| A | Dev sau rà soát | 6/15 (40,0%) | 8/15 (53,3%) | 237 |
| B | Dev sau rà soát | 8/15 (53,3%) | 10/15 (66,7%) | 270 |
| C | Dev sau rà soát | 9/15 (60,0%) | 10/15 (66,7%) | 270, dùng B |
| A | Test, học viên rà soát xác nhận | 0/5 (0%) | 1/5 (20%) | 237 |
| B | Test, học viên rà soát xác nhận | 1/5 (20%) | 2/5 (40%) | 270 |
| C | Test, học viên rà soát xác nhận | 1/5 (20%) | 2/5 (40%) | 270, dùng B |

Baseline dev trước bổ sung evidence: A 5/15 và 7/15; B 7/15 và 9/15; C 8/15 và 9/15
(Hit@1, Hit@3). Các baseline/trace không bị ghi đè. Test nhỏ hơn dev và chưa dùng
phát triển; chênh lệch không đủ chứng minh nguyên nhân duy nhất hay độ tốt tổng quát.

| Tài nguyên | A | B | C |
|---|---:|---:|---|
| Tổng ký tự chunk (gồm overlap nếu có) | 109.015 | 98.886 | Dùng B |
| Độ dài min / median / max, ký tự | 76 / 500 / 500 | 31 / 393 / 499 | Dùng B |
| Tổng token đầu vào embedding, gồm prefix/special | 24.853 | 22.587 | Không embed thêm |
| Embedding CPU trong lần đo | 9,842 giây | 10,044 giây | Dùng vector B |
| Upsert lần đầu trong lần đo lưu trữ | 0,225 giây | 0,220 giây | Không nhập bản sao |
| Phí dịch vụ | 0 USD | 0 USD | 0 USD |

Nạp model 3,204 giây; script embedding tổng 23,325 giây. Không đo gộp end-to-end
đọc PDF + chunking + embedding + DB thành một thời gian ingest; không cộng các lần
đo khác thời điểm rồi gọi đó là phép đo chung. Máy Ryzen 5 5500U, khoảng 8 GB RAM,
Windows Python/Ubuntu WSL; số đo phụ thuộc tải máy. Thời gian từng query/search
được lưu trong trace. B/C có nhiều chunk hơn nhưng tổng token embed B thấp hơn A
do không overlap; không suy luận thời gian tuyến tính chỉ từ số chunk.

## 5. Ba audit của học viên

Người chấm/kiểm tra: **Phạm Tuấn Anh**, tác giả bài lab. Điểm/lý do được gửi qua
chat; Codex ghi lại, đối chiếu ID/trang và tính tổng. Không coi là đánh giá độc lập
hoặc chấm mù, không tự suy nhãn từ similarity.

| Strategy | Coherence /2 (n) | Metadata đủ/đúng | Filter test tuân thủ | Grounding số câu 0 / 1 / 2 | Grounding /2 |
|---|---|---|---|---|---:|
| A | 1,0 (10) | 15/15 | 1/2 | 0 / 4 / 1 | 1,2 |
| B | 2,0 (10) | 15/15 | 1/2 | 2 / 1 / 2 | 1,0 |
| C | 2,0 (10) | 15/15 | 2/2 | 2 / 1 / 2 | 1,0 |

**Coherence:** chọn trước khi nhận điểm 10 trang đầu corpus theo số trang tăng dần,
một anchor đoạn chính mỗi trang; chọn chunk phủ anchor có start_char nhỏ nhất.
Dùng cùng vị trí cho A/B/C, C tái dùng B. Tôi cho A=1 và B/C=2 ở cả 10 mẫu, có lý do
cụ thể về câu/từ bị cắt, heading dính thêm hoặc ranh giới giữ trọn ý. B mẫu 05 vẫn có
đuôi câu trang trước; tôi chấp nhận vì câu ví dụ chính đầy đủ. Không suy 2/2 thành
toàn corpus không lỗi; 10 trang đầu chưa đại diện đủ section và B/C không độc lập.

**Metadata:** tôi kiểm tra đủ 45 bản ghi test, không phát hiện lỗi document_id/source/
page/section; kiểm chứng kỹ thuật cũng khớp 45 lát cắt PDF. Source/page giúp mở đúng
nguồn, section giúp lọc. A/B không filter là đúng thiết kế, nên không tuân phạm vi
không đồng nghĩa gắn sai metadata. Hạn chế: đúng metadata không đảm bảo đủ evidence,
ví dụ q20–C vẫn thiếu điều kiện dù section đúng.

**Grounding:** chấm cả bộ top-3 của 5 câu test mỗi strategy, theo 0/1/2. A có nhiều
bằng chứng một phần nên trung bình 1,2, cao hơn B/C 1,0 dù Hit@3 thấp hơn. Ví dụ q17–A
và q19–A tôi cho 1 vì có liên hệ chủ đề/chủ thể nhưng thiếu ý trả lời; nhãn này là
nhận xét của tôi theo thang đã hướng dẫn, có thể có thiên lệch/khác biệt giữa người
chấm. Grounding ở đây là đủ evidence, không phải độ chính xác câu trả lời LLM.

## 6. Tác động chiến lược và ví dụ lỗi

**A–B:** B tăng dev Hit@3 từ 8/15 lên 10/15 và test từ 1/5 lên 2/5. Coherence trên
mẫu tăng 1,0 lên 2,0 vì giữ ranh giới câu/ý tốt hơn. Đổi lại B có 270 chunk so với
237 và vẫn có chunk ngắn chỉ header/credit; không phải mọi chunk cấu trúc đều hữu ích.
A có overlap, B không overlap nên khác biệt bao gồm chính sách chunking tổng thể.

**B–C:** chỉ thay filter. C tăng dev Hit@1 từ 8/15 lên 9/15, filter compliance test
từ 1/2 lên 2/2, nhưng test Hit@1/Hit@3 và grounding bằng B. Filter giảm phạm vi sai,
không sửa đoạn bị chia thiếu hoặc đảm bảo lấy đúng đoạn. Không filter thì B/C giống nhau.

| Ví dụ | Nguồn | Quan sát và tác động |
|---|---|---|
| q15 dev, A so với B/C | esmap-annual-report-2021, PDF 61 | A thiếu đầu câu nhưng chứa đủ 4,5 triệu euro/20 năm/hoàn vốn 5 năm. Review chấp nhận A; cho thấy matching toàn quote có thể quá chặt. Không dùng lỗi chấm ban đầu để thổi phồng B. |
| q17 test, A/B/C | PDF 31 | A lấy đoạn chủ đề coal repurposing, thiếu ba công năng; B/C không lấy đoạn trả lời, có cả chunk credit ảnh. Lỗi truy xuất đúng đoạn và nhiễu boilerplate. |
| q18 test, A so với B/C | PDF 41 | A cắt trước nguyên nhân trợ cấp/cấp phép; B/C giữ đủ hai ý trong rank 1. Ranh giới chunk ảnh hưởng evidence đầy đủ. |
| q20 test, C | PDF 62 | Lấy đúng dự án/section nhưng thiếu câu điều kiện sau đánh giá kỹ thuật. Filter không thể khôi phục phần bị thiếu trong top-3. |

## 7. Giới hạn, lỗi chạy và cải tiến sau nghiên cứu

- Chỉ một báo cáo tiếng Anh năm 2021, truy vấn tiếng Việt, dev 15/test 5; mỗi câu
  test là 20 điểm phần trăm. Không diễn giải số liệu lịch sử thành hiện trạng hiện nay.
- Có liên hệ chủ đề giữa dev/test, test chưa có Clean Cooking. Người tạo dữ liệu và
  người chấm không độc lập; tôi đã thấy phần hỗ trợ của AI trước khi xác nhận dev.
- Coherence 10 trang đầu, C dùng chung B; metadata 45/45 chỉ đúng trên mẫu đã kiểm.
- Matching chuỗi có giới hạn, đã công khai dev additions; test reviewed không đổi.
  Không tự ghép evidence nhiều chunk vào metric chính.
- PDF đa cột, header/footer/ảnh credit, ngắt từ/đoạn qua trang chưa xử lý hoàn toàn.
- Đã gặp timeout khi container WSL dừng exit 0, không OOM; khởi động lại thành công,
  không xóa volume. Kiểm tra sai chiều và snapshot cleanup đã pass, không fallback giả.
- Cải tiến có thể thử trong nghiên cứu tiếp theo: bỏ boilerplate có kiểm chứng,
  cấu trúc PDF tốt hơn, kích thước/overlap khác, query ngắn gọn, hoặc hybrid. Vì đã
  xem test, không chỉnh rồi báo lại như holdout độc lập; cần benchmark test mới.

## 8. Tái lập, minh chứng và sử dụng AI

Xem [README](../../README.md) và [starter/README](../../starter/README.md) để setup,
lấy dữ liệu/model, tạo chunk/vector, nạp pgvector, truy xuất và kiểm tra. Kết quả
test lần đầu có guard chống ghi đè. Không commit .env/model/PDF gốc/venv. Hash frozen
là snapshot file tại thời điểm chốt, không phải commit Git chốt bài.

| Minh chứng | File |
|---|---|
| Corpus/quyền | [manifest](../../data/manifest.json), [attribution](../../data/ATTRIBUTION.md) |
| Benchmark/split | [questions](../../benchmark/questions.json), [manifest](../../benchmark/manifest.json) |
| Cấu hình và lịch sử chốt | [chunking](../../artifacts/chunking_config.json), [embedding](../../artifacts/embedding_config.json), [frozen](../../artifacts/frozen_pipeline.json) |
| Nhật ký tổng hợp | [experiment_log.csv](../../artifacts/experiment_log.csv), [ghi chú](../../artifacts/experiment_log_README.md) |
| Dev baseline/reviewed | [trace gốc](../../results/dev/traces.jsonl), [reviewed](../../results/dev/reviewed/comparison.md), [xác nhận học viên](../dev_evidence_review_and_freeze.md) |
| Test + nhãn học viên | [trace](../../results/test/traces.jsonl), [summary rà soát](../../results/test/student_review/summary.json), [báo cáo](../test_evidence_review_student.md) |
| Coherence | [nhãn](../../results/coherence/student_scores.json), [mẫu/ID](../../results/coherence/reviewed_samples.jsonl), [báo cáo](../coherence_review_student.md) |
| Metadata | [45 bản ghi](../../results/test/student_review/metadata_audit.json), [báo cáo](../metadata_review_student.md) |
| Grounding | [điểm/lý do](../../results/test/student_review/grounding_scores.json), [báo cáo](../grounding_review_student.md) |
| Tài nguyên/lỗi | [embedding](../../results/embeddings/summary.json), [storage](../../results/storage_check.json), results/ingestion.log, results/embeddings/embedding.log, results/dev/run.log, results/test/run.log |

Tôi dùng **Codex** để giải thích, hỗ trợ code, soạn benchmark, đối chiếu nguồn và
chuẩn bị báo cáo. Tôi rà soát dev, tự gửi bản đánh giá evidence test, điểm coherence,
grounding và kết quả metadata; các báo cáo ghi đúng người chấm. Kiểm tra bằng PDF,
trace, ID/hash và phép tính lại; không tự tạo số đo, nhãn người học hoặc kết quả chưa chạy.

Kết luận: chọn **C theo dev trước test**, có lợi về giới hạn phạm vi khi có filter.
Test chỉ đạt 2/5 Evidence Hit@3 nên chưa đủ để dùng như hệ thống trả lời đáng tin cậy;
giá trị của bài là pipeline có thể truy vết, phép so sánh có kiểm soát và phân tích
trung thực các lỗi. Grounding cao hơn của A là đánh đổi cần báo cáo, không bỏ qua.
