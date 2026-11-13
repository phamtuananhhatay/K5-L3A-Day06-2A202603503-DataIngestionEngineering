"""Load saved A/B vectors into pgvector and verify persistence/idempotency."""
import hashlib
import json
import os
import sys
import time
from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))
from src.models import Chunk
from src.store import PgVectorStore


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    load_dotenv(ROOT / "starter/.env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL missing; see starter/.env.example")
    summary = json.loads((ROOT / "results/embeddings/summary.json").read_text(encoding="utf-8"))
    model = summary["model"]
    if model != json.loads((ROOT / "artifacts/embedding_config.json").read_text(encoding="utf-8")):
        raise ValueError("Embedding configuration has changed; regenerate vectors explicitly")
    store = PgVectorStore(url, model["dimensions"])
    # Validate every file before making any schema/data changes.
    payloads = {}
    for strategy in ("A", "B"):
        entry = summary["strategies"][strategy]
        chunk_path = ROOT / entry["chunk_file"]
        vector_path = ROOT / f"results/embeddings/vectors_{strategy}.npz"
        if fingerprint(chunk_path) != entry["chunk_file_sha256"] or fingerprint(vector_path) != entry["vector_file_sha256"]:
            raise ValueError(f"Chunk/vector snapshot hash mismatch for {strategy}")
        chunks = [Chunk(**json.loads(line)) for line in chunk_path.read_text(encoding="utf-8").splitlines()]
        with np.load(vector_path, allow_pickle=False) as saved:
            vectors = saved["vectors"].copy()
            if saved["chunk_ids"].tolist() != [chunk.chunk_id for chunk in chunks]:
                raise ValueError(f"Vector order differs from chunk IDs for {strategy}")
        if vectors.shape != (len(chunks), model["dimensions"]) or not np.isfinite(vectors).all() or not np.allclose(np.linalg.norm(vectors, axis=1), 1, atol=1e-5):
            raise ValueError(f"Invalid vectors for {strategy}")
        for chunk in chunks:
            chunk.metadata = deepcopy(chunk.metadata)
            chunk.metadata["embedding_model"] = model
        payloads[strategy] = (chunks, vectors)

    store.create_schema()
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "table": "public.day6_chunks",
              "dimensions": model["dimensions"], "model_name": model["model_name"], "revision": model["revision"],
              "strategies": {}, "retrieval_executed": False}
    for strategy, (chunks, vectors) in payloads.items():
        start = time.perf_counter()
        store.upsert(strategy, chunks, vectors.tolist())
        seconds = time.perf_counter() - start
        def verify():
            # A new connection confirms data was committed and is persistently readable.
            with psycopg.connect(url, connect_timeout=10) as connection:
                rows = connection.execute("""
                    SELECT chunk_id, document_id, source, page, text, metadata,
                           embedding::text, vector_dims(embedding)
                    FROM public.day6_chunks WHERE strategy = %s
                """, (strategy,)).fetchall()
            by_id = {row[0]: row for row in rows}
            if set(by_id) != {chunk.chunk_id for chunk in chunks}:
                raise ValueError(f"Stored IDs/count differ for {strategy}")
            for chunk, vector in zip(chunks, vectors):
                row = by_id[chunk.chunk_id]
                if row[1:6] != (chunk.document_id, chunk.source, chunk.page, chunk.text, chunk.metadata):
                    raise ValueError(f"Stored text/metadata differ for {strategy}")
                if row[7] != model["dimensions"] or not np.allclose(json.loads(row[6]), vector, atol=1e-7, rtol=1e-6):
                    raise ValueError(f"Stored vector differs for {strategy}")
            return len(rows)
        count = verify()
        store.upsert(strategy, chunks, vectors.tolist())
        second_count = verify()
        report["strategies"][strategy] = {"rows": count, "rows_after_reingest": second_count,
            "first_import_seconds": round(seconds, 3), "text_metadata_and_vector_roundtrip": "pass",
            "idempotent_reingest": count == second_count, "distinct_pages": len({c.page for c in chunks})}

    # Exercise obsolete-chunk cleanup with real vectors in an isolated test strategy.
    test_strategy = "_storage_check"
    with psycopg.connect(url, connect_timeout=10) as connection:
        if connection.execute("SELECT count(*) FROM public.day6_chunks WHERE strategy=%s", (test_strategy,)).fetchone()[0]:
            raise ValueError("Test strategy already exists; refusing to overwrite its data")
    chunks, vectors = payloads["A"]
    samples = [replace(chunk, document_id="storage-check-only") for chunk in chunks[:2]]
    try:
        store.upsert(test_strategy, samples, vectors[:2].tolist())
        store.upsert(test_strategy, samples[:1], vectors[:1].tolist())
        with psycopg.connect(url, connect_timeout=10) as connection:
            remaining = connection.execute("SELECT chunk_id FROM public.day6_chunks WHERE strategy=%s", (test_strategy,)).fetchall()
        if remaining != [(samples[0].chunk_id,)]:
            raise ValueError("Obsolete chunk cleanup failed")
        report["obsolete_chunk_cleanup"] = "pass: isolated snapshot shrank from 2 chunks to 1"
    finally:
        with psycopg.connect(url, connect_timeout=10) as connection:
            connection.execute("DELETE FROM public.day6_chunks WHERE strategy=%s AND document_id=%s", (test_strategy, "storage-check-only"))
    # Verify input rejection does not alter committed A data.
    try:
        store.upsert("A", chunks[:1], [vectors[0, :-1].tolist()])
    except ValueError:
        report["wrong_dimension_rejected"] = True
    else:
        raise ValueError("Wrong vector dimensions were accepted")
    with psycopg.connect(url, connect_timeout=10) as connection:
        report["database"] = connection.execute("SELECT current_database(), current_setting('server_version'), (SELECT extversion FROM pg_extension WHERE extname='vector')").fetchone()
        report["total_A_B_rows"] = connection.execute("SELECT count(*) FROM public.day6_chunks WHERE strategy=ANY(%s::text[])", (["A", "B"],)).fetchone()[0]
        if report["total_A_B_rows"] != sum(entry["rows"] for entry in report["strategies"].values()):
            raise ValueError("Final row count changed unexpectedly")
    report["status"] = "pass"
    report["C_plan"] = "Reuse B at search time; no C copy imported"
    report["search_plan"] = "Exact cosine search planned; no approximate vector index created"
    (ROOT / "results/storage_check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
