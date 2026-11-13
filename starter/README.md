# Starter · PostgreSQL + pgvector

Bộ khởi động **tùy chọn** cho lab cá nhân. Docker Compose tạo PostgreSQL + pgvector local.
Hiện đã triển khai đọc tài liệu, chia chunk A/B, embedding local và lưu pgvector.
Đã có runner và metric retrieval tự động cho dev/test; đã chạy lần test đầu tiên
theo snapshot đã chốt. Phạm Tuấn Anh đã rà soát evidence test, chấm grounding,
kiểm tra metadata và chấm coherence trên 10 mẫu đã chuẩn bị. Phân tích, nhật ký và
[báo cáo cá nhân](../report/individual/2A202603503_PhamTuanAnh.md) đã hoàn thiện;
còn commit/push và nộp link theo kênh lớp. Vẫn có thể chọn
Qdrant, Chroma hoặc vector store tương đương theo [GUIDE.md](../GUIDE.md).

## Cấu trúc

```text
starter/
├── docker-compose.yml     # PostgreSQL 16 + pgvector, chỉ mở cổng local
├── init.sql               # bật extension khi tạo database mới
├── requirements.txt       # psycopg, pypdf và python-dotenv
├── .env.example           # cấu hình mẫu; copy thành .env
├── scripts/check_setup.py # kiểm tra kết nối và extension (đã chạy được)
├── src/
│   ├── models.py          # cấu trúc dữ liệu mẫu
│   ├── ingestion.py       # TODO: đọc / chuẩn hóa tài liệu
│   ├── chunking.py        # TODO: chia chunk
│   ├── embeddings.py      # TODO: chọn model API hoặc local
│   ├── store.py           # TODO: lưu vector, metadata và filter
│   ├── evaluation.py      # TODO: chấm truy xuất, lưu trace
│   └── run.py             # TODO: kết nối các bước thành pipeline
├── data/                  # bạn tự chuẩn bị corpus được phép sử dụng
└── results/               # lưu kết quả của bạn
```

## 1. Cài và kiểm tra database

Cần Docker Desktop hoặc Docker Engine + Compose, Python **3.11–3.14**, và mạng để tải image/dependencies lần đầu. Các lệnh sau chạy từ thư mục `starter/`:

```bash
cd starter
python3 -m venv .venv
```

Kích hoạt `.venv`: macOS/Linux dùng `source .venv/bin/activate`; Windows PowerShell dùng `.venv\Scripts\Activate.ps1`. Sau đó:

```bash
python -m pip install -r requirements.txt
# macOS/Linux: cp .env.example .env
# Windows PowerShell: Copy-Item .env.example .env
docker compose -p day6_student_starter up -d --wait
python scripts/check_setup.py
```

Kỳ vọng: hiện tên database, phiên bản PostgreSQL và pgvector, sau đó `Setup OK`. Đây **chỉ là kiểm tra hạ tầng**, không phải kết quả benchmark. Docker dùng cổng `127.0.0.1:55433` và mật khẩu cố định **chỉ dùng local cho lab**; nếu cổng bận, sửa đồng thời port trong `docker-compose.yml` và `DATABASE_URL` trong `.env`. `init.sql` chỉ chạy khi volume mới được tạo; nếu database sẵn có chưa bật extension, xem log Docker và kiểm tra cấu hình thay vì xóa volume chứa dữ liệu.

Dừng container nhưng giữ dữ liệu:

```bash
docker compose -p day6_student_starter stop
```

### Windows dùng Docker trong Ubuntu WSL

Máy hiện tại dùng Python trong `starter/.venv` trên Windows và Docker Engine trong
Ubuntu WSL 2. Chạy các lệnh sau trong PowerShell, từ thư mục `starter/`:

