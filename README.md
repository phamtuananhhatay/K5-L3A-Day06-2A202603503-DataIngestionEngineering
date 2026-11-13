# Day 06 · Bài nộp Phạm Tuấn Anh

**MSSV:** 2A202603503 · **Lớp:** L3A

**Chủ đề:** truy xuất bằng chứng về chuyển dịch năng lượng từ ESMAP Annual Report 2021.

Đã triển khai pipeline Python: đọc/chuẩn hóa PDF → chunk A/B → embedding local
đa ngữ → PostgreSQL + pgvector → exact cosine top-3 → đánh giá A/B/C. C dùng vector B
và filter section do câu hỏi cung cấp. Không xây chatbot sinh câu trả lời.

## Đọc bài nộp

- [Báo cáo cá nhân đầy đủ](report/individual/2A202603503_PhamTuanAnh.md)
- [Thông tin học viên](STUDENT.md) và [trạng thái checklist](report/submission_checklist.md)
- [Nguồn/quyền/cách lấy dữ liệu](data/README.md), [manifest](data/manifest.json)
- [Benchmark và split](benchmark/README.md), [20 câu hỏi/evidence](benchmark/QUESTIONS_REVIEW.md)
- [Nhật ký thí nghiệm](artifacts/experiment_log.csv) và [cách đọc log](artifacts/experiment_log_README.md)
- [Hướng dẫn kỹ thuật chi tiết](starter/README.md), [danh mục kết quả](results/README.md)

## Kết quả chính

| Strategy | Dev Hit@1 | Dev Hit@3 | Test Hit@1 | Test Hit@3 | Coherence /2 | Grounding /2 |
|---|---|---|---|---|---:|---:|
| A | 6/15 | 8/15 | 0/5 | 1/5 | 1,0 | 1,2 |
| B | 8/15 | 10/15 | 1/5 | 2/5 | 2,0 | 1,0 |
| C | 9/15 | 10/15 | 1/5 | 2/5 | 2,0 | 1,0 |

Dev sau rà soát, test được học viên rà soát xác nhận; metadata test đủ/đúng 15/15
bản ghi mỗi strategy. **Chọn C trước test** bằng dev Hit@3 rồi Hit@1; không chọn lại
theo test. Các mẫu nhỏ, grounding A cao hơn B/C và các giới hạn được phân tích trong
báo cáo, không tuyên bố C tốt nhất tổng quát. Người chấm audit: Phạm Tuấn Anh.

## Setup và chạy lại (Windows PowerShell + Ubuntu WSL)

Cần Python 3.11–3.14, Docker Engine + Compose trong Ubuntu WSL 2 hoặc Docker Desktop,
mạng để tải thư viện/model lần đầu. Lần đo dùng Python 3.11.9, pgvector 0.8.7 trên
PostgreSQL 16.16. Có thể đọc mọi báo cáo/trace mà không khởi động database.

Từ thư mục gốc repo:

```powershell
cd starter
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
# Chỉ copy nếu chưa có .env; không commit .env.
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe scripts/check_setup.py
```

Nếu dùng Docker Desktop thay WSL, thay `wsl -d Ubuntu -- docker ...` bằng `docker ...`.
Tải PDF theo [data/README.md](data/README.md), đặt đúng tên trong data/raw/. PDF và
model lớn được Git bỏ qua; snapshot text/chunk/vector và kết quả nhỏ có trong repo.

Từ `starter/`, kiểm tra kết quả hiện có và chuẩn bị tìm kiếm:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 scripts/validate_benchmark.py
.\.venv\Scripts\python.exe -X utf8 scripts/freeze_configuration.py
.\scripts\download_embedding_model.ps1
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 scripts/ingest_vectors.py
```

Tìm một câu hỏi với C, không sử dụng gold làm input:

```powershell
.\.venv\Scripts\python.exe -X utf8 scripts/search_chunks.py --strategy C --section "Renewable Energy" --question "Báo cáo mô tả các giải pháp lưu trữ năng lượng như thế nào?"
```

Để tái lập retrieval mà giữ nguyên trace holdout đầu tiên, dùng thư mục riêng:

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 -m src.run --split dev --output-dir ../results/reproduction/dev
.\.venv\Scripts\python.exe -X utf8 -m src.run --split test --output-dir ../results/reproduction/test
```

Các lần tái lập này đã biết test, không phải holdout mới. Runner test từ chối ghi đè
thư mục có summary. Metric tự động ban đầu chưa nhận evidence dev bổ sung; bản reviewed
và xác nhận học viên nằm trong results/dev/reviewed/ và báo cáo, được giữ riêng.

Muốn tái tạo toàn pipeline đọc/chunk/embedding: dùng bản sao repo và giữ nguyên bản
gốc để đối chiếu; lần lượt chạy check_ingestion.py, check_chunking.py, embed_chunks.py,
ingest_vectors.py. Sau tạo lại file, hash có thể thay đổi: không ghi đè frozen snapshot
để che khác biệt. Chi tiết từng bước trong starter/README.md.

