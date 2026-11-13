# Nhiệm vụ 3, bước 3: embedding local

## Model và lý do chọn

Chọn `intfloat/multilingual-e5-small`, revision
`614241f622f53c4eeff9890bdc4f31cfecc418b3`, bản chính thức `onnx/model.onnx` FP32,
không quantization. Chạy ONNX Runtime CPU trên máy AMD Ryzen 5 5500U, khoảng 8 GB RAM.
Model đa ngữ phù hợp thử truy vấn tiếng Việt trên tài liệu tiếng Anh; không khẳng định
chất lượng retrieval trước khi đo. Nguồn kỹ thuật:
https://huggingface.co/intfloat/multilingual-e5-small và thư mục onnx của cùng repo.
Metadata repo ghi giấy phép MIT; quyền corpus được ghi riêng ở data/ATTRIBUTION.md.

Theo model card: vector 384 chiều, tiền tố `passage: ` cho document, `query: ` cho
query, attention-mask mean pooling và chuẩn L2. Giới hạn 512 token tính cả prefix
và token đặc biệt. Không silently truncate; đầu vào quá giới hạn báo lỗi.

## Đã triển khai

- `starter/src/embeddings.py`: adapter `MyEmbedder`, load model local, kiểm chứng
  SHA-256 model/tokenizer trước khi dùng, xử lý batch và query theo cùng cấu hình.
- `starter/scripts/download_embedding_model.ps1`: tải đúng revision bằng HTTPS,
  kiểm tra SHA-256, chỉ đổi file .part thành file hoàn chỉnh khi xác minh thành công.
- `artifacts/embedding_config.json`: lưu đầy đủ provider local, revision, file,
  hash, prefix, dimensions, pooling, normalization, batch 8 và 4 CPU threads.
- `starter/scripts/embed_chunks.py`: chỉ đọc chunk A/B, tạo vector, kiểm tra và
  lưu NPZ có `vectors` và `chunk_ids`. Không đọc benchmark, expected_answer, evidence
  hoặc test; không tính similarity/ranking. Có query smoke riêng và kiểm tra batch.
- Cập nhật requirements và lưu requirements-lock.txt để ghi đúng phiên bản đã cài.

Model/tokenizer tải tổng khoảng 487 MB, nằm trong models/ đã được Git bỏ qua.
Hash và link tải cho phép tái lập, không cần đưa trọng số lớn lên repo.

## Kết quả thực chạy

| Chỉ số | A | B |
|---|---:|---:|
| Số chunk/vector | 237 | 270 |
| Số chiều | 384 | 384 |
| Kiểu dữ liệu | float32 | float32 |
| Thời gian embedding CPU | 9,842 giây | 10,044 giây |
| Tổng token gồm prefix/token đặc biệt | 24.853 | 22.587 |
| Token lớn nhất mỗi đầu vào | 140 | 123 |
| Đầu vào bị cắt | 0 | 0 |
| Phí dịch vụ embedding | 0 USD | 0 USD |

Nạp model khoảng 3,204 giây; tổng script khoảng 23,325 giây. Thời gian này không
gồm tải model/cài thư viện, đọc PDF/chia chunk hoặc ingest database. Chi phí 0 là phí
dịch vụ API; không bao gồm điện, mạng và phần cứng. Phiên bản đã chạy: Python 3.11.9,
NumPy 2.4.6, ONNX Runtime 1.31.1, tokenizers 0.23.3.

Đã kiểm tra shape, giá trị hữu hạn, norm gần 1, số token không vượt 512, query vector
384 chiều cùng norm, và cùng một document chạy riêng/batch khớp trong dung sai 1e-5.
Đầu vào rỗng/blank và quá giới hạn được kiểm tra, không chuyển sang mock.

Các vector ở cùng không gian biểu diễn vì dùng cùng model, revision, tokenizer,
pooling và normalization. C sẽ dùng lại vector B; filter chỉ áp dụng khi truy vấn store.

## Chạy lại và xem kết quả

Từ thư mục gốc repo, sau khi cài requirements:

```powershell
.\starter\scripts\download_embedding_model.ps1
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/embed_chunks.py
```

Đầu ra: results/embeddings/vectors_A.npz, vectors_B.npz, summary.json,
query_smoke.json, embedding.log. summary lưu hash input chunk và output vector để
đối chiếu phiên bản. Khi load dùng `np.load(path, allow_pickle=False)`; hàng thứ i
của vectors tương ứng chunk_ids[i]. Nội dung/metadata xem ở file chunk cùng strategy.

Đây mới là vector trung gian, chưa phải vector store. Chưa ghi pgvector, chạy top-3,
đánh giá retrieval hoặc chọn lại chiến lược theo test. Hiệu quả đa ngữ phải được
đánh giá ở các bước sau. Chạy lại CPU có thể sai khác số thực nhỏ; dùng dung sai hợp lý.