```powershell
# Khởi động database; WSL tự chuyển thư mục hiện tại sang đường dẫn Linux.
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait

# Gọi trực tiếp Python trong môi trường ảo, không cần activate.
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_setup.py

# Xem trạng thái và log khi cần.
wsl -d Ubuntu -- docker compose -p day6_student_starter ps
wsl -d Ubuntu -- docker compose -p day6_student_starter logs --tail 50 postgres

# Dừng database và giữ dữ liệu trong Docker volume.
wsl -d Ubuntu -- docker compose -p day6_student_starter stop
```

Kết nối từ Python Windows vẫn dùng `127.0.0.1:55433` trong `.env`.
Không chạy `down -v` nếu cần giữ dữ liệu. Docker Compose đã được cài trong Ubuntu;
không cần Docker Desktop cho cách chạy này.

### Kiểm tra bước đọc và chuẩn hóa đã triển khai

`src/ingestion.py` đã có `load_pdf`, `normalize_text` và `load_corpus`.
Bước này đọc PDF gốc, kiểm tra SHA-256, chọn trang theo `data/manifest.json`,
gắn section và ghi nhận trang rỗng/lỗi.

Từ thư mục `starter/`:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/check_ingestion.py
```

Lệnh đối chiếu toàn bộ 38 trang với corpus đã chốt, kiểm tra Unicode và xuất:

- `../results/ingestion_check.json`: thống kê và kết quả kiểm tra.
- `../results/ingestion_page65.json`: trang mẫu 65 với text và metadata.
- `../results/ingestion.log`: log, gồm cảnh báo trang 82 không có text.

Không cần database hoặc API key cho bước đọc tài liệu. Chuẩn hóa giữ nguyên chính sách
đã chốt ở nhiệm vụ 1; chưa xóa header/footer hoặc nối từ ngắt dòng để tránh làm thay
đổi corpus và evidence đã kiểm chứng.

### Chia chunk A và B

`src/chunking.py` đã triển khai A (500 ký tự, overlap 50) và B (đoạn/heading,
tối đa 500 ký tự, không overlap). Tham số nằm trong `../artifacts/chunking_config.json`.
B nhận diện dòng trống và heading chữ hoa; khi đoạn quá dài hoặc không có ranh giới
đoạn trong text PDF, ưu tiên ngắt ở câu, rồi khoảng trắng, cuối cùng ngắt cứng.
Đây là heuristic, chưa bảo đảm khôi phục cấu trúc đoạn của PDF.

Từ `starter/`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 scripts/check_chunking.py
```

Kết quả nằm trong `../results/chunking/`: `chunks_A.jsonl`, `chunks_B.jsonl`,
`summary.json` và `page65_comparison.md`. Mỗi chunk giữ nguồn, trang, section,
offset ký tự và ID ổn định. Offset bắt đầu từ 0, cuối không bao gồm ký tự tại vị trí đó.
Chỉ bỏ khoảng trắng ở hai đầu chunk; không sửa corpus hoặc dùng benchmark để chia đoạn.
Chưa tạo embedding hoặc đánh giá retrieval/coherence.

## 2. Chọn embedding model

