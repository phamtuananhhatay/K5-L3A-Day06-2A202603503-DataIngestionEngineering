# Corpus cho bài lab

Chủ đề: các chương trình và giải pháp chuyển dịch năng lượng trong báo cáo ESMAP 2021.
Đây là báo cáo thường niên có nội dung kỹ thuật/chính sách năng lượng, không phải
manual phần mềm. Đề lab cho phép dùng báo cáo thường niên.

## Nguồn và cách lấy

- [Trang nguồn World Bank](https://documents.worldbank.org/en/publication/documents-reports/documentdetail/615511640189474271)
- [PDF chính thức](https://documents1.worldbank.org/curated/en/615511640189474271/pdf/Energy-Sector-Management-Assistance-Program-ESMAP-Annual-Report-2021.pdf)
- Lưu PDF vào `data/raw/Energy-Sector-Management-Assistance-Program-ESMAP-Annual-Report-2021.pdf`.
- SHA-256: `e49c65cc3d0d0e234a81d9a4f7f5dbc397df3a997c7f772dd2771948ad924b29`.
- Đối chiếu bản chính thức ngày 2026-11-13: trùng mã băm với file người học cung cấp.
- Không suy ra ngày người học tải file từ thời gian sửa file. `accessed_at` trong
  manifest là ngày xác minh nguồn của lần audit này.

## Phạm vi được chọn

PDF có 82 trang vật lý. Corpus dùng 38 trang: **23–25, 27–35, 37–43,
45–47, 49–55, 57–65**. Dùng số thứ tự PDF bắt đầu từ 1. Trong các khoảng này,
số trang in trên tài liệu bằng số trang PDF trừ 8.

Mỗi trang được giữ nguyên danh tính nguồn, không nhân bản và không chia lại để
tăng số trang. Xem `page_inventory.json` để biết lý do chọn/loại từng trang.
Trang bị loại không nhất thiết không hợp lệ: nhiều trang được loại vì nằm ngoài
phạm vi chủ đề đã chọn.

## Các file

- `manifest.json`: nguồn, quyền sử dụng, snapshot, phạm vi, số ký tự và metadata.
- `page_inventory.json`: kiểm tra toàn bộ 82 trang và lý do chọn/loại.
- `processed/esmap_pages.jsonl`: 38 trang văn bản được trích xuất và chuẩn hóa sơ bộ.
- `ATTRIBUTION.md`: ghi nguồn và điều kiện sử dụng.
- `../results/task1_audit.json`: kết quả kiểm tra tự động.
- `../results/task1_source_verification.json`: kết quả đối chiếu nguồn chính thức.
- `../report/task1_corpus_review.md`: cách làm, kết luận và giới hạn kiểm tra.

## Tái tạo kết quả kiểm tra

Từ thư mục gốc repo, sau khi có PDF và môi trường Python của starter:

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/audit_corpus.py --verified-at 2026-11-13
```

Khi xác minh lại nguồn vào ngày khác, thay ngày trong lệnh bằng ngày xác minh thực tế.
Script dùng `pypdf` trong `starter/requirements.txt`, không cần OCR hoặc embedding.
Các ranh giới mục là cấu hình riêng cho tài liệu này, không phải bộ nhận diện mục tự động.

## Metadata để dùng tiếp

`document_id` (string), `source` (string URL), `page` (integer, trang PDF vật lý),
`printed_page` (string) giúp truy nguồn. `section` (string) có sáu giá trị lấy từ
mục lục và heading thật: Energy Data; Foundations of Energy Transition;
Accelerating Decarbonization; Clean Cooking; Electricity Access; Renewable Energy.

`section` là trường lọc chính. `report_year=2021`, `language=en`,
`document_type=annual_report` là thông tin mô tả; vì corpus chỉ có một tài liệu,
ba trường này không giúp phân biệt kết quả trong corpus hiện tại.
Một trang có thể nhắc chủ đề thuộc mục khác; `section` chỉ chỉ vị trí trong báo cáo.
Chỉ áp dụng filter khi câu hỏi/ngữ cảnh chỉ rõ phạm vi, không lấy từ gold answer.

## Quyền sử dụng

Trang PDF 2 ghi CC BY 3.0 IGO và các ngoại lệ cho ảnh/nội dung bên thứ ba.
Workflow này giữ PDF gốc trên máy, bỏ qua file đó khi Git theo dõi và cung cấp link
tải để tái lập. Chỉ xuất văn bản, không xuất ảnh. Các file `tmp/pdfs/` chỉ dùng để
kiểm tra cục bộ, cũng được Git bỏ qua. Xem `ATTRIBUTION.md`.