## Minh chứng, chi phí và nộp bài

Model intfloat/multilingual-e5-small, revision cố định, ONNX FP32, 384 chiều, CPU.
Phí dịch vụ 0 USD, không gồm điện/mạng/phần cứng. Phiên bản thư viện và lệnh chạy
được ghi trong requirements-lock.txt và báo cáo; lỗi có trong results/*/run.log
và các log chuyên biệt. Không fallback vector giả. Ghi nguồn/công cụ AI và người
chấm đúng thực tế.

Bài làm hiện được hoàn thiện trong workspace. Chưa tạo commit chứa toàn bộ bài
nộp, chưa push hoặc xác minh truy cập của người chấm, chưa nộp link trên kênh lớp.
Xem checklist để hoàn tất các thao tác Git/nộp bài; không suy deadline từ checkpoint.

---

<details>
<summary>Đề bài gốc và tài liệu lớp (giữ để tham khảo)</summary>

# Day 06 · Data Ingestion Engineering

**Lab cá nhân** · **4 giờ** · **Dữ liệu tự chọn**

Biến tài liệu thành kho tri thức có thể truy xuất cho AI agent, rồi đo xem cách chuẩn bị dữ liệu nào hiệu quả nhất.

| 📄 Dữ liệu | 🧩 Chiến lược | 🎯 Benchmark |
|---|---|---|
| Tối thiểu **30 trang nội dung** | Tối thiểu **3 cấu hình** | Tối thiểu **20 câu hỏi** |

## Bắt đầu nhanh

Dùng [starter PostgreSQL + pgvector](starter/README.md) để dựng database và hoàn thiện các hàm TODO, hoặc tự chọn vector store tương đương. Starter chỉ là khung: **bạn tự hiện thực pipeline và benchmark**.

## 1. Xây pipeline

![Đọc tài liệu, chuẩn hóa, chia chunk, tạo vector, lưu và kiểm tra](assets/ingestion-pipeline.svg)

Chọn tài liệu được phép sử dụng; giữ **ID tài liệu, nguồn, trang/vị trí** và metadata phù hợp. Dùng embedding model thật qua API hoặc chạy local; lưu và truy xuất bằng pgvector, Qdrant, Chroma hoặc một store tương đương.

## 2. So sánh và đánh giá

![Ba chiến lược được đánh giá trên cùng corpus và benchmark dev/test](assets/benchmark-workflow.svg)

Dùng cùng dữ liệu, model và câu hỏi cho cả ba cấu hình. Tách **15 câu dev / 5 câu test** trước khi chạy; chọn cấu hình trên dev, rồi đánh giá test sau khi cố định. Mỗi câu hỏi cần có đoạn bằng chứng và trang nguồn; thiết kế bộ câu hỏi và đánh giá theo [BENCHMARK.md](BENCHMARK.md).

Đánh giá theo năm khía cạnh: **độ chính xác truy xuất**, **tính mạch lạc của chunk**, **tính hữu dụng của metadata**, **chất lượng grounding** và **tác động của chiến lược dữ liệu**. Giải thích lựa chọn bằng kết quả, ví dụ lỗi và các đánh đổi.

## 3. Chuẩn bị bài nộp

1. Chạy pipeline và lưu cấu hình, kết quả top-3, trace cùng nhãn đánh giá thủ công.
2. Điền [thông tin học viên](STUDENT.md), [nhật ký thí nghiệm](artifacts/experiment_log.csv) và bản sao [mẫu báo cáo cá nhân](report/individual/MSSV_HoTen.md).
3. Kiểm tra mã nguồn, cách chạy, manifest dữ liệu và checklist trong [SUBMISSION.md](SUBMISSION.md).

## Tài liệu hướng dẫn

| Bạn cần tìm | Tài liệu |
|---|---|
| Setup baseline PostgreSQL + pgvector | [starter/README.md](starter/README.md) |
| Các bước làm và cách tính chỉ số | [GUIDE.md](GUIDE.md) |
| Tiến độ trong 4 giờ | [CHECKPOINTS.md](CHECKPOINTS.md) |
| Năm tiêu chí benchmark và bộ câu hỏi | [BENCHMARK.md](BENCHMARK.md) |
| Tiêu chí chấm điểm | [RUBRIC.md](RUBRIC.md) |
| Quy tắc sử dụng dữ liệu, AI và API | [RULES.md](RULES.md) |
| Cách nộp bài | [SUBMISSION.md](SUBMISSION.md) |

[data/format-example.json](data/format-example.json) chỉ minh họa định dạng, không phải corpus đủ điều kiện. Phần xử lý và benchmark do bạn tự hiện thực; không bắt buộc xây chatbot.

</details>
