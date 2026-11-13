"""Export A/B chunks and verify content coverage, provenance and stable IDs."""
import json
import logging
import statistics
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))
from src.chunking import by_paragraph, fixed_size
from src.ingestion import load_corpus


def verify(page, chunks, limit, overlap_allowed):
    covered = [0] * len(page.text)
    for chunk in chunks:
        start, end = chunk.metadata["start_char"], chunk.metadata["end_char"]
        if not (0 <= start < end <= len(page.text)) or chunk.text != page.text[start:end]:
            raise ValueError("Chunk text or offsets do not match source")
        if not chunk.text.strip() or len(chunk.text) > limit:
            raise ValueError("Empty or oversized chunk")
        if (chunk.document_id, chunk.source, chunk.page, chunk.metadata["section"]) != (
                page.document_id, page.source, page.page, page.metadata["section"]):
            raise ValueError("Chunk provenance changed")
        for position in range(start, end):
            covered[position] += 1
    if any(not count for char, count in zip(page.text, covered) if not char.isspace()):
        raise ValueError("Source content lost between chunks")
    if not overlap_allowed and any(count > 1 for count in covered):
        raise ValueError("Unexpected overlap in B")


def main():
    logging.basicConfig(level=logging.INFO)
    pages = load_corpus(ROOT / "data/manifest.json")
    frozen = {row["page"]: row for row in map(json.loads, (ROOT / "data/processed/esmap_pages.jsonl").read_text(encoding="utf-8").splitlines())}
    if set(frozen) != {page.page for page in pages} or any(page.text != frozen[page.page]["text"] for page in pages):
        raise ValueError("Source differs from frozen corpus")
    config = json.loads((ROOT / "artifacts/chunking_config.json").read_text(encoding="utf-8"))
    output = ROOT / "results/chunking"
    output.mkdir(parents=True, exist_ok=True)
    summary, sample = {}, ["# So sánh chia chunk trên trang PDF 65", "", "Tham số ban đầu, chưa đánh giá retrieval/coherence.", ""]
    for strategy in ("A", "B"):
        params = config[strategy]
        make = (lambda p: fixed_size(p, params["size"], params["overlap"])) if strategy == "A" else (lambda p: by_paragraph(p, params["max_size"]))
        chunks = []
        for page in pages:
            produced = make(page)
            verify(page, produced, params.get("size", params.get("max_size")), strategy == "A")
            if [asdict(c) for c in produced] != [asdict(c) for c in make(page)]:
                raise ValueError("Repeated chunking is not deterministic")
            chunks.extend(produced)
        if len({c.chunk_id for c in chunks}) != len(chunks):
            raise ValueError("Duplicate chunk IDs")
        (output / f"chunks_{strategy}.jsonl").write_text("".join(json.dumps(asdict(c), ensure_ascii=False) + "\n" for c in chunks), encoding="utf-8")
        lengths = sorted(len(c.text) for c in chunks)
        summary[strategy] = {"parameters": params, "pages": len(pages), "chunk_count": len(chunks),
                             "total_characters_in_chunks": sum(lengths), "min_characters": min(lengths),
                             "median_characters": statistics.median(lengths), "mean_characters": round(statistics.mean(lengths), 2),
                             "max_characters": max(lengths), "p10_characters": lengths[int((len(lengths)-1)*.1)],
                             "p90_characters": lengths[int((len(lengths)-1)*.9)],
                             "checks": "pass: source coverage, offsets, size, provenance, stable IDs; B has no overlap"}
        sample.extend([f"## Chiến lược {strategy}", ""])
        for index, chunk in enumerate((c for c in chunks if c.page == 65), 1):
            sample.extend([f"### Chunk {index} — {len(chunk.text)} ký tự — [{chunk.metadata['start_char']}, {chunk.metadata['end_char']})", "", "```text", chunk.text, "```", ""])
    summary["scope"] = "Chunking only; no embeddings, retrieval metrics or manual coherence labels"
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "page65_comparison.md").write_text("\n".join(sample), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
