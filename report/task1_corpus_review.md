# Báo cáo nhiệm vụ 1: lựa chọn và kiểm tra corpus

Ngày kiểm tra: 2026-11-13 (Asia/Saigon).

## Kết luận

Corpus được chọn đáp ứng yêu cầu chuẩn bị dữ liệu của nhiệm vụ 1: 38 trang nội dung
từ một PDF 82 trang, có văn bản trích xuất được, nguồn chính thức, ghi nhận quyền
sử dụng và metadata phục vụ filter. Phạm vi là **các chương trình và giải pháp
chuyển dịch năng lượng trong ESMAP Annual Report 2021**.

Tài liệu là báo cáo thường niên có nội dung kỹ thuật/chính sách năng lượng, không
phải manual phần mềm. README/GUIDE của lab cho phép dùng báo cáo thường niên.
Kết luận này không có nghĩa pipeline, benchmark hoặc các nhiệm vụ khác đã hoàn thành.

## Những gì đã làm và phương pháp

1. Kiểm kê file trong `data/raw/`, đọc metadata và toàn bộ 82 trang bằng pypdf 6.21.4.
2. Tìm trang công bố chính thức trên World Bank và tải lại bản PDF vào thư mục tạm.
   SHA-256 của bản tải chính thức trùng hoàn toàn với file người học cung cấp:
   `e49c65cc3d0d0e234a81d9a4f7f5dbc397df3a997c7f772dd2771948ad924b29`.
   File có kích thước 4.459.648 byte. Không thay đổi PDF gốc.
3. Đọc trang quyền sử dụng (PDF 2) và mục lục (PDF 4–5). Ghi nhận CC BY 3.0 IGO,
   yêu cầu ghi nguồn và các ngoại lệ ảnh/nội dung bên thứ ba. Tạo `data/ATTRIBUTION.md`.
4. Chọn sáu nhóm nội dung năng lượng theo mục lục/heading; loại các trang mở đầu
   thiên về ảnh và phần ngoài phạm vi. Ghi quyết định cho từng trang trong inventory.
5. Chuẩn hóa Unicode NFC, khoảng trắng ngang, bỏ khoảng trắng đầu/cuối dòng và
   giảm dòng trống liên tiếp. Giữ xuống dòng để còn kiểm tra cấu trúc.
6. Xuất mỗi trang được chọn thành một bản ghi JSONL có ID, nguồn, số trang và metadata.
   Không chia chunk, không dịch nội dung và không tạo embedding trong nhiệm vụ này.
7. Kiểm tra tự động: số trang, văn bản rỗng, lỗi trích xuất, ký tự thay thế U+FFFD,
   trang trùng văn bản và thống kê độ dài.
8. Render 11 trang bằng Poppler 24.02.0 và xem trực tiếp để đối chiếu bố cục với text:
   PDF 2, 4, 24, 28, 38, 43, 44, 50, 57, 62, 65.

## Phạm vi và cách đếm trang

| Mục (`section`) | Trang PDF vật lý | Trang in trên tài liệu | Số trang |
|---|---|---|---:|
| Energy Data | 23–25 | 15–17 | 3 |
| Foundations of Energy Transition | 27–35 | 19–27 | 9 |
| Accelerating Decarbonization | 37–43 | 29–35 | 7 |
| Clean Cooking | 45–47 | 37–39 | 3 |
| Electricity Access | 49–55 | 41–47 | 7 |
| Renewable Energy | 57–65 | 49–57 | 9 |
| **Tổng** | | | **38** |

Dùng số trang PDF bắt đầu từ 1, không dùng số thứ tự bắt đầu từ 0 của thư viện.
Trong phạm vi chọn, số trang in bằng số trang PDF trừ 8.
Các trang phụ về giới và năng lượng (PDF 32–35) nằm trong nhóm Foundations theo
vị trí trong tài liệu; `section` biểu thị vị trí chứ không phải mọi chủ đề được nhắc đến.

Không tính bìa, trang bản quyền, mục lục, danh mục viết tắt, donor logos, trang
mở đầu chủ yếu là ảnh và trang cuối không trích xuất được text. Các phần tổng quan,
đối tác, quỹ và tài chính nằm ngoài corpus được chọn. **Không khẳng định mọi trang
bị loại đều là trang không hợp lệ**; phạm vi chọn hẹp hơn toàn bộ nội dung báo cáo.

Các trang 38, 43, 62, 65 có ảnh lớn nhưng vẫn có các đoạn văn độc lập mô tả giải pháp,
điều kiện hoặc dự án, nên được giữ. Ví dụ PDF 65 giải thích nguyên lý thủy điện tích năng
và mô tả dự án. PDF 44 chủ yếu là ảnh mở đầu Clean Cooking nên được loại để đếm thận trọng.
Đề không quy định ngưỡng 1.500 ký tự cho mỗi trang PDF; ngưỡng đó dành cho một cách
quy đổi dữ liệu không có phân trang.

## Kết quả tự động

| Kiểm tra | Kết quả |
|---|---:|
| Trang PDF vật lý | 82 |
| Trang được chọn | 38 |
| Tổng ký tự sau chuẩn hóa trong corpus | 99.118 |
| Trang ngắn nhất / dài nhất sau chuẩn hóa | 607 / 4.325 ký tự |
| Lỗi trích xuất trên toàn PDF | 0 |
| Trang không có text trích xuất | 82, đã loại |
| Trang được chọn có ký tự U+FFFD | 0 |
| Trang được chọn trùng hoàn toàn sau chuẩn hóa | 0 |

