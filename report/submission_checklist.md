# Checklist bài nộp — Phạm Tuấn Anh, 2A202603503, L3A

Đối chiếu với [SUBMISSION.md](../SUBMISSION.md). Đây là trạng thái chuẩn bị file
trong workspace và kết quả push đã xác minh; không phải xác nhận đã nộp link cho lớp.

| Yêu cầu | Trạng thái | Minh chứng |
|---|---|---|
| ≥30 trang nội dung, nguồn/quyền và cách tính | Đã có, 38 trang | data/manifest.json, data/ATTRIBUTION.md, data/page_inventory.json |
| ≥20 câu, evidence, ≥15 dev/5 test | Đã có | benchmark/questions.json, benchmark/manifest.json |
| Câu kiểm tra filter, gồm test | Đã có, 8 câu/2 test | benchmark/questions.json |
| Embedding thật + persistent vector store/filter | Đã có | starter/src/embeddings.py, store.py; results/embeddings/summary.json, storage_check.json |
| 3 cấu hình và so sánh kiểm soát | Đã có | artifacts/chunking_config.json; C dùng vector B, chỉ thay filter |
| Trace top-3, chỉ số dev/test, chi phí/thời gian | Đã có | results/dev/, results/test/, results/embeddings/summary.json |
| Audit thủ công và phân tích 5 khía cạnh | Đã có | report/individual/2A202603503_PhamTuanAnh.md và ba báo cáo audit của học viên |
| Code, lệnh chạy, manifest, experiment log | Đã chuẩn bị | README.md, starter/, artifacts/experiment_log.csv |
| Báo cáo cá nhân đúng tên | Đã có | report/individual/2A202603503_PhamTuanAnh.md |
| Thông tin học viên | Đã điền | STUDENT.md |
| Secret/dữ liệu lớn không đi vào Git | Xem kết quả kiểm tra cuối | results/submission_check.json, .gitignore |
| Commit chứa toàn bộ bài làm, push lên origin | **Đã hoàn thành và xác minh** | Commit nội dung f534e5fa899140ddfdd6dc1387573f4ff019b452 trên origin/main; artifacts/publication.json |
| Người chấm truy cập được repo | **Chưa xác minh** | Cần kiểm tra quyền repo khi nộp |
| Nộp link theo kênh lớp | **Chưa thực hiện** | Học viên nộp theo yêu cầu giảng viên/coach |

Repo hiện tại: https://github.com/phamtuananhhatay/K5-L3-Day06-2A202603503-DataIngestionEngineering

Kiểm tra hoàn thiện file: 13/13 unittest đạt; kiểm tra CLI có tùy chọn output riêng
cho tái lập; các đường dẫn báo cáo chính hợp lệ, nhật ký CSV khớp số liệu reviewed,
26 file frozen giữ nguyên hash. Kết quả chi tiết ở results/submission_check.json.
Quét mẫu credential trên các file ứng viên Git không phát hiện trùng mẫu; đây không
phải bảo đảm tuyệt đối mọi nội dung đều không nhạy cảm. .env/model/PDF gốc/venv/tmp
được bỏ qua bởi .gitignore.

Không đổi tên repo chỉ để theo tên gợi ý nếu lớp không bắt buộc. Deadline theo thông
báo lớp, không tự suy từ thời lượng 4 giờ/checkpoint. Không tự gán commit khung ban đầu
là commit chốt bài. STUDENT.md đã ghi commit nội dung thực tế; commit tài liệu tiếp
theo bổ sung trạng thái push mà không thay cấu hình hoặc kết quả đánh giá.

Trước commit, xem `git status --short` và kiểm tra danh sách file sẽ đưa lên. Không thêm
`.env`, `.venv`, `models/`, PDF gốc hoặc `tmp/`. Dữ liệu/model tái lập qua URL/hash.
Các báo cáo dùng thông tin cá nhân Phạm Tuấn Anh/MSSV theo yêu cầu của học viên.
