"""Validate task-2 gold evidence against both the corpus and the original PDF.

This is a data check, not a retrieval benchmark or an automatic semantic judge.
Run from any directory; paths are resolved relative to the repository root.
"""
import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    questions_path = ROOT / "benchmark/questions.json"
    questions = json.loads(questions_path.read_text(encoding="utf-8"))
    frozen = json.loads((ROOT / "benchmark/manifest.json").read_text(encoding="utf-8"))
    source = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    corpus_path = ROOT / "data/processed/esmap_pages.jsonl"
    pages = {row["page"]: row for row in map(json.loads, corpus_path.read_text(encoding="utf-8").splitlines())}
    pdf_path = ROOT / source["local_path"]
    pdf = PdfReader(pdf_path)
    errors, rows = [], []
    seen_ids, seen_questions = set(), set()

    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)

    check(digest(questions_path) == frozen["questions_sha256"], "Questions differ from frozen snapshot")
    check(digest(corpus_path) == frozen["corpus_sha256"], "Corpus differs from frozen snapshot")
    check(digest(pdf_path) == source["sha256"] == frozen["source_pdf_sha256"], "Source PDF checksum mismatch")
    split_counts = Counter(q.get("split") for q in questions)
    check(len(questions) >= 20, "Fewer than 20 questions")
    check(split_counts["dev"] >= 15 and split_counts["test"] >= 5, "Insufficient dev/test split")
    check(set(split_counts) <= {"dev", "test"}, "Unknown split")
    required = {"id", "split", "question", "expected_answer", "gold_source_id", "gold_page", "evidence_quote", "filter"}

    for q in questions:
        qid = q.get("id", "<missing>")
        check(required <= q.keys(), f"{qid}: missing fields")
        if not required <= q.keys():
            continue
        check(qid not in seen_ids, f"{qid}: duplicate ID")
        seen_ids.add(qid)
        query = normalized(q["question"])
        check(query not in seen_questions, f"{qid}: duplicate question")
        seen_questions.add(query)
        check(bool(query) and bool(q["expected_answer"].strip()), f"{qid}: empty question or answer")
        page = pages.get(q["gold_page"])
        check(page is not None, f"{qid}: gold page outside selected corpus")
        if page is None:
            continue
        check(q["gold_source_id"] == page["document_id"], f"{qid}: gold source mismatch")
        evidence = normalized(q["evidence_quote"])
        in_corpus = bool(evidence) and evidence in normalized(page["text"])
        in_pdf = bool(evidence) and evidence in normalized(pdf.pages[q["gold_page"] - 1].extract_text() or "")
        check(in_corpus, f"{qid}: evidence missing from normalized page")
        check(in_pdf, f"{qid}: evidence missing from original PDF page")
        filters = q["filter"]
        if filters is not None:
            check(isinstance(filters, dict) and set(filters) == {"section"}, f"{qid}: unsupported filter")
            if isinstance(filters, dict):
                section = filters.get("section")
                check(section == page["metadata"]["section"], f"{qid}: filter does not match source section")
                check(bool(section) and f"Chỉ xét mục {section}" in query, f"{qid}: filter not explicitly given in question")
                check(bool(q.get("filter_origin")), f"{qid}: missing filter provenance")
        for alternative in q.get("alternative_gold_evidence", []):
            alt = pages.get(alternative["page"])
            check(alt is not None and alt["document_id"] == alternative["source_id"] and normalized(alternative["evidence_quote"]) in normalized(alt["text"]), f"{qid}: invalid alternative evidence")
        rows.append({"id": qid, "split": q["split"], "gold_page": q["gold_page"],
                     "evidence_in_corpus": in_corpus, "evidence_in_pdf": in_pdf,
                     "filter": filters, "semantic_review": "Authoring review recorded in verification_note; not an independent human assessment"})

    filter_counts = Counter(q["split"] for q in questions if q.get("filter"))
    check(sum(filter_counts.values()) >= 3 and filter_counts["test"] >= 1, "Insufficient filter questions")
    dev_pages = {q["gold_page"] for q in questions if q["split"] == "dev"}
    test_pages = {q["gold_page"] for q in questions if q["split"] == "test"}
    check(not dev_pages & test_pages, "Dev/test gold pages overlap, contrary to documented split")
    for split in ("dev", "test"):
        check([q["id"] for q in questions if q["split"] == split] == frozen["splits"][split], f"{split}: split assignment changed")

    result = {"benchmark_version": frozen["version"], "status": "pass" if not errors else "fail",
              "questions": len(questions), "split_counts": dict(split_counts),
              "filter_counts": dict(filter_counts),
              "gold_page_overlap": sorted(dev_pages & test_pages),
              "evidence_in_corpus_count": sum(r["evidence_in_corpus"] for r in rows),
              "evidence_in_pdf_count": sum(r["evidence_in_pdf"] for r in rows),
              "retrieval_executed": False, "errors": errors, "per_question": rows}
    output = ROOT / "results/task2_validation.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "per_question"}, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
