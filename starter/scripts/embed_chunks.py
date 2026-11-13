"""Create real local embeddings for frozen A/B chunks; no retrieval or gold inputs."""
import hashlib
import importlib.metadata
import json
import logging
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))
from src.embeddings import MyEmbedder


def main():
    output = ROOT / "results/embeddings"
    output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(output / "embedding.log", mode="w", encoding="utf-8"), logging.StreamHandler()])
    started = time.perf_counter()
    embedder = MyEmbedder()
    load_seconds = time.perf_counter() - started
    if embedder.embed_documents([]) != []:
        raise RuntimeError("Empty document batch must return no vectors")
    for bad_input in ([" "], ["word " * 600]):
        try:
            embedder.embed_documents(bad_input)
        except ValueError:
            pass
        else:
            raise RuntimeError("Blank or overlength input must be rejected")
    summary = {"model": embedder.config, "started_at_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "runtime_versions": {name: importlib.metadata.version(name) for name in ("numpy", "onnxruntime", "tokenizers")},
               "model_load_seconds": round(load_seconds, 3), "paid_service_cost_usd": 0,
               "cost_note": "Local CPU inference; excludes electricity, hardware and network costs",
               "strategies": {}, "retrieval_executed": False}
    for strategy in ("A", "B"):
        source = ROOT / f"results/chunking/chunks_{strategy}.jsonl"
        chunks = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
        before = len(embedder.token_counts)
        t0 = time.perf_counter()
        vectors = np.asarray(embedder.embed_documents([chunk["text"] for chunk in chunks]), dtype=np.float32)
        seconds = time.perf_counter() - t0
        norms = np.linalg.norm(vectors, axis=1)
        if vectors.shape != (len(chunks), embedder.dimensions) or not np.isfinite(vectors).all() or not np.allclose(norms, 1, atol=1e-5):
            raise RuntimeError(f"Invalid {strategy} vectors")
        # NPZ stores float32 vectors alongside IDs; no pickle required when loading.
        target = output / f"vectors_{strategy}.npz"
        partial = output / f"vectors_{strategy}.partial.npz"
        np.savez_compressed(partial, vectors=vectors, chunk_ids=np.asarray([chunk["chunk_id"] for chunk in chunks]))
        partial.replace(target)
        counts = embedder.token_counts[before:]
        summary["strategies"][strategy] = {"chunks": len(chunks), "dimensions": embedder.dimensions,
            "shape": list(vectors.shape), "dtype": str(vectors.dtype),
            "chunk_file": str(source.relative_to(ROOT)).replace("\\", "/"),
            "chunk_file_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "vector_file_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "embedding_seconds": round(seconds, 3), "min_tokens_with_prefix": min(counts),
            "max_tokens_with_prefix": max(counts), "total_tokens_with_prefix": sum(counts),
            "truncated_inputs": 0, "min_norm": float(norms.min()), "max_norm": float(norms.max())}
        logging.info("Saved %s vectors: %s", strategy, vectors.shape)

    # Check query path using a technical sentence, without loading benchmark/gold/test.
    question = "Thủy điện tích năng phát điện như thế nào?"
    query = np.asarray(embedder.embed_query(question), dtype=np.float32)
    if query.shape != (embedder.dimensions,) or not np.isfinite(query).all() or not np.isclose(np.linalg.norm(query), 1, atol=1e-5):
        raise RuntimeError("Query vector is not compatible with document vectors")
    (output / "query_smoke.json").write_text(json.dumps({"question": question, "dimensions": embedder.dimensions,
        "vector": query.tolist(), "retrieval_executed": False}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Re-encode one document to check batching/padding invariance against saved output.
    repeated = np.asarray(embedder.embed_documents([chunks[0]["text"]])[0], dtype=np.float32)
    if not np.allclose(repeated, vectors[0], atol=1e-5):
        raise RuntimeError("Single-document and batch embeddings disagree")
    summary["checks"] = "pass: shape, finite values, unit norm, no truncation, query compatibility, batch invariance"
    summary["C_plan"] = "Reuse B vectors with exactly the same model; apply filter at vector-store query time"
    summary["total_seconds"] = round(time.perf_counter() - started, 3)
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Embedding failed; no mock fallback was used")
        raise
