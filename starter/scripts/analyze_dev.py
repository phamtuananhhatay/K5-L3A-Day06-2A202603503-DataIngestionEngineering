"""Diagnose dev misses against all indexed chunks, without more retrieval or test use."""
import json
import hashlib
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))
from src.evaluation import normalize_evidence, summarize


def main():
    traces = [json.loads(line) for line in (ROOT / "results/dev/traces.jsonl").read_text(encoding="utf-8").splitlines()]
    summary = json.loads((ROOT / "results/dev/summary.json").read_text(encoding="utf-8"))
    expected_ids = json.loads((ROOT / "benchmark/manifest.json").read_text(encoding="utf-8"))["splits"]["dev"]
    if len(traces) != 45 or summary["metrics"] != summarize(traces)["metrics"]:
        raise ValueError("Dev traces/summary mismatch")
    for strategy in ("A", "B", "C"):
        selected = [t for t in traces if t["strategy"] == strategy]
        if [t["question_id"] for t in selected] != expected_ids or any(len(t["hits"]) > 3 for t in selected):
            raise ValueError("Incomplete or invalid strategy trace set")
    snapshots = {s: [json.loads(line) for line in (ROOT / f"results/chunking/chunks_{s}.jsonl").read_text(encoding="utf-8").splitlines()] for s in ("A", "B")}
    rows = []
    for trace in traces:
        if trace["split"] != "dev":
            raise ValueError("This diagnostic only accepts dev traces")
        chunks = snapshots["B" if trace["strategy"] == "C" else "A" if trace["strategy"] == "A" else "B"]
        filters = trace["applied_filter"] or {}
        eligible = [c for c in chunks if all(c["metadata"].get(key) == value for key,value in filters.items())]
        available = [c["chunk_id"] for c in eligible if any(c["document_id"] == gold["source_id"] and c["page"] == gold["page"] and normalize_evidence(gold["evidence_quote"]) in normalize_evidence(c["text"]) for gold in trace["gold_evidence"])]
        category = ("hit" if trace["evidence_hit_at_3"] else "retrieval_miss_despite_available_complete_quote" if available else "complete_quote_absent_from_any_eligible_chunk")
        rows.append({"question_id":trace["question_id"], "strategy":trace["strategy"],
                     "category":category, "complete_evidence_chunk_ids_in_index":available,
                     "retrieved_pages":[h["page"] for h in trace["hits"]],
                     "gold_pages":[g["page"] for g in trace["gold_evidence"]]})
    counts = {s:dict(Counter(row["category"] for row in rows if row["strategy"] == s)) for s in ("A","B","C")}
    result={"counts":counts,"per_question":rows,
            "note":"Automatic full-quote diagnostics, not independent semantic review or manual grounding. Does not change hit labels."}
    (ROOT / "results/dev/failure_analysis.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    ordered = sorted(summary["metrics"], key=lambda m: (-m["evidence_hit_at_3"]["value"], -m["hit_at_1"]["value"]))
    best = ordered[0]
    tied = [m for m in ordered if (m["evidence_hit_at_3"]["value"],m["hit_at_1"]["value"]) == (best["evidence_hit_at_3"]["value"],best["hit_at_1"]["value"])]
    selection={"selected_strategy":best["strategy"] if len(tied)==1 else None,
               "basis":"Fixed rule: dev Evidence Hit@3 then Hit@1; resource tie-breakers unnecessary if unique",
               "tie_requires_resource_comparison":len(tied)>1,
               "evidence_hit_at_3":best["evidence_hit_at_3"], "hit_at_1":best["hit_at_1"],
               "metric_scope":"automatic complete-recorded-quote matching, pending semantic-equivalence review",
               "test_executed":False,
               "configuration_hashes":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ("artifacts/chunking_config.json","artifacts/embedding_config.json","benchmark/questions.json")}}
    (ROOT/"results/dev/selection.json").write_text(json.dumps(selection,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(counts,ensure_ascii=False,indent=2))
    print('Selected by automatic dev metrics:',selection['selected_strategy'])


if __name__ == "__main__":
    main()
