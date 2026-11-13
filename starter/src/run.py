"""Evaluate fixed dev or frozen test questions against already-ingested A/B vectors."""
import argparse
import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv

from .embeddings import MyEmbedder
from .evaluation import evaluate_query, summarize
from .store import PgVectorStore

ROOT = Path(__file__).resolve().parents[2]


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev", "test"), default="dev")
    parser.add_argument("--output-dir", type=Path, help="Separate output folder for reproduction; preserve original holdout history")
    args = parser.parse_args()
    output = args.output_dir.resolve() if args.output_dir else ROOT / "results" / args.split
    test_already_seen = (ROOT / "results/test/summary.json").exists()
    frozen_pipeline = None
    verification = None
    if args.split == "test":
        if (output / "summary.json").exists():
            raise ValueError("Test results already exist; refusing to overwrite holdout history")
        verification = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "starter/scripts/freeze_configuration.py")],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        frozen_pipeline = json.loads((ROOT / "artifacts/frozen_pipeline.json").read_text(encoding="utf-8"))
    output.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler(output / "run.log", mode="w", encoding="utf-8"), logging.StreamHandler()])
    if verification:
        logging.info("Pre-test frozen configuration verification passed")
        (output / "pretest_verification.json").write_text(json.dumps({
            "checked_at_utc": datetime.now(timezone.utc).isoformat(), "result": verification,
            "frozen_pipeline_sha256": fingerprint(ROOT / "artifacts/frozen_pipeline.json"),
            "selected_strategy_before_test": frozen_pipeline["selected_strategy"],
            "selection_will_not_be_changed_using_test": True,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    load_dotenv(ROOT / "starter/.env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL missing")
    frozen = json.loads((ROOT / "benchmark/manifest.json").read_text(encoding="utf-8"))
    for path_key, hash_key in (("questions_file", "questions_sha256"), ("corpus_file", "corpus_sha256")):
        if fingerprint(ROOT / frozen[path_key]) != frozen[hash_key]:
            raise ValueError("Benchmark/corpus differs from frozen snapshot")
    questions = [q for q in json.loads((ROOT / frozen["questions_file"]).read_text(encoding="utf-8")) if q["split"] == args.split]
    if [q["id"] for q in questions] != frozen["splits"][args.split]:
        raise ValueError("Question assignment differs from frozen split")
    corpus = [json.loads(line) for line in (ROOT / frozen["corpus_file"]).read_text(encoding="utf-8").splitlines()]
    if len(corpus) < 30:
        raise ValueError("Corpus needs at least 30 content pages")
    embedding_summary = json.loads((ROOT / "results/embeddings/summary.json").read_text(encoding="utf-8"))
    config = json.loads((ROOT / "artifacts/embedding_config.json").read_text(encoding="utf-8"))
    if config != embedding_summary["model"]:
        raise ValueError("Embedding configuration changed")
    # Confirm database is the exact chunk/vector snapshot, not just the same model name.
    with psycopg.connect(url, connect_timeout=10) as connection:
        for strategy in ("A", "B"):
            info = embedding_summary["strategies"][strategy]
            path = ROOT / info["chunk_file"]
            vector_path = ROOT / f"results/embeddings/vectors_{strategy}.npz"
            if fingerprint(path) != info["chunk_file_sha256"] or fingerprint(vector_path) != info["vector_file_sha256"]:
                raise ValueError("Chunk/vector hash mismatch")
            chunks = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            rows = connection.execute("SELECT chunk_id, document_id, source, page, text, metadata, embedding::text FROM public.day6_chunks WHERE strategy=%s", (strategy,)).fetchall()
            indexed = {row[0]: row for row in rows}
            if set(indexed) != {c["chunk_id"] for c in chunks}:
                raise ValueError("Database snapshot IDs differ")
            with np.load(vector_path, allow_pickle=False) as vectors:
                if vectors["chunk_ids"].tolist() != [c["chunk_id"] for c in chunks]:
                    raise ValueError("Vector ID order differs")
                for i, chunk in enumerate(chunks):
                    row = indexed[chunk["chunk_id"]]
                    expected_metadata = {**chunk["metadata"], "embedding_model": config}
                    if row[1:6] != (chunk["document_id"], chunk["source"], chunk["page"], chunk["text"], expected_metadata) or not np.allclose(json.loads(row[6]), vectors["vectors"][i], atol=1e-7, rtol=1e-6):
                        raise ValueError("Database content/model/vector differs from snapshot")
    store = PgVectorStore(url, config["dimensions"])
    embedder = MyEmbedder()
    traces = []
    with (output / "traces.jsonl").open("w", encoding="utf-8") as stream:
        for question in questions:
            # No answer/evidence/source/page passed to embedder or retrieval.
            query_start = time.perf_counter()
            vector = embedder.embed_query(question["question"])
            query_seconds = time.perf_counter() - query_start
            for strategy in ("A", "B", "C"):
                filters = question.get("filter") if strategy == "C" else None
                started = time.perf_counter()
                hits = store.search(strategy, vector, top_k=3, filters=filters)
                search_seconds = time.perf_counter() - started
                trace = {**evaluate_query(question, hits), "strategy": strategy, "applied_filter": filters,
                         "query_embedding_seconds": query_seconds, "search_seconds": search_seconds}
                traces.append(trace)
                stream.write(json.dumps(trace, ensure_ascii=False) + "\n")
                stream.flush()
            logging.info("Completed %s for A/B/C", question["id"])
    summary = summarize(traces)
    summary.update({"status": "complete", "split": args.split, "trace_count": len(traces),
                    "test_executed": args.split == "test", "paid_service_cost_usd": 0,
                    "run_purpose": "reproduction_after_test_seen" if args.output_dir and test_already_seen else "original_run",
                    "executed_at_utc": datetime.now(timezone.utc).isoformat(),
                    "benchmark_sha256": frozen["questions_sha256"], "corpus_sha256": frozen["corpus_sha256"],
                    "model": config, "search_type": "exact_cosine_top3", "selection_rule": frozen["selection_rule"]})
    if frozen_pipeline:
        summary.update({"selected_strategy_before_test": frozen_pipeline["selected_strategy"],
                        "selection_changed_using_test": False,
                        "frozen_pipeline_sha256": fingerprint(ROOT / "artifacts/frozen_pipeline.json"),
                        "evidence_policy": frozen_pipeline["evaluation_policy"],
                        "semantic_equivalence_review": "pending; baseline quote matching saved before any adjudication"})
    (output / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [f"# Kết quả {args.split} — A/B/C", "", "Chấm tự động bảo thủ bằng toàn bộ quote trong một chunk đúng nguồn/trang; chưa chấm tương đương ngữ nghĩa hoặc grounding thủ công.", "", "| Strategy | Hit@1 | Evidence Hit@3 | Top-3 tuân thủ filter yêu cầu |", "|---|---|---|---|"]
    if args.output_dir and test_already_seen:
        lines.insert(2, "Lần chạy tái lập sau khi đã xem test; không phải holdout mới hoặc bằng chứng chọn lại cấu hình.")
    def label(ratio):
        return f"{ratio['numerator']}/{ratio['denominator']} ({ratio['value']:.1%})" if ratio["denominator"] else "N/A"
    for metric in summary["metrics"]:
        lines.append(f"| {metric['strategy']} | {label(metric['hit_at_1'])} | {label(metric['evidence_hit_at_3'])} | {label(metric['filter_compliance'])} |")
    lines.extend(["", "A/B không áp dụng filter; compliance đo mức khớp phạm vi được câu hỏi yêu cầu. C có áp dụng filter.", "", "| Câu | Strategy | Trang top-3 | Hit@1 | Hit@3 | Chẩn đoán |", "|---|---|---|---|---|---|"])
    for trace in traces:
        lines.append(f"| {trace['question_id']} | {trace['strategy']} | {', '.join(str(h['page']) for h in trace['hits'])} | {int(trace['hit_at_1'])} | {int(trace['evidence_hit_at_3'])} | {trace['diagnostic']} |")
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output / "manual_review_queue.json").write_text(json.dumps([trace for trace in traces if not trace["evidence_hit_at_3"]], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("model", "selection_rule")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("Evaluation failed; partial traces are not a complete run")
        raise
