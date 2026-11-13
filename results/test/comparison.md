# Kết quả test — A/B/C

Chấm tự động bảo thủ bằng toàn bộ quote trong một chunk đúng nguồn/trang; chưa chấm tương đương ngữ nghĩa hoặc grounding thủ công.

| Strategy | Hit@1 | Evidence Hit@3 | Top-3 tuân thủ filter yêu cầu |
|---|---|---|---|
| A | 0/5 (0.0%) | 1/5 (20.0%) | 1/2 (50.0%) |
| B | 1/5 (20.0%) | 2/5 (40.0%) | 1/2 (50.0%) |
| C | 1/5 (20.0%) | 2/5 (40.0%) | 2/2 (100.0%) |

A/B không áp dụng filter; compliance đo mức khớp phạm vi được câu hỏi yêu cầu. C có áp dụng filter.

| Câu | Strategy | Trang top-3 | Hit@1 | Hit@3 | Chẩn đoán |
|---|---|---|---|---|---|
| q16 | A | 23, 24, 23 | 0 | 1 | complete_recorded_evidence_found |
| q16 | B | 24, 23, 24 | 0 | 1 | complete_recorded_evidence_found |
| q16 | C | 24, 23, 24 | 0 | 1 | complete_recorded_evidence_found |
| q17 | A | 28, 31, 27 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q17 | B | 38, 27, 52 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q17 | C | 38, 27, 52 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q18 | A | 40, 41, 40 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q18 | B | 41, 41, 40 | 1 | 1 | complete_recorded_evidence_found |
| q18 | C | 41, 41, 40 | 1 | 1 | complete_recorded_evidence_found |
| q19 | A | 27, 49, 28 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q19 | B | 52, 38, 27 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q19 | C | 52, 38, 27 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q20 | A | 62, 24, 28 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q20 | B | 62, 38, 52 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q20 | C | 62, 57, 65 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