Đã chọn `intfloat/multilingual-e5-small`, ONNX FP32 chạy CPU, 384 chiều, revision
`614241f622f53c4eeff9890bdc4f31cfecc418b3`. Dùng `passage: ` cho tài liệu và `query: `
cho câu hỏi, masked mean pooling rồi chuẩn L2 theo
[model card](https://huggingface.co/intfloat/multilingual-e5-small).
Giới hạn 512 token gồm tiền tố và token đặc biệt; đầu vào quá dài báo lỗi, không âm
thầm cắt. Không cần API key. Toàn bộ suy luận chạy local sau khi tải model.

Từ `starter/`:

```powershell
python -m pip install -r requirements.txt
# Hoặc dùng requirements-lock.txt để cài đúng toàn bộ phiên bản đã chạy.
.\scripts\download_embedding_model.ps1
.\.venv\Scripts\python.exe -X utf8 scripts/embed_chunks.py
```

Model/tokenizer được kiểm tra SHA-256, lưu tại `../models/multilingual-e5-small/`
và được Git bỏ qua; cấu hình/prefix/revision nằm trong `../artifacts/embedding_config.json`.
Tạo lại chunk trước nếu chưa có `../results/chunking/chunks_A.jsonl` và `chunks_B.jsonl`.

Đầu ra trong `../results/embeddings/`:

- `vectors_A.npz`, `vectors_B.npz`: mảng `vectors` float32 và `chunk_ids` cùng thứ tự.
- `summary.json`: model/runtime, hash file chunk/vector, thời gian và số token.
- `query_smoke.json`: vector câu hỏi thử; không có kết quả tìm kiếm.
- `embedding.log`: tiến độ và lỗi; không fallback sang vector giả.

Ví dụ đọc vector bằng NumPy: `np.load(path, allow_pickle=False)` rồi lấy `vectors`
và `chunk_ids`. Không dùng file NPZ thay cho vector store bắt buộc: đây là kết quả
trung gian để nạp pgvector ở bước tiếp theo. C sẽ tái dùng vector B.
Script không đọc benchmark/gold, không chạy retrieval hoặc tính điểm dev/test.

### Nạp vector vào PostgreSQL + pgvector

Đã triển khai `PgVectorStore.create_schema()` và `upsert()` trong `src/store.py`.
Bảng `public.day6_chunks` chứa strategy, chunk_id, document_id, source, page, text,
metadata JSONB và embedding `vector(384)`. Khóa chính là `(strategy, chunk_id)`.
Metadata giữ section, offsets, cấu hình chunking và thông tin model/revision.
Index thông thường phục vụ strategy/document/section; chưa tạo index vector approximate.

Từ thư mục `starter/` (khởi động database ngay trước khi chạy):

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 scripts/ingest_vectors.py
```

Script kiểm tra hash model config/chunk/vector và thứ tự ID, nạp A/B, đọc lại bằng
kết nối mới để so sánh text/metadata/vector, rồi nạp lại để kiểm tra không trùng.
Đồng thời kiểm tra loại chunk cũ bằng strategy thử riêng và dọn dữ liệu thử đó.
Kết quả ở `../results/storage_check.json`. Không cần tạo lại embedding.

`upsert` nhận **toàn bộ chunk của từng document được cung cấp**, không gọi từng batch
nhỏ của cùng document vì hàm sẽ loại những chunk cũ không thuộc snapshot được gửi.
Các document/strategy khác được giữ. Input rỗng bị từ chối; lỗi giao dịch rollback.
Không dùng `down -v` hoặc xóa volume khi cần giữ dữ liệu. Nếu WSL/container đã dừng,
chạy lệnh `up -d --wait` trước; dữ liệu nằm trong Docker volume.

Không nhập bản sao C: C truy xuất tập B với filter khi được cung cấp.

### Tìm kiếm top-3 bằng cosine và metadata filter

`PgVectorStore.search()` đã triển khai exact cosine search trong SQL bằng toán tử
`<=>`. Filter áp dụng trước khi xếp hạng; kết quả có text, chunk ID, source/page,
metadata, rank, cosine_distance và score = 1 - cosine_distance (cao hơn là gần hơn).
Kết quả bằng điểm được sắp thêm theo chunk_id. Không có kết quả phù hợp trả `[]`,
ít hơn 3 thì trả đúng số có sẵn, không bỏ filter để bù kết quả.

Từ `starter/`, chạy ví dụ không filter (B):

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 scripts/search_chunks.py --strategy B --question "Báo cáo mô tả các giải pháp lưu trữ năng lượng như thế nào?"
```

Hoặc chạy C với section do người dùng cung cấp trước:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/search_chunks.py --strategy C --section "Renewable Energy" --question "Báo cáo mô tả các giải pháp lưu trữ năng lượng như thế nào?" --output ../results/search/example_C.json
```

CLI chỉ cho `--section` khi dùng C. C không filter cho kết quả giống B. Hàm store
cấp thấp còn hỗ trợ equality AND trên section/report_year/document_id/source/page;
không dùng gold page/source để tạo filter khi chạy benchmark. Key không hỗ trợ hoặc
kiểu sai báo lỗi; mọi giá trị SQL đều được bind bằng tham số.
CLI đối chiếu model config trong database với model query trước khi tìm.

Kiểm tra tích hợp (không đọc benchmark):

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/check_search.py
```

Đầu ra `../results/search/check_summary.json` và `smoke_traces.json`.
Kiểm chứng bao gồm xếp hạng cosine, filter, B/C không filter, tập ít hơn 3 kết quả,
input sai và giá trị filter có hình thức SQL. NumPy chỉ làm oracle trong kiểm tra;
ứng dụng luôn truy xuất bằng pgvector. Chưa chạy dev/test hoặc tính Hit@1/Hit@3.
Score similarity không phải xác suất trả lời đúng hoặc nhãn grounding.

### Chạy benchmark dev A/B/C

Từ `starter/`, sau khi đã nạp vectors vào database:

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 -m src.run --split dev
.\.venv\Scripts\python.exe -X utf8 scripts/analyze_dev.py
```

Runner kiểm tra checksum benchmark/corpus/chunk/vector và đối chiếu snapshot database,
embed mỗi câu dev một lần rồi tái dùng cùng query vector cho A/B/C. Chỉ question/filter
được đưa vào truy xuất; các trường gold chỉ dùng sau khi có kết quả. A/B không filter,
C áp dụng filter nếu câu hỏi cung cấp. `--split dev` chạy riêng dev; test dùng
`--split test` và bắt buộc kiểm tra snapshot trước khi chạy.

Output `../results/dev/`: traces.jsonl (45 lượt đầy đủ top-3), summary.json,
comparison.md, run.log, manual_review_queue.json. analyze_dev.py kiểm tra summary
khớp trace, tạo failure_analysis.json và selection.json theo quy tắc chọn đã chốt.

`src/evaluation.py` chấm hit khi một chunk đúng nguồn/trang chứa toàn bộ evidence
đã ghi hoặc alternative được ghi nhận, sau NFC/chuẩn hóa khoảng trắng. Không tự ghép
evidence qua nhiều chunk. Đây là cách chấm tự động bảo thủ, có thể bỏ sót bằng chứng
ngữ nghĩa tương đương hoặc quote dài hơn phần cần để trả lời. Cần review và khai báo
bằng chứng tương đương trước khi xem đây là kết quả đã chấm ngữ nghĩa hoàn chỉnh.
Không suy ra nhãn coherence/grounding thủ công từ matching. Kết quả test đầu tiên
được lưu riêng tại `../results/test/`, không dùng để chọn lại cấu hình.

## 3. Các phần còn lại của lab

### Evidence test đã được học viên rà soát

Phạm Tuấn Anh đã gửi nhận xét cho đủ 15 lượt test/45 chunk, ngày 13/11/2026.
Báo cáo ở `../report/test_evidence_review_student.md`, bản gốc ở
`../report/sources/test_evidence_review_student_original.txt`. Nhãn và lý do do học viên
cung cấp; Codex chỉ nhập, định dạng, đối chiếu ID/trang và kiểm tra tổng hợp.
File đầy đủ ID/nhãn: `../results/test/student_review/chunk_reviews.jsonl`;
metric: `../results/test/student_review/summary.json`.
Kết quả khớp baseline: A Hit@1=0/5, Hit@3=1/5; B/C Hit@1=1/5, Hit@3=2/5.
Không ghi đè trace hoặc summary test gốc; không thay cấu hình/lựa chọn C.
Không suy ra điểm audit từ nhãn evidence. Sau đó học viên đã gửi điểm grounding và
kiểm tra metadata riêng, ghi ở các báo cáo dưới đây.

### Grounding, metadata và mẫu coherence

Điểm grounding do Phạm Tuấn Anh gửi: A trung bình 1,2/2; B/C 1,0/2. Báo cáo:
`../report/grounding_review_student.md`. Metadata học viên kiểm tra đủ/đúng 15/15
bản ghi mỗi strategy; đã đối chiếu kỹ thuật 45/45 lát cắt PDF và trường nguồn/section.
Báo cáo: `../report/metadata_review_student.md`. A/B không filter là đúng thiết kế,
không phải lỗi metadata hoặc triển khai.

Học viên đã chấm 10 vị trí nguồn chung cho A/B/C: A trung bình 1,0/2; B/C 2,0/2.
C dùng chunk B nên điểm trùng không phải hai bộ quan sát độc lập. Báo cáo và lý do:
`../report/coherence_review_student.md`; nhãn gốc `../results/coherence/student_scores.json`.
Dữ liệu mẫu ban đầu ở `../results/coherence/samples.json`, giữ nguyên để đối chiếu.

### Rà soát evidence dev và snapshot trước test

Đã đọc lại 45 trace/135 chunk dev, đối chiếu nguồn và ghi lý do ở
`../results/dev/review_decisions.json`. Chấp nhận evidence ngắn hơn cho q02/q15
theo `../benchmark/evidence_policy.json`; không đổi questions.json hoặc lấy nhiều
chunk ghép thành hit. Kết quả baseline vẫn giữ nguyên; kết quả sau rà soát ở
`../results/dev/reviewed/comparison.md`. Reviewer là Codex, không phải con người
độc lập; chưa tạo nhãn coherence/grounding thủ công.

**C đã được chọn và cấu hình trước test đã chốt** tại
`../artifacts/frozen_pipeline.json` bằng Hit@3 rồi Hit@1 trên dev đã rà soát.
Không thay model/chunking để tăng điểm. Snapshot được tạo trước test; lần test đầu
tiên sau đó đã hoàn tất. Lệnh kiểm tra snapshot từ starter/:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/freeze_configuration.py
```

Kiểm tra phải pass trước khi đánh giá test. Snapshot ghi hash của corpus, benchmark,
code thuật toán, cấu hình, vector và bằng chứng/kết quả dev đã rà soát. Không ghi đè
snapshot hoặc tạo lại các file đã chốt để che thay đổi. Nếu cần sửa thuật toán/cấu hình,
ghi phiên bản và lý do rõ ràng trước khi test; chỉnh theo kết quả test làm mất tính holdout.

`scripts/review_dev.py` có thể tái lập việc chấm lại từ trace cũ mà không truy xuất
database. Không cần chạy lại sau khi freeze; baseline và reviewed đều là lịch sử đã chốt.

1. Đặt corpus vào `data/` hoặc cung cấp manifest/hướng dẫn truy cập. Đọc [GUIDE.md](../GUIDE.md) về **30 trang nội dung**, quyền dữ liệu và metadata.
2. Hoàn thiện từng hàm TODO trong `src/`. Lưu ID tài liệu, nguồn, trang/vị trí và ít nhất một trường filter có ích.
3. Xây ít nhất ba cấu hình; ví dụ A fixed-size, B theo đoạn, C như B nhưng có filter. Cần cùng corpus, model và benchmark; nạp lại không nhân đôi và xử lý chunk cũ khi dữ liệu đổi.
4. Tự viết ít nhất 20 câu hỏi kèm evidence, tách dev/test trước khi thử theo [BENCHMARK.md](../BENCHMARK.md). Lưu trace top-3 và báo cáo đủ năm tiêu chí.
5. Chạy `python -m src.run --split dev` từ `starter/` để đánh giá dev. Test và audit
   thủ công là các bước tiếp theo, sau khi đã chốt cấu hình.

Lưu code, cấu hình, kết quả và lệnh chạy để người chấm tái lập; không commit key, dữ liệu mật hoặc dữ liệu không có quyền chia sẻ.
