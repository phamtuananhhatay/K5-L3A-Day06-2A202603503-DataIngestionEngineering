"""Read source pages without losing physical page numbers or provenance."""
import hashlib
import json
import logging
import re
import unicodedata
from pathlib import Path

from pypdf import PdfReader

from .models import DocumentPage

logger = logging.getLogger(__name__)


def load_pdf(path: Path, document_id: str, source: str) -> list[DocumentPage]:
    """Extract every physical page, including empty/failed pages, numbered from 1.

    File-level errors fail loudly. Page-level errors are logged and retained in
    metadata so corpus selection can reject an unreadable selected page. No OCR
    or guessed content is substituted for missing text.
    """
    path = Path(path)
    if not document_id.strip() or not source.strip():
        raise ValueError("document_id and source must not be empty")
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and not reader.decrypt(""):
            raise ValueError(f"PDF requires a password: {path}")
        page_count = len(reader.pages)
    except Exception:
        logger.exception("Cannot open PDF: %s", path)
        raise

    pages = []
    for number in range(1, page_count + 1):
        error = None
        try:
            text = normalize_text(reader.pages[number - 1].extract_text() or "")
            status = "ok" if text else "empty"
            if not text:
                logger.warning("No extractable text: document=%s page=%d", document_id, number)
        except Exception as exc:
            text, status = "", "error"
            error = f"{type(exc).__name__}: {exc}"
            logger.exception("Page extraction failed: document=%s page=%d", document_id, number)
        metadata = {"extraction_status": status, "normalized_characters": len(text)}
        if error:
            metadata["extraction_error"] = error
        pages.append(DocumentPage(document_id, source, number, text, metadata))
    logger.info("Read %d physical pages: document=%s", len(pages), document_id)
    return pages


def normalize_text(text: str) -> str:
    """Match the frozen task-1 corpus normalization; keep line boundaries.

    Do not guess paragraph breaks, remove headings or repair hyphenation here:
    those edits would change the corpus used to verify the benchmark.
    """
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def load_corpus(manifest_path: Path) -> list[DocumentPage]:
    """Read the original PDF and select the content pages declared in a manifest.

    local_path is relative to the repository containing data/manifest.json.
    Section metadata comes from explicit physical-page ranges in that manifest.
    """
    manifest_path = Path(manifest_path).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent.parent
    path = root / manifest["local_path"]
    if hashlib.sha256(path.read_bytes()).hexdigest() != manifest["sha256"]:
        raise ValueError("Source PDF checksum differs from the manifest")
    selected = manifest["content_pages"]
    if any(type(number) is not int or number < 1 for number in selected):
        raise ValueError("Content page numbers must be positive integers")
    if len(selected) != len(set(selected)):
        raise ValueError("Duplicate content page numbers in manifest")
    if len(selected) != manifest["content_page_count"] or len(selected) < 30:
        raise ValueError("Manifest must declare at least 30 unique content pages with a matching count")

    all_pages = load_pdf(path, manifest["source_id"], manifest["source_path_or_url"])
    if len(all_pages) != manifest["physical_pages"]:
        raise ValueError("Physical PDF page count differs from the manifest")
    by_number = {page.page: page for page in all_pages}
    corpus = []
    for number in selected:
        if number not in by_number:
            raise ValueError(f"Selected page {number} does not exist")
        page = by_number[number]
        if page.metadata["extraction_status"] != "ok":
            raise ValueError(f"Selected page {number} is empty or unreadable; see ingestion log")
        sections = [entry["section"] for entry in manifest["content_page_ranges"]
                    if entry["start"] <= number <= entry["end"]]
        if len(sections) != 1:
            raise ValueError(f"Selected page {number} must have exactly one declared section")
        page.metadata["section"] = sections[0]
        if "report_year" in manifest:
            page.metadata["report_year"] = manifest["report_year"]
        corpus.append(page)
    logger.info("Selected %d valid content pages from manifest", len(corpus))
    return corpus
