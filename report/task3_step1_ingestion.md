# Nhiệm vụ 3, bước 1: đọc và chuẩn hóa tài liệu

Đã triển khai trong `starter/src/ingestion.py`:

- `normalize_text`: chuẩn hóa Unicode NFC, khoảng trắng, CR/LF và dòng trống;
  giữ xuống dòng và nội dung để tương thích corpus đã chốt.
- `load_pdf`: đọc toàn bộ trang vật lý, đánh số từ 1, giữ ID tài liệu và nguồn;
  ghi log trang rỗng/lỗi, lưu trạng thái trích xuất trong metadata. Lỗi mở file
  được báo ngay; không tự thay nội dung bằng OCR hoặc dữ liệu giả.
- `load_corpus`: kiểm tra SHA-256 PDF với manifest, chọn đúng trang nội dung,
  kiểm tra số lượng và gắn `section`, `report_year` từ manifest. Trang được chọn
  rỗng/lỗi hoặc không có một section duy nhất sẽ làm bước này báo lỗi.

Không tự suy ra section từ đáp án benchmark. Không thay PDF, corpus JSONL hoặc
benchmark đã cố định. Không xóa header/footer hay sửa từ ngắt dòng trong lần này;
muốn thay chính sách chuẩn hóa cần quản lý phiên bản corpus và kiểm chứng lại gold.

## Cách chạy

Từ thư mục gốc repo:

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/check_ingestion.py
```

Hoặc từ `starter/`: `.\.venv\Scripts\python.exe -X utf8 scripts/check_ingestion.py`.
Script kiểm tra đọc PDF gốc và đối chiếu nội dung, ID, URL, trang, section của cả
38 trang với snapshot đã có. Có kiểm tra tiếng Việt dạng Unicode tổ hợp và tính
ổn định khi chuẩn hóa lại cùng một văn bản.

## Kết quả chạy thực tế

- Đọc đủ 82 trang vật lý.
- Chọn 38 trang, tổng 99.118 ký tự, khớp hoàn toàn text và provenance của corpus.
- Trang 65 có section `Renewable Energy`, nội dung về thủy điện tích năng và dự án
  Indonesia. File mẫu: `results/ingestion_page65.json`.
- Trang 82 không có text: được log cảnh báo, nằm ngoài phạm vi chọn.
- Không cần OCR cho các trang được chọn.
- Chạy lại validator benchmark: 20/20 evidence có trong PDF và corpus; checksum
  của câu hỏi/corpus vẫn hợp lệ. Đây không phải kết quả retrieval.

Thống kê: `results/ingestion_check.json`. Log: `results/ingestion.log`.
Chưa chia chunk, tạo embedding, lưu database hay sửa `src/run.py`.
