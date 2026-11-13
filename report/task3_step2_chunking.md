# Nhiệm vụ 3, bước 2: chia chunk A/B

Đã triển khai `fixed_size` và `by_paragraph` trong `starter/src/chunking.py`.
Tham số ban đầu được lưu ở `artifacts/chunking_config.json`, chưa chọn bằng điểm dev/test.
Không thay đổi PDF, văn bản corpus hoặc benchmark đã chốt. Không đọc gold/test để
quyết định ranh giới chunk; chỉ đọc nội dung trang. Không tạo embedding hoặc retrieval.

## Hai cách chia

- A: cửa sổ 500 ký tự, dịch 450 ký tự, overlap 50. Cửa sổ cuối dừng tại cuối trang,
  không tạo thêm cửa sổ trùng đuôi sau khi đã phủ hết trang.
- B: nhận diện đoạn bằng dòng trống, nhận diện heading chữ hoa và giữ chuỗi heading
  nhiều dòng cùng văn bản tiếp theo nếu giới hạn cho phép. Gom các khối ngắn; khối
  quá 500 ký tự được tách ưu tiên ranh giới câu, rồi từ, cuối cùng ngắt cứng nếu cần.
  Không overlap. Cả hai cách đều không nối qua ranh giới trang nguồn.
- PDF ít giữ dòng trống phân đoạn nên B dùng heuristic và sentence fallback;
  không khẳng định đã khôi phục mọi đoạn/heading thật. Chưa chấm coherence.

Mỗi chunk giữ document_id, URL nguồn, trang PDF, section và metadata trang.
Thêm start_char/end_char theo văn bản trang (bắt đầu từ 0, cuối loại trừ), cấu hình
chunking. ID SHA-256 gồm danh tính nguồn/trang, offsets, text và tham số. Cùng đầu vào
sinh cùng ID; thay nội dung hoặc cấu hình sinh ID khác. Metadata được sao chép độc lập.
Chỉ cắt khoảng trắng đầu/cuối, giữ nguyên mọi ký tự nội dung trong phạm vi nguồn.

## Kết quả thực chạy trên 38 trang

| Chỉ số | A | B |
|---|---:|---:|
| Chunk count | 237 | 270 |
| Tổng ký tự trong các chunk | 109.015 | 98.886 |
| Ngắn nhất | 76 | 31 |
| Trung vị | 500 | 393 |
| Trung bình | 459,98 | 366,24 |
| Dài nhất | 500 | 499 |
| P10 / P90 (chọn vị trí trong danh sách độ dài đã sắp xếp) | 278 / 500 | 216 / 485 |

Corpus gốc có 99.118 ký tự. A có ký tự lặp do overlap; B bỏ khoảng trắng tại ranh giới
chunk nên tổng thấp hơn corpus. Đã kiểm tra mọi ký tự không phải khoảng trắng đều được
phủ. Số chunk nhiều hơn không tự chứng minh chất lượng tốt hơn. Vẫn có chunk ngắn,
header/footer, ghi công ảnh và giới hạn ngắt trang cần đánh giá ở bước coherence/retrieval.
Chưa đếm token vì chưa chọn tokenizer/model.

## Kiểm tra

- 7 kiểm thử unittest pass: overlap/cuối trang, đoạn, văn xuôi xuống dòng, heading
  nhiều dòng, token dài/Unicode/trang rỗng, ID/metadata, tham số không hợp lệ.
- Trên toàn corpus: xác nhận text đúng lát cắt nguồn, kích thước trong giới hạn,
  không mất ký tự nội dung, metadata đúng, ID duy nhất và chạy lại ra kết quả giống nhau.
- B không có overlap. Corpus đầu vào khớp nội dung snapshot nhiệm vụ 1.
- Xem trực tiếp mẫu trang 65 để phát hiện heading bị tách riêng; đã điều chỉnh xử lý
  heading nhiều dòng trước khi chốt output. Đây là kiểm tra cấu trúc, không dùng điểm test.

## Cách chạy và đầu ra

Từ thư mục gốc repo:

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/check_chunking.py
```

Chạy kiểm thử từ thư mục `starter/`:

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
```

Đầu ra trong `results/chunking/`: `chunks_A.jsonl`, `chunks_B.jsonl`, `summary.json`
và bản dễ đọc `page65_comparison.md`. Ghi nguồn/giấy phép của text kế thừa
`data/ATTRIBUTION.md`. C dự kiến tái dùng B và chỉ thay metadata filter lúc truy xuất.
Chưa đo thời gian ingest/chi phí embedding/database vì các bước đó chưa triển khai.
