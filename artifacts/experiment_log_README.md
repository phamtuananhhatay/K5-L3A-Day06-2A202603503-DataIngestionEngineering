# Nhật ký thí nghiệm A/B/C

`experiment_log.csv` giữ 13 cột của mẫu đề bài, mỗi dòng là một strategy. `chunk_size`
và `overlap` tính theo ký tự Unicode. Các cột dev_hit1/dev_hit3/test_hit1/test_hit3
là tỷ lệ số thực 0–1, không phải số câu. Dev là kết quả sau rà soát được học viên xác
nhận; test là kết quả học viên rà soát trùng baseline. Tử/mẫu được ghi trong notes.

Giả thuyết trong cột hypothesis được tổng hợp lại **khi hoàn thiện bài nộp**, sau
khi có kết quả. File khung trước đó chưa điền, nên không coi thời điểm điền log là
bằng chứng đăng ký trước giả thuyết. Cấu hình và quy tắc chọn được ghi riêng trong
benchmark/manifest.json và artifacts/frozen_pipeline.json, có trước chạy test.

Nguồn số liệu:

- `results/dev/reviewed/summary.json`: dev sau review, A 6/15–8/15, B 8/15–10/15,
  C 9/15–10/15 (Hit@1–Hit@3).
- `results/test/student_review/summary.json`: test học viên xác nhận, A 0/5–1/5,
  B/C 1/5–2/5.
- `artifacts/chunking_config.json`, `artifacts/embedding_config.json`: tham số.

C tái sử dụng vector B; không cộng trùng chi phí embedding C. File CSV là bảng
snapshot kết quả thực tế để chấm bài, không phải workbook công thức. Không thay nhãn
hoặc kết quả test bằng cách chỉnh giá trị trong CSV.
