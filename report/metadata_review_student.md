# Audit metadata test — kết quả kiểm tra của học viên

Người kiểm tra: **Phạm Tuấn Anh**. Ngày ghi nhận: 13/11/2026.

Học viên báo đã kiểm tra đủ 45 bản ghi, không phát hiện lỗi. Codex ghi nhận kết quả
và kiểm tra kỹ thuật bổ sung trên PDF gốc/manifest, không thay đổi nhận xét của học viên.

| Strategy | Metadata đủ và đúng | Lỗi được học viên báo |
|---|---|---|
| A | 15/15 (100%) | Không |
| B | 15/15 (100%) | Không |
| C | 15/15 (100%) | Không |

Kiểm tra document_id, source, page và metadata.section. Tất cả ID tài liệu là
esmap-annual-report-2021, source khớp source_path_or_url, section khớp khoảng trang
content_page_ranges. Codex cũng đối chiếu từng text với lát cắt trang PDF gốc theo
offset: 45/45 khớp. Bản ghi chi tiết: results/test/student_review/metadata_audit.json.

Học viên nêu quy đổi trang in Ả Rập = trang PDF vật lý - 8 (ví dụ PDF 38 → 30,
PDF 41 → 33, PDF 62 → 54). Quy đổi dùng để đối chiếu với PDF; không phải chunk nào
cũng chứa số trang in, vì chunking có thể tách phần thân văn bản khỏi header/footer.

## Filter và tính hữu dụng

Học viên lưu ý q20 A/B có applied_filter=null và trả chunk ngoài section yêu cầu.
Đây là **đúng thiết kế A/B không filter**, không phải lỗi triển khai. Metadata từng
chunk vẫn có thể đúng dù chunk không liên quan câu hỏi hoặc không tuân thủ phạm vi.
Theo trace, trên hai câu test có filter: A=1/2, B=1/2, C=2/2 lượt có top-3 tuân thủ.

Phân tích của Codex bổ sung từ kết quả học viên: source/page giúp truy về tài liệu
để xác minh, section giúp C giới hạn phạm vi. Hạn chế: metadata đúng/đủ không bảo đảm
chunk chứa đủ evidence; C ở q20 vẫn thiếu điều kiện sau khi đánh giá kỹ thuật hoàn tất.
Tỷ lệ 100% chỉ áp dụng 45 bản ghi đã kiểm tra, không suy rộng mọi dữ liệu.

Đã giữ nguyên baseline, cấu hình và lựa chọn C. Không chạy lại test.
