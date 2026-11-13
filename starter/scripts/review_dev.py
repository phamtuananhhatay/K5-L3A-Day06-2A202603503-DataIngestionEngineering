"""Replay saved dev retrieval with documented Codex evidence decisions; no search."""
import copy
import hashlib
import json
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))
from src.evaluation import evaluate_query, normalize_evidence, summarize
from src.ingestion import normalize_text


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def main():
    frozen = read_json("benchmark/manifest.json")
    for file_key, hash_key in (("questions_file", "questions_sha256"), ("corpus_file", "corpus_sha256")):
        if hashlib.sha256((ROOT / frozen[file_key]).read_bytes()).hexdigest() != frozen[hash_key]:
            raise ValueError("Original benchmark/corpus changed")
    source = read_json("data/manifest.json")
    if hashlib.sha256((ROOT / source["local_path"]).read_bytes()).hexdigest() != frozen["source_pdf_sha256"]:
        raise ValueError("Original PDF changed")
    reader = PdfReader(ROOT / source["local_path"])
    source_pages = {}
    def page_text(number):
        if number not in source_pages:
            source_pages[number] = normalize_text(reader.pages[number - 1].extract_text() or "")
        return source_pages[number]
    dev = {q["id"]: q for q in read_json("benchmark/questions.json") if q["split"] == "dev"}
    additions = read_json("benchmark/dev_evidence_additions.json")["additions"]
    decisions = read_json("results/dev/review_decisions.json")
    by_id = {item["id"]: item for item in decisions["questions"]}
    if set(by_id) != set(dev) or not set(additions) <= set(dev):
        raise ValueError("Review must cover exactly dev; additions must not include test")
    for qid, items in additions.items():
        for item in items:
            if item["source_id"] != source["source_id"] or normalize_evidence(item["evidence_quote"]) not in normalize_evidence(page_text(item["page"])):
                raise ValueError(f"Unverified added evidence for {qid}")
    baseline = [json.loads(line) for line in (ROOT / "results/dev/traces.jsonl").read_text(encoding="utf-8").splitlines()]
    if len(baseline) != 45 or summarize(baseline)["metrics"] != read_json("results/dev/summary.json")["metrics"]:
        raise ValueError("Baseline trace/summary mismatch")
    reviewed, chunk_reviews = [], []
    for trace in baseline:
        if trace["split"] != "dev" or trace["question_id"] not in dev:
            raise ValueError("Non-dev trace encountered")
        qid, strategy = trace["question_id"], trace["strategy"]
        question = copy.deepcopy(dev[qid])
        question["alternative_gold_evidence"] = question.get("alternative_gold_evidence", []) + additions.get(qid, [])
        for hit in trace["hits"]:
            start, end = hit["metadata"]["start_char"], hit["metadata"]["end_char"]
            if hit["document_id"] != source["source_id"] or hit["source"] != source["source_path_or_url"] or hit["text"] != page_text(hit["page"])[start:end]:
                raise ValueError("Retrieved text/provenance differs from original PDF slice")
        row = {**trace, **evaluate_query(question, trace["hits"])}
        expected_ranks = by_id[qid]["hit_ranks"][strategy]
        if [h["rank"] for h in row["hits"] if h["evidence_hit"]] != expected_ranks:
            raise ValueError(f"Evidence matching disagrees with recorded source-review decision: {qid}/{strategy}")
        row.update({"manual_equivalence_review": decisions["reviewer"], "evidence_policy": "evidence-policy-v1",
                    "baseline_hit_at_1": trace["hit_at_1"], "baseline_evidence_hit_at_3": trace["evidence_hit_at_3"],
                    "review_reason": by_id[qid]["reason"]})
        reviewed.append(row)
        for old, hit in zip(trace["hits"], row["hits"]):
            chunk_reviews.append({"question_id":qid,"strategy":strategy,"rank":hit["rank"],"chunk_id":hit["chunk_id"],
                "page":hit["page"],"baseline_evidence_hit":old["evidence_hit"],"reviewed_evidence_hit":hit["evidence_hit"],
                "changed":old["evidence_hit"] != hit["evidence_hit"],"matched_evidence":hit["matched_gold_evidence"],
                "reason":by_id[qid]["reason"],"source_slice_verified":True,"reviewer":decisions["reviewer"]})
    for strategy in ("A","B","C"):
        if [t["question_id"] for t in reviewed if t["strategy"] == strategy] != frozen["splits"]["dev"]:
            raise ValueError("Incomplete dev strategy review")
    summary = summarize(reviewed)
    summary.update({"scope":"reviewed dev only", "reviewer":decisions["reviewer"],
        "note":"Dev evidence reviewed against source under a documented policy, then replayed with original plus accepted equivalent quotes; not independent human grounding/coherence assessment",
        "trace_count":len(reviewed),"ranked_chunks_reviewed":len(chunk_reviews),
        "changed_chunk_labels":sum(item["changed"] for item in chunk_reviews),
        "test_executed":False,"retrieval_rerun":False,
        "human_grounding_or_coherence_labels_created":False})
    ordered = sorted(summary["metrics"], key=lambda m:(-m["evidence_hit_at_3"]["value"],-m["hit_at_1"]["value"]))
    winner = ordered[0]
    if any((m["evidence_hit_at_3"]["value"],m["hit_at_1"]["value"]) == (winner["evidence_hit_at_3"]["value"],winner["hit_at_1"]["value"]) for m in ordered[1:]):
        raise ValueError("Need resource tie-break before configuration can be frozen")
    selection={"selected_strategy":winner["strategy"],"metrics":winner,
               "basis":"Original criterion: dev Hit@3, then Hit@1. Resource tie-break not needed.",
               "reviewer":decisions["reviewer"],"test_executed":False}
    out=ROOT/"results/dev/reviewed"
    out.mkdir(exist_ok=True)
    for name, value in (("summary.json",summary),("selection.json",selection)):
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for name, rows in (("traces.jsonl",reviewed),("chunk_review.jsonl",chunk_reviews)):
        (out/name).write_text("".join(json.dumps(row,ensure_ascii=False)+"\n" for row in rows),encoding="utf-8")
    lines=["# Dev sau rà soát evidence bằng Codex", "", "Không phải chấm độc lập của con người; không có nhãn grounding/coherence thủ công.", "", "| Strategy | Hit@1 | Evidence Hit@3 |", "|---|---|---|"]
    for m in summary["metrics"]:
        lines.append(f"| {m['strategy']} | {m['hit_at_1']['numerator']}/15 | {m['evidence_hit_at_3']['numerator']}/15 |")
    lines += ["", "| Câu | Strategy | Hit ranks sau review | Thay đổi Hit@1 / Hit@3 | Lý do |", "|---|---|---|---|---|"]
    for row in reviewed:
        ranks=[h["rank"] for h in row["hits"] if h["evidence_hit"]]
        lines.append(f"| {row['question_id']} | {row['strategy']} | {ranks} | {int(row['baseline_hit_at_1'])}→{int(row['hit_at_1'])} / {int(row['baseline_evidence_hit_at_3'])}→{int(row['evidence_hit_at_3'])} | {row['review_reason']} |")
    (out/"comparison.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