Số ký tự gồm cả heading, header/footer và nhãn hình còn giữ trong bản text;
không phải số ký tự văn xuôi đã làm sạch hoàn chỉnh. Không có U+FFFD không chứng minh
mọi từ đều được trích xuất chính xác. Chưa dùng OCR vì các trang được chọn có text layer.

## Kiểm tra trực quan và giới hạn

- PDF 2: xác nhận trang quyền sử dụng, các ngoại lệ và mẫu attribution.
- PDF 4: xác nhận tên sáu nhóm và mối quan hệ số trang in/số trang PDF.
- PDF 24 và 50: có box và hai cột; các đoạn chữ chính đọc được nhưng thứ tự text
  không bảo toàn đầy đủ bố cục hình học, cần kiểm tra evidence theo đoạn gốc.
- PDF 28 và 57: có biểu đồ; nhãn bị đưa thành dòng text rời, không coi đó là bảng
  số liệu đã kiểm chứng. Corpus vẫn có văn xuôi hữu ích trên cùng trang.
- PDF 38, 43, 62, 65: có ảnh lớn và đoạn văn hữu ích; chỉ sử dụng phần văn bản.
- PDF 44: chủ yếu ảnh và lời dẫn ngắn, loại khỏi số trang để thận trọng.

Đây là kiểm tra tự động toàn bộ trang và đối chiếu trực quan theo mẫu, không phải
đọc soát từng từ của 38 trang. Vẫn còn header/footer, ghi công ảnh, từ ngắt dòng,
đoạn tiếp nối qua trang và nhãn biểu đồ. Cần xử lý hoặc ghi nhận ở nhiệm vụ pipeline.
Khi viết benchmark phải kiểm chứng từng evidence, đặc biệt câu có số liệu/điều kiện.
Các thông tin là theo báo cáo 2021, không phải khẳng định tình hình hiện tại.

## Nguồn và quyền sử dụng

- Nguồn: https://documents.worldbank.org/en/publication/documents-reports/documentdetail/615511640189474271
- Giấy phép được ghi trên PDF 2: https://creativecommons.org/licenses/by/3.0/igo/
- Attribution và thông báo adaptation được lưu trong `data/ATTRIBUTION.md`.
- Không xuất ảnh; PDF gốc và ảnh render cục bộ được `.gitignore` bỏ qua. Người chấm
  có thể tải PDF từ link chính thức và kiểm tra SHA-256. Không xóa file gốc trên máy.
- Các thành phần có nguồn bên thứ ba cần được xem riêng trước khi tái sử dụng;
  không coi giấy phép chung là quyền tự động đối với mọi thành phần.
- Ngày tải ban đầu của người học chưa biết. Ngày 2026-11-13 chỉ là ngày xác minh
  nguồn trong lần làm này, đã ghi rõ trong manifest.

## Metadata đã chuẩn bị

- `document_id`: string ổn định `esmap-annual-report-2021`.
- `source`: string, URL PDF chính thức.
- `page`: integer, số trang PDF vật lý, phục vụ truy nguồn.
- `printed_page`: string, số trang in để đối chiếu khi đọc thủ công.
- `section`: string, sáu giá trị từ cấu trúc thật của tài liệu, là trường filter chính.
- `report_year`: integer 2021, `language`: string `en`, `document_type`: string
  `annual_report`; là metadata mô tả, không phân biệt được phạm vi trong một tài liệu này.

Đủ sáu giá trị section để thiết kế câu filter sau này. Filter chỉ dùng khi phạm vi
được người hỏi/ngữ cảnh cung cấp trước, không lấy section từ đáp án gold.
Mục này chưa chứng minh filter cải thiện retrieval; điều đó cần đo bằng benchmark.

## Tái lập và file đầu ra

Từ thư mục gốc repo:

```powershell
.\starter\.venv\Scripts\python.exe -X utf8 starter/scripts/audit_corpus.py --verified-at 2026-11-13
```

Ngày truyền vào là ngày xác minh nguồn thực tế của snapshot này.
Script xuất `data/manifest.json`, `data/page_inventory.json`,
`data/processed/esmap_pages.jsonl` và `results/task1_audit.json`.
Kết quả đối chiếu nguồn nằm trong `results/task1_source_verification.json`.

Poppler được cài trong Ubuntu WSL bằng `apt-get install -y poppler-utils` chỉ để
render kiểm tra. Ví dụ render PDF 24 từ thư mục gốc repo sau khi đã tạo `tmp/pdfs/`:

```powershell
wsl -d Ubuntu -- pdftoppm -f 24 -l 24 -scale-to 1300 -singlefile -png data/raw/Energy-Sector-Management-Assistance-Program-ESMAP-Annual-Report-2021.pdf tmp/pdfs/page-24
```

Công cụ AI hỗ trợ: Codex đã viết script audit và tài liệu ghi nhận, chạy trích xuất,
đối chiếu nguồn/mã băm và xem ảnh render theo mẫu. Chưa tạo nhãn benchmark hay
kết quả retrieval; các kiểm tra hiện tại chỉ phục vụ nhiệm vụ 1.

Bước tiếp theo là xây bộ câu hỏi và gold evidence trước khi thử cấu hình retrieval.
