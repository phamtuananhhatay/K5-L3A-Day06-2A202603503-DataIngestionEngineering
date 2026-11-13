"""Run the ingestion step and compare it with the frozen task-1 corpus.

From the repository root:
    starter/.venv/Scripts/python.exe starter/scripts/check_ingestion.py
"""
import json
import logging
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))

from src.ingestion import load_corpus, normalize_text


def main() -> None:
    output = ROOT / "results"
    output.mkdir(exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(output / "ingestion.log", mode="w", encoding="utf-8"), logging.StreamHandler()],
    )
    corpus = load_corpus(ROOT / "data/manifest.json")
    frozen = [json.loads(line) for line in (ROOT / "data/processed/esmap_pages.jsonl").read_text(encoding="utf-8").splitlines()]
    actual = {page.page: page for page in corpus}
    if set(actual) != {row["page"] for row in frozen}:
        raise ValueError("Ingestion page selection differs from frozen corpus")
    for row in frozen:
        page = actual[row["page"]]
        if (page.text != row["text"] or page.source != row["source"]
                or page.document_id != row["document_id"]
                or page.metadata["section"] != row["metadata"]["section"]):
            raise ValueError(f"Content/provenance mismatch on page {page.page}")

    # Check accented text and paragraph boundaries rather than assuming English-only input.
    if normalize_text("  Tie\u0302\u0301ng\tVie\u0323\u0302t\r\n\r\n\r\n  do\u0300ng  hai  ") != "Tiếng Việt\n\ndòng hai":
        raise ValueError("Unicode/whitespace normalization regression")
    if any(normalize_text(page.text) != page.text for page in corpus):
        raise ValueError("Normalization must be idempotent")

    sample = actual[65]
    (output / "ingestion_page65.json").write_text(json.dumps(asdict(sample), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {
        "status": "pass", "selected_pages": len(corpus),
        "normalized_characters": sum(len(page.text) for page in corpus),
        "pages_matching_frozen_corpus": len(frozen),
        "sample_page": 65, "sample_section": sample.metadata["section"],
        "unicode_and_idempotence_checks": "pass",
        "scope": "Read and normalize only; no chunks, embeddings or retrieval",
    }
    (output / "ingestion_check.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
