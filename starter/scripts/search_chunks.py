"""Ask a question using local E5 + exact pgvector cosine retrieval (no gold data)."""
import argparse
import json
import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter"))
from src.embeddings import MyEmbedder
from src.store import PgVectorStore


def prepare_search(strategy):
    load_dotenv(ROOT / "starter/.env")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL missing; see starter/.env.example")
    config = json.loads((ROOT / "artifacts/embedding_config.json").read_text(encoding="utf-8"))
    with psycopg.connect(url, connect_timeout=10) as connection:
        models = connection.execute("SELECT DISTINCT metadata->'embedding_model' FROM public.day6_chunks WHERE strategy=%s",
                                    ("B" if strategy == "C" else strategy,)).fetchall()
    if not models or any(model[0] != config for model in models):
        raise ValueError("Stored model configuration is missing/mixed or differs from query configuration")
    return PgVectorStore(url, config["dimensions"]), MyEmbedder()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", required=True)
    parser.add_argument("--strategy", choices=("A", "B", "C"), default="B")
    parser.add_argument("--section", help="User-supplied section, allowed only for strategy C")
    parser.add_argument("--output", type=Path, help="Optional JSON trace file")
    args = parser.parse_args()
    if args.section is not None and args.strategy != "C":
        parser.error("A/B run without filters; use --strategy C with --section")
    store, embedder = prepare_search(args.strategy)
    filters = {"section": args.section} if args.section is not None else None
    vector = embedder.embed_query(args.question)
    hits = store.search(args.strategy, vector, top_k=3, filters=filters)
    result = {"question": args.question, "strategy": args.strategy, "filter": filters,
              "model_name": embedder.model_name, "revision": embedder.config["revision"],
              "search_type": "exact_cosine", "top_k": 3, "returned_count": len(hits), "hits": hits}
    formatted = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(formatted + "\n", encoding="utf-8")
    print(formatted)


if __name__ == "__main__":
    main()
