"""Evidence retrieval metrics; never infer human coherence/grounding labels."""
import re
import unicodedata
from collections import defaultdict
from typing import Any


def normalize_evidence(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def evaluate_query(question: dict[str, Any], hits: list[dict[str, Any]]) -> dict[str, Any]:
    """A hit needs a valid source/page and a complete recorded evidence quote.

    Normalize NFC/whitespace only. This conservative automatic rule may miss
    semantically equivalent evidence; such cases need documented review, not
    automatic relabeling from page match or similarity score. Accept alternative
    evidence records supplied in the benchmark consistently for all strategies.
    """
    gold = [{"source_id": question["gold_source_id"], "page": question["gold_page"],
             "evidence_quote": question["evidence_quote"]}, *question.get("alternative_gold_evidence", [])]
    if not all(normalize_evidence(item["evidence_quote"]) for item in gold):
        raise ValueError("Gold evidence must not be empty")
    annotated = []
    for rank, hit in enumerate(hits[:3], 1):
        text = normalize_evidence(hit["text"])
        valid = [item for item in gold if hit["document_id"] == item["source_id"] and hit["page"] == item["page"]]
        matching = [item for item in valid if normalize_evidence(item["evidence_quote"]) in text]
        annotated.append({**hit, "rank": rank, "gold_source_page_match": bool(valid),
                          "evidence_hit": bool(matching), "matched_gold_evidence": matching})
    hit1 = bool(annotated and annotated[0]["evidence_hit"])
    hit3 = any(hit["evidence_hit"] for hit in annotated)
    if hit3:
        diagnostic = "complete_recorded_evidence_found"
    elif any(hit["gold_source_page_match"] for hit in annotated):
        diagnostic = "gold_page_retrieved_but_complete_quote_missing; review partial/split/equivalent evidence"
    else:
        diagnostic = "gold_source_page_absent_from_top3; review possible alternative evidence"
    required_filter = question.get("filter")
    def obeys(hit):
        return all((hit.get(key) if key in ("source", "page", "document_id") else hit["metadata"].get(key)) == value
                   for key, value in required_filter.items())
    compliance = (bool(annotated) and all(obeys(hit) for hit in annotated)) if required_filter else None
    return {"question_id": question["id"], "split": question["split"], "question": question["question"],
            "expected_answer": question["expected_answer"], "gold_evidence": gold,
            "requested_filter": required_filter, "hit_at_1": hit1, "evidence_hit_at_3": hit3,
            "filter_compliance": compliance, "diagnostic": diagnostic, "hits": annotated,
            "evaluation_method": "NFC/whitespace-normalized complete recorded quote in one valid-source/page chunk",
            "manual_equivalence_review": "not performed", "manual_grounding": None, "manual_coherence": None}


def summarize(traces: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate question-level metrics with explicit numerators/denominators."""
    groups = defaultdict(list)
    seen = set()
    for trace in traces:
        key = (trace["strategy"], trace["split"], trace["question_id"])
        if key in seen:
            raise ValueError("Duplicate strategy/split/question trace would bias metrics")
        seen.add(key)
        groups[key[:2]].append(trace)
    def ratio(n, total):
        return {"numerator": n, "denominator": total, "value": n / total if total else None}
    metrics = []
    for (strategy, split), rows in sorted(groups.items()):
        filter_rows = [row for row in rows if row["requested_filter"]]
        metrics.append({"strategy": strategy, "split": split, "questions": len(rows),
                        "hit_at_1": ratio(sum(row["hit_at_1"] for row in rows), len(rows)),
                        "evidence_hit_at_3": ratio(sum(row["evidence_hit_at_3"] for row in rows), len(rows)),
                        "filter_compliance": ratio(sum(row["filter_compliance"] is True for row in filter_rows), len(filter_rows)),
                        "miss_question_ids": [row["question_id"] for row in rows if not row["evidence_hit_at_3"]]})
    return {"metrics": metrics, "note": "Automatic conservative evidence matching; not LLM answer accuracy or manual grounding/coherence"}
