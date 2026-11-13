"""Implement fixed-size and structure-aware chunking."""
import hashlib
import json
import re
from copy import deepcopy

from .models import Chunk, DocumentPage


def _positive_size(value: int) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError("Chunk size must be a positive integer (characters)")


def _chunk(page: DocumentPage, start: int, end: int, config: dict) -> Chunk | None:
    # Trim only boundary whitespace; offsets always refer to the original page text.
    while start < end and page.text[start].isspace():
        start += 1
    while end > start and page.text[end - 1].isspace():
        end -= 1
    if start == end:
        return None
    text = page.text[start:end]
    identity = {"document_id": page.document_id, "source": page.source, "page": page.page,
                "start": start, "end": end, "text": text, "config": config}
    chunk_id = hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    metadata = deepcopy(page.metadata)
    metadata.update({"start_char": start, "end_char": end, "chunking": deepcopy(config)})
    return Chunk(chunk_id, page.document_id, page.source, page.page, text, metadata)


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """A: fixed character windows with overlap; never cross a source page."""
    _positive_size(size)
    if type(overlap) is not int or not 0 <= overlap < size:
        raise ValueError("Overlap must be an integer with 0 <= overlap < size")
    config = {"method": "fixed_size", "version": 1, "size": size, "overlap": overlap}
    chunks = []
    for start in range(0, len(page.text), size - overlap):
        end = min(start + size, len(page.text))
        chunk = _chunk(page, start, end, config)
        if chunk is not None:
            chunks.append(chunk)
        if end == len(page.text):
            break
    return chunks


def _block_spans(text: str) -> list[tuple[int, int]]:
    """Find blank-line paragraphs and simple uppercase headings without rewriting text.

    PDF extraction often has only wrapped lines. A heading detector is a heuristic,
    not a claim that the original PDF's paragraph structure has been recovered.
    """
    boundaries = {0, len(text)}
    boundaries.update(match.end() for match in re.finditer(r"\n[ \t]*\n+", text))
    offset = 0
    previous_heading = False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        letters = [char for char in stripped if char.isalpha()]
        is_heading = len(letters) >= 3 and len(stripped) <= 120 and all(char.isupper() for char in letters)
        if is_heading and not previous_heading:
            # Keep multi-line headings with the prose that follows them.
            boundaries.add(offset)
        previous_heading = is_heading
        offset += len(line)
    points = sorted(boundaries)
    return [(start, end) for start, end in zip(points, points[1:]) if text[start:end].strip()]


def _split_long_span(text: str, start: int, end: int, limit: int) -> list[tuple[int, int]]:
    spans = []
    while end - start > limit:
        window = text[start:start + limit]
        # Prefer complete sentences; if none fit, prefer a word boundary.
        sentences = list(re.finditer(r'[.!?][\s]+(?=[A-Z0-9“"‘])', window))
        if sentences:
            cut = start + sentences[-1].end()
        else:
            spaces = list(re.finditer(r"\s+", window))
            cut = start + spaces[-1].end() if spaces else start + limit
        spans.append((start, cut))
        start = cut
    if start < end:
        spans.append((start, end))
    return spans


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """B: pack paragraph/heading blocks, splitting long blocks at sentence/word boundaries.

    Uses at most max_size characters, no overlap, and no cross-page joins. If the
    PDF has no blank-line paragraphs, sentence-aware splitting provides a fallback.
    """
    _positive_size(max_size)
    config = {"method": "by_paragraph", "version": 1, "max_size": max_size, "overlap": 0,
              "boundaries": "blank_lines_and_uppercase_headings_then_sentence_word_hard"}
    spans = [span for start, end in _block_spans(page.text)
             for span in _split_long_span(page.text, start, end, max_size)]
    packed = []
    for start, end in spans:
        if packed and end - packed[-1][0] <= max_size:
            packed[-1] = (packed[-1][0], end)
        else:
            packed.append((start, end))
    chunks = [_chunk(page, start, end, config) for start, end in packed]
    return [chunk for chunk in chunks if chunk is not None]
