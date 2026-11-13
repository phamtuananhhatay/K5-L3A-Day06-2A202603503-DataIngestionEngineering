"""Reproduce the task-1 audit of the selected ESMAP PDF (no embeddings)."""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parents[2]
SOURCE_ID = "esmap-annual-report-2021"
FILENAME = "Energy-Sector-Management-Assistance-Program-ESMAP-Annual-Report-2021.pdf"
SOURCE_URL = "https://documents1.worldbank.org/curated/en/615511640189474271/pdf/" + FILENAME
CATALOG_URL = "https://documents.worldbank.org/en/publication/documents-reports/documentdetail/615511640189474271"
# Physical PDF pages, 1-based. Derived from the TOC and section headings.
SECTIONS = [
    (23, 25, "Energy Data"),
    (27, 35, "Foundations of Energy Transition"),
    (37, 43, "Accelerating Decarbonization"),
    (45, 47, "Clean Cooking"),
    (49, 55, "Electricity Access"),
    (57, 65, "Renewable Energy"),
]


def normalize(text: str) -> str:
    """NFC + normalize horizontal whitespace; retain line boundaries for inspection."""
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def excluded_reason(page: int) -> str:
    if page in (1, 3):
        return "Cover or title page"
    if page == 2:
        return "About, copyright and permissions; kept as provenance, not corpus"
    if page in (4, 5):
        return "Table of contents"
    if page == 6:
        return "Abbreviations; excluded conservatively from the selected corpus"
    if page == 7:
        return "Donor logos, little extractable text"
    if page in (8, 20, 22, 26, 36, 44, 48, 56, 72, 76):
        return "Section opener, mostly image/title; excluded conservatively"
    if page == 74:
        return "Photo and credit only"
    if page == 82:
        return "No extractable text; final page excluded"
    return "Outside selected scope: overview, partnerships, trust funds or financial review"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verified-at", required=True, help="Actual source verification date, YYYY-MM-DD")
    args = parser.parse_args()
    pdf = ROOT / "data" / "raw" / FILENAME
    reader = pypdf.PdfReader(pdf)
    inventory, corpus, errors = [], [], []
    for number, page in enumerate(reader.pages, 1):
        try:
            text = normalize(page.extract_text() or "")
            error = None
        except Exception as exc:
            text, error = "", f"{type(exc).__name__}: {exc}"
            errors.append({"page": number, "error": error})
        section = next((name for start, end, name in SECTIONS if start <= number <= end), None)
        selected = section is not None
        inventory.append({
            "page": number,
            "printed_page": str(number - 8) if 9 <= number <= 81 else None,
            "included": selected,
            "section": section,
            "normalized_characters": len(text),
            "replacement_characters": text.count("\ufffd"),
            "extraction_error": error,
            "reason": "Substantive text in selected energy topic" if selected else excluded_reason(number),
        })
        if selected:
            if error or not text:
                raise RuntimeError(f"Selected page {number} is unreadable: {error}")
            corpus.append({
                "page_id": f"{SOURCE_ID}:p{number:03d}",
                "document_id": SOURCE_ID,
                "source": SOURCE_URL,
                "page": number,
                "printed_page": str(number - 8),
                "metadata": {"section": section, "report_year": 2021, "language": "en", "document_type": "annual_report"},
                "text": text,
            })
    if len(corpus) < 30:
        raise RuntimeError("Fewer than 30 selected content pages")
    digests = [hashlib.sha256(row["text"].encode("utf-8")).hexdigest() for row in corpus]
    if len(set(digests)) != len(digests):
        raise RuntimeError("Duplicate normalized pages detected")
    manifest = {
        "source_id": SOURCE_ID,
        "title": "Energy Sector Management Assistance Program (ESMAP) Annual Report 2021",
        "author": "Energy Sector Management Assistance Program (ESMAP)",
        "publisher": "World Bank",
        "source_path_or_url": SOURCE_URL,
        "catalog_url": CATALOG_URL,
        "local_path": "data/raw/" + FILENAME,
        "license_or_permission": "CC BY 3.0 IGO, declared on physical PDF page 2; image and third-party content exceptions apply",
        "license_url": "https://creativecommons.org/licenses/by/3.0/igo/",
        "rights_evidence_page": 2,
        "attribution": "Energy Sector Management Assistance Program (ESMAP). 2021. Annual Report 2021. Washington, DC: World Bank.",
        "accessed_at": args.verified_at,
        "accessed_at_note": "Date official source was verified for this audit; original user download date unknown",
        "report_year": 2021,
        "version": "Local PDF snapshot identified by SHA-256; no software version or effective date inferred",
        "sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
        "file_size_bytes": pdf.stat().st_size,
        "physical_pages": len(reader.pages),
        "content_page_count": len(corpus),
        "content_pages": [row["page"] for row in corpus],
        "content_page_ranges": [{"start": start, "end": end, "section": name} for start, end, name in SECTIONS],
        "page_numbering": "Physical PDF pages, 1-based. Printed Arabic page = physical page - 8 for pages 9-81.",
        "page_count_rule": "Selected six energy-topic sections; conservatively omit cover, front matter, section openers, photo-only pages and content outside chosen scope. Not every excluded page is invalid.",
        "normalized_character_count": sum(len(row["text"]) for row in corpus),
        "normalization": "Unicode NFC, normalize horizontal whitespace, trim lines, keep line boundaries; headers, footers and hyphenation retained for later pipeline work",
        "extraction": {"library": "pypdf", "version": pypdf.__version__, "ocr_used": False},
        "filter_field": {"name": "section", "type": "string", "values": [name for _, _, name in SECTIONS], "provenance": "PDF TOC physical page 4 and corresponding headings", "use": "Restrict retrieval to a section explicitly requested by question/context; never infer from gold evidence"},
        "scope": "Text corpus only; no image extraction or redistribution of the original PDF by this repository workflow",
        "outputs": {"page_inventory": "data/page_inventory.json", "normalized_pages": "data/processed/esmap_pages.jsonl", "audit_log": "results/task1_audit.json"},
    }
    audit = {
        "verified_at": args.verified_at,
        "physical_pages": len(reader.pages),
        "selected_pages": len(corpus),
        "selected_normalized_characters": manifest["normalized_character_count"],
        "selected_min_characters": min(len(row["text"]) for row in corpus),
        "selected_max_characters": max(len(row["text"]) for row in corpus),
        "no_text_pages": [row["page"] for row in inventory if not row["normalized_characters"]],
        "selected_pages_with_replacement_characters": [row["page"] for row in inventory if row["included"] and row["replacement_characters"]],
        "duplicate_normalized_selected_pages": len(digests) - len(set(digests)),
        "extraction_errors": errors,
        "manual_review_note": "Automated extraction does not prove semantic correctness; see report/task1_corpus_review.md for visual checks and limitations",
    }
    for folder in ("data/processed", "results"):
        (ROOT / folder).mkdir(parents=True, exist_ok=True)
    for path, obj in (("data/manifest.json", manifest), ("data/page_inventory.json", inventory), ("results/task1_audit.json", audit)):
        (ROOT / path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "data/processed/esmap_pages.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in corpus), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
