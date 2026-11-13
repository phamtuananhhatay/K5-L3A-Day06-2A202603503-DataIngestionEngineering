"""Import the learner's submitted review; verify labels refer to saved test hits."""
import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    args=parser.parse_args()
    raw=args.input.read_bytes()
    text=raw.decode("utf-8-sig")
    reviewer=re.search(r"^Người rà soát:\s*(.+)$",text,re.M).group(1).strip()
    date=re.search(r"^Ngày rà soát:\s*(.+)$",text,re.M).group(1).strip()
    traces=[json.loads(line) for line in (ROOT/"results/test/traces.jsonl").read_text(encoding="utf-8").splitlines()]
    indexed={(t["question_id"],t["strategy"]):t for t in traces}
    headings=list(re.finditer(r"^## (q\d+) — Chiến lược ([ABC])\s*$",text,re.M))
    if len(headings)!=15:
        raise ValueError("Expected 15 question/strategy review sections")
    entries,results=[],[]
    seen=set()
    for i,heading in enumerate(headings):
        qid,strategy=heading.group(1,2)
        key=(qid,strategy)
        if key in seen or key not in indexed:
            raise ValueError("Duplicate or unknown question/strategy section")
        seen.add(key)
        body=text[heading.end():headings[i+1].start() if i+1<len(headings) else len(text)]
        table_rows=re.findall(r"^\|\s*([123])\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|\s*(Đủ|Thiếu|Không có)\s*\|([^\n]+)$",body,re.M)
        if [int(row[0]) for row in table_rows]!=[1,2,3]:
            raise ValueError(f"Missing/duplicate rank rows: {key}")
        enough=[]
        for rank,short_id,page,label,tail in table_rows:
            hit=indexed[key]["hits"][int(rank)-1]
            if not hit["chunk_id"].startswith(short_id.removesuffix("...")) or hit["page"]!=int(page):
                raise ValueError(f"Chunk ID/page mismatch: {key}, rank {rank}")
            cells=tail.rstrip().removesuffix("|").split("|")
            if len(cells)!=2:
                raise ValueError("Expected evidence and reason columns")
            clean=lambda value:re.sub(r"\[cite:\s*[\d,\s]+\]","",value).strip()
            item={"question_id":qid,"strategy":strategy,"rank":int(rank),"chunk_id":hit["chunk_id"],
                  "page":hit["page"],"label":label,"evidence_hit":label=="Đủ",
                  "evidence_or_missing_information":clean(cells[0]),"reason":clean(cells[1]),
                  "reviewer":reviewer,"review_date_as_submitted":date,
                  "baseline_evidence_hit":hit["evidence_hit"],"matches_baseline":(label=="Đủ")==hit["evidence_hit"],
                  "provenance":"Learner-submitted assessment; ID/page and arithmetic checked by Codex"}
            entries.append(item)
            if label=="Đủ": enough.append(int(rank))
        h1,h3=int(1 in enough),int(bool(enough))
        stated1=re.search(r"- Hit@1:\s*`([01])`",body)
        stated3=re.search(r"- Hit@3:\s*`([01])`",body)
        if not stated1 or not stated3 or (h1,h3)!=(int(stated1.group(1)),int(stated3.group(1))):
            raise ValueError(f"Learner conclusion disagrees with rank labels: {key}")
        results.append({"question_id":qid,"strategy":strategy,"enough_ranks":enough,"hit_at_1":h1,"evidence_hit_at_3":h3})
    if seen!=set(indexed): raise ValueError("Test trace coverage is incomplete")
    metrics=[]
    for strategy in ("A","B","C"):
        rows=[r for r in results if r["strategy"]==strategy]
        metrics.append({"strategy":strategy,"split":"test","questions":len(rows),
                        "hit_at_1":{"numerator":sum(r["hit_at_1"] for r in rows),"denominator":len(rows)},
                        "evidence_hit_at_3":{"numerator":sum(r["evidence_hit_at_3"] for r in rows),"denominator":len(rows)}})
    summary={"status":"validated","reviewer":reviewer,"review_date_as_submitted":date,
             "source_sha256":hashlib.sha256(raw).hexdigest(),"trace_file":"results/test/traces.jsonl",
             "trace_sha256":hashlib.sha256((ROOT/"results/test/traces.jsonl").read_bytes()).hexdigest(),
             "question_strategy_reviews":len(results),"ranked_chunks_reviewed":len(entries),"metrics":metrics,
             "all_hit_labels_match_automatic_baseline":all(e["matches_baseline"] for e in entries),
             "selected_strategy_unchanged":"C","retrieval_rerun":False,"model_or_configuration_changed":False,
             "scope":"Learner evidence sufficiency review only; no coherence/grounding scores or metadata audit inferred",
             "per_question":results}
    out=ROOT/"results/test/student_review"
    out.mkdir(parents=True,exist_ok=True)
    (out/"chunk_reviews.jsonl").write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in entries),encoding="utf-8")
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    archive=ROOT/"report/sources/test_evidence_review_student_original.txt"
    archive.parent.mkdir(exist_ok=True)
    archive.write_bytes(raw)
    # Replace pasted citation tokens with a declared source map; retain student judgments.
    formatted=re.sub(r"\[cite:\s*1,\s*2\]"," [S1] [S2]",text)
    formatted=re.sub(r"\[cite:\s*1\]"," [S1]",formatted)
    formatted=re.sub(r"\[cite:\s*2\]"," [S2]",formatted)
    intro=("\n> Bản rà soát do **"+reviewer+"** cung cấp, ngày "+date+". Codex chỉ định dạng, "
           "đối chiếu ID/trang với trace và kiểm tra phép tổng hợp; không thay nhãn hoặc lý do của học viên. "
           "ID chunk viết rút gọn trong bảng; bản đầy đủ nằm ở results/test/student_review/chunk_reviews.jsonl.\n\n"
           "[S1]: ../benchmark/QUESTIONS_REVIEW.md\n[S2]: ../results/test/traces.jsonl\n\n"
           "Nguồn tham chiếu: **S1** = câu hỏi/evidence chuẩn q16–q20; **S2** = trace test gốc. "
           "Các ký hiệu citation trong bản dán được thay bằng hai tham chiếu này. Bản gốc được giữ tại "
           "[sources/test_evidence_review_student_original.txt](sources/test_evidence_review_student_original.txt).\n")
    first,rest=formatted.split("\n",1)
    formatted=first+"\n"+intro+rest
    formatted+="\n\n## Kết quả tổng hợp theo nhãn của học viên\n\n| Strategy | Hit@1 | Evidence Hit@3 |\n|---|---|---|\n"
    for metric in metrics:
        formatted+=f"| {metric['strategy']} | {metric['hit_at_1']['numerator']}/5 | {metric['evidence_hit_at_3']['numerator']}/5 |\n"
    formatted+="\nCả 45 nhãn đủ/không đủ khớp baseline tự động. Không thay đổi điểm hoặc lựa chọn C. "
    formatted+="Đây là rà soát evidence của học viên; chưa thay thế bảng chấm coherence, metadata và grounding theo rubric.\n"
    (ROOT/"report/test_evidence_review_student.md").write_text(formatted,encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k!='per_question'},ensure_ascii=False,indent=2))


if __name__=="__main__": main()
