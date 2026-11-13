# Nhiệm vụ 3, bước 5: cosine top-3 và metadata filter

## Triển khai

- `starter/src/store.py`: `search` kiểm tra strategy A/B/C, vector đúng 384 chiều,
  hữu hạn/khác zero, top_k nguyên dương, tên và kiểu của filter.
- C dùng dữ liệu B đã lưu; không tạo thêm bản sao vector. Hàm store hỗ trợ filter
  equality AND theo section, report_year, document_id, source, page.
- SQL dùng `embedding <=> query_vector` (cosine distance); score = 1 - distance.
  Filter được áp dụng vào candidates trước khi tính và sắp hạng. Candidates là CTE
  MATERIALIZED để giữ exact search, không dùng ANN. Sắp distance tăng dần rồi chunk_id.
- Tất cả giá trị SQL bind bằng tham số; tên cột chỉ lấy từ allowlist. Không nối
  filter của người dùng vào SQL. Filter không khớp không được bỏ qua.
- Kết quả có rank, strategy yêu cầu/stored_strategy, ID, text, source, trang,
  metadata, cosine_distance, score và score_type.
- `starter/scripts/search_chunks.py`: CLI tạo query vector cùng model đã chốt,
  kiểm tra config model trong database, gọi store, in JSON và tùy chọn lưu trace.
  A/B không chấp nhận --section; C áp dụng section khi được người dùng cung cấp.
- `starter/scripts/check_search.py`: kiểm tra tích hợp read-only, không đọc benchmark
  hoặc gold và không ghi dữ liệu vào database.

Tài liệu toán tử/định nghĩa score: https://github.com/pgvector/pgvector#querying.
Score cao hơn thể hiện gần hơn trong không gian embedding, không phải phần trăm
đúng, xác suất hoặc bằng chứng đủ trả lời.

## Kiểm chứng đã chạy

Model thật: intfloat/multilingual-e5-small, revision và tiền tố theo config đã chốt.
Câu thử: “Báo cáo mô tả các giải pháp lưu trữ năng lượng như thế nào?”

| Trường hợp | Trang PDF trong top-3 |
|---|---|
| A, không filter | 53, 27, 24 |
| B, không filter | 27, 53, 24 |
| C, không filter | 27, 53, 24 |
| C, section Renewable Energy | 59, 57, 63 |
| C, section Renewable Energy và report_year 2021 | 59, 57, 63 |

Đây là smoke test kỹ thuật, chưa chấm độ đúng hoặc đủ evidence. Không dùng kết quả
này để tuyên bố B/C tốt hơn A. Truy vấn rộng có thể trả chunk chưa đủ bằng chứng;
chất lượng phải được đánh giá bằng bộ benchmark và audit thủ công sau.

Các kiểm tra đều pass:

- A/B/C trả top-3 đúng cấu trúc và score giảm dần.
- C không filter trùng B về thứ tự ID.
- Section và filter kết hợp đều được tuân thủ.
- Thứ hạng và score B/C khớp cosine tính độc lập bằng NumPy trên vector đã lưu
  (dung sai score 1e-5). NumPy chỉ phục vụ kiểm tra, không thay vector store ứng dụng.
- Filter không tồn tại hoặc chuỗi `Renewable Energy' OR 1=1 --` trả rỗng.
- Chọn trang có ít ứng viên từ thống kê chunk, không từ gold: PDF 43 có 2 chunk B,
  tìm kiếm trả đúng 2 kết quả, không lấy thêm ngoài phạm vi.
- Query sai số chiều, vector zero/NaN, top_k=0, filter sai kiểu hoặc key lạ bị từ chối.

Database không thay đổi. Không chạy bộ benchmark dev/test, không sinh Hit@1/Hit@3
hoặc nhãn coherence/grounding. Không điều chỉnh cấu hình dựa vào test.

## Chạy lại

Từ thư mục starter/:

```powershell
wsl -d Ubuntu -- docker compose -p day6_student_starter up -d --wait
.\.venv\Scripts\python.exe -X utf8 scripts/check_search.py
.\.venv\Scripts\python.exe -X utf8 scripts/search_chunks.py --strategy C --section "Renewable Energy" --question "Báo cáo mô tả các giải pháp lưu trữ năng lượng như thế nào?" --output ../results/search/example_C.json
```

Kết quả: results/search/check_summary.json, smoke_traces.json và example_C.json.
Không cần tạo lại embedding hoặc nhập lại database. Nếu container WSL đã dừng,
khởi động ngay trước khi chạy lệnh. Chưa hoàn thiện src/run.py và evaluation.py.
