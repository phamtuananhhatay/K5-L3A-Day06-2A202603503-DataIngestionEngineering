# Kết quả dev — A/B/C

Chấm tự động bảo thủ bằng toàn bộ quote trong một chunk đúng nguồn/trang; chưa chấm tương đương ngữ nghĩa hoặc grounding thủ công.

| Strategy | Hit@1 | Evidence Hit@3 | Top-3 tuân thủ filter yêu cầu |
|---|---|---|---|
| A | 5/15 (33.3%) | 7/15 (46.7%) | 3/6 (50.0%) |
| B | 7/15 (46.7%) | 9/15 (60.0%) | 3/6 (50.0%) |
| C | 8/15 (53.3%) | 9/15 (60.0%) | 6/6 (100.0%) |

A/B không áp dụng filter; compliance đo mức khớp phạm vi được câu hỏi yêu cầu. C có áp dụng filter.

| Câu | Strategy | Trang top-3 | Hit@1 | Hit@3 | Chẩn đoán |
|---|---|---|---|---|---|
| q01 | A | 28, 65, 57 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q01 | B | 38, 52, 62 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q01 | C | 62, 65, 57 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q02 | A | 24, 24, 23 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q02 | B | 24, 24, 23 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q02 | C | 24, 24, 23 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q03 | A | 24, 25, 53 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q03 | B | 38, 51, 42 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q03 | C | 38, 51, 42 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q04 | A | 29, 29, 27 | 1 | 1 | complete_recorded_evidence_found |
| q04 | B | 38, 29, 27 | 0 | 1 | complete_recorded_evidence_found |
| q04 | C | 29, 27, 31 | 1 | 1 | complete_recorded_evidence_found |
| q05 | A | 30, 30, 31 | 1 | 1 | complete_recorded_evidence_found |
| q05 | B | 30, 30, 38 | 1 | 1 | complete_recorded_evidence_found |
| q05 | C | 30, 30, 38 | 1 | 1 | complete_recorded_evidence_found |
| q06 | A | 32, 32, 32 | 1 | 1 | complete_recorded_evidence_found |
| q06 | B | 32, 32, 35 | 1 | 1 | complete_recorded_evidence_found |
| q06 | C | 32, 32, 35 | 1 | 1 | complete_recorded_evidence_found |
| q07 | A | 38, 38, 65 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q07 | B | 38, 38, 42 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q07 | C | 38, 38, 42 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q08 | A | 40, 28, 31 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q08 | B | 38, 52, 40 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q08 | C | 38, 52, 40 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q09 | A | 47, 47, 52 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q09 | B | 38, 43, 47 | 0 | 1 | complete_recorded_evidence_found |
| q09 | C | 38, 43, 47 | 0 | 1 | complete_recorded_evidence_found |
| q10 | A | 47, 47, 46 | 0 | 1 | complete_recorded_evidence_found |
| q10 | B | 46, 46, 47 | 1 | 1 | complete_recorded_evidence_found |
| q10 | C | 46, 46, 47 | 1 | 1 | complete_recorded_evidence_found |
| q11 | A | 47, 47, 45 | 0 | 1 | complete_recorded_evidence_found |
| q11 | B | 47, 47, 47 | 1 | 1 | complete_recorded_evidence_found |
| q11 | C | 47, 47, 47 | 1 | 1 | complete_recorded_evidence_found |
| q12 | A | 50, 49, 47 | 1 | 1 | complete_recorded_evidence_found |
| q12 | B | 50, 47, 38 | 1 | 1 | complete_recorded_evidence_found |
| q12 | C | 50, 49, 52 | 1 | 1 | complete_recorded_evidence_found |
| q13 | A | 29, 23, 47 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q13 | B | 38, 23, 60 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q13 | C | 38, 23, 60 | 0 | 0 | gold_source_page_absent_from_top3; review possible alternative evidence |
| q14 | A | 54, 24, 50 | 1 | 1 | complete_recorded_evidence_found |
| q14 | B | 54, 38, 25 | 1 | 1 | complete_recorded_evidence_found |
| q14 | C | 54, 38, 25 | 1 | 1 | complete_recorded_evidence_found |
| q15 | A | 61, 61, 52 | 0 | 0 | gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence |
| q15 | B | 61, 61, 38 | 1 | 1 | complete_recorded_evidence_found |
| q15 | C | 61, 61, 38 | 1 | 1 | complete_recorded_evidence_found |
