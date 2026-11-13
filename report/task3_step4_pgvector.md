# Nhiệm vụ 3, bước 4: lưu vector vào PostgreSQL + pgvector

## Đã thực hiện

- Triển khai constructor, `create_schema` và `upsert` trong starter/src/store.py.
- Tạo bảng public.day6_chunks trong database day6_lab, extension pgvector 0.8.7,
  PostgreSQL 16.16. Không xóa bảng/volume có sẵn.
- Bảng chứa strategy, chunk_id, document_id, source, page, text, metadata JSONB,
  embedding vector(384) và updated_at. Khóa chính (strategy, chunk_id) ngăn trùng.
- Tạo index thông thường cho strategy/document và strategy/section để phục vụ lọc.
  Chưa tạo HNSW/IVFFlat; dự kiến tìm chính xác bằng cosine ở bước truy xuất sau.
- Gắn cấu hình embedding đã chốt vào metadata.embedding_model của mỗi bản ghi,
  giữ nguyên metadata và text trong các file chunk gốc.
- Viết starter/scripts/ingest_vectors.py: kiểm tra checksum chunk/vector và cấu hình,
  đối chiếu thứ tự chunk ID, shape, finite và norm trước khi nhập.

Tham khảo kỹ thuật: https://github.com/pgvector/pgvector và
https://www.psycopg.org/psycopg3/docs/basic/adapt.html#json-adaptation.
Vector được bind dưới dạng chuỗi tham số rồi cast `%s::vector`; metadata dùng Jsonb.
Không nối dữ liệu người dùng vào câu SQL. Connection URL chỉ đọc từ .env, không ghi báo cáo.

## Cập nhật dữ liệu và chống trùng

Mỗi lệnh upsert là snapshot đầy đủ của từng document được gửi cho một strategy:
validate toàn bộ input, lấy khóa bảng để tránh nhập đồng thời xung đột, INSERT ON
CONFLICT UPDATE, xóa chunk cũ của các document đó không còn thuộc snapshot. Tất cả
nằm trong một transaction; lỗi sẽ rollback. Document/strategy khác không bị xóa.
Không gọi theo từng batch thiếu một phần document. Input rỗng bị từ chối thay vì
ngầm xóa tài liệu; việc xóa hẳn tài liệu cần thao tác riêng có phạm vi rõ ràng.

ID ổn định được tạo ở bước chunking. Khi tài liệu hoặc chunking đổi, chunk ID mới
được nhập và chunk cũ trong cùng phạm vi được dọn. Trước khi đổi model/corpus cần
tạo lại vector và ghi phiên bản; script không âm thầm dùng vector khác config.

## Kết quả chạy thực tế

| Kiểm tra | A | B |
|---|---:|---:|
| Bản ghi sau nạp | 237 | 270 |
| Bản ghi sau nạp lại | 237 | 270 |
| Trang nguồn phân biệt | 38 | 38 |
| Số chiều vector | 384 | 384 |
| Thời gian nạp lần đầu trong lần kiểm tra | 0,225 giây | 0,220 giây |

Tổng A/B: 507 bản ghi. Thời gian trên chỉ gồm upsert, không gồm embedding, kiểm tra
hash, tạo bảng hoặc kiểm chứng lại. Các lần chạy sau có thể khác theo tải máy.

Đọc lại bằng kết nối mới: mọi ID/text/metadata trùng đầu vào, vector khớp dung sai
atol=1e-7, rtol=1e-6. Không mất độ chính xác đáng kể ngoài biểu diễn float32.
Nạp lại không nhân đôi. Kiểm tra snapshot thử riêng bằng vector thật từ A:
2 chunk → 1 chunk, chunk cũ bị loại; dữ liệu thử đã dọn. Sai số chiều bị từ chối
trước khi thay đổi dữ liệu. Không có vector giả thay cho model thật.

Không nhập bản sao C; sẽ tái sử dụng B và chỉ đổi filter khi truy xuất. Chưa chạy
query top-3, chưa đọc benchmark để xếp hạng và chưa tạo điểm retrieval.

## Lỗi gặp và xử lý

Lần chạy đầu timeout tại kết nối, trước tạo bảng. Kiểm tra Docker cho thấy container
đã dừng với exit code 0, OOMKilled=false; chưa xác định nguyên nhân dừng. Khởi động
lại bằng Compose rồi chạy nhập thành công. Không đổi URL hay xóa volume.

## Cách chạy

Từ thư mục starter/:

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 scripts/ingest_vectors.py
```

Kết quả đầy đủ: results/storage_check.json. Script không log .env hoặc mật khẩu.
Dữ liệu lưu trong Docker volume day6_student_starter_pg_data. Dừng container không
xóa volume; tránh `down -v`. Nếu container/WSL dừng, khởi động lại trước khi dùng.
