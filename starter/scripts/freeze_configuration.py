"""Create once, or verify, the pre-test pipeline/evidence snapshot (no inference)."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "artifacts/frozen_pipeline.json"
FILES = [
    "artifacts/chunking_config.json", "artifacts/embedding_config.json",
    "benchmark/manifest.json", "benchmark/questions.json", "benchmark/evidence_policy.json",
    "benchmark/dev_evidence_additions.json", "data/manifest.json", "data/processed/esmap_pages.jsonl",
    "starter/src/ingestion.py", "starter/src/chunking.py", "starter/src/embeddings.py",
    "starter/src/store.py", "starter/src/evaluation.py", "starter/scripts/review_dev.py",
    "starter/requirements-lock.txt", "results/chunking/chunks_A.jsonl", "results/chunking/chunks_B.jsonl",
    "results/embeddings/vectors_A.npz", "results/embeddings/vectors_B.npz",
    "results/dev/traces.jsonl", "results/dev/summary.json", "results/dev/review_decisions.json",
    "results/dev/reviewed/traces.jsonl", "results/dev/reviewed/summary.json", "results/dev/reviewed/selection.json",
]


def fingerprint(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--create",action="store_true",help="Create initial snapshot; refuse overwrite")
    args=parser.parse_args()
    if args.create:
        if TARGET.exists():
            raise ValueError("Snapshot already exists; refusing to overwrite pre-test history")
        def read(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
        reviewed=read("results/dev/reviewed/summary.json")
        selected=read("results/dev/reviewed/selection.json")
        if selected["selected_strategy"] != "C" or selected["test_executed"] or reviewed["test_executed"]:
            raise ValueError("Unexpected selection/test state; inspect before freezing")
        source=read("data/manifest.json")
        hashes={path:fingerprint(ROOT/path) for path in FILES}
        hashes[source["local_path"]]=fingerprint(ROOT/source["local_path"])
        if hashes[source["local_path"]] != source["sha256"]:
            raise ValueError("Source PDF changed")
        snapshot={"version":"pipeline-pretest-v1", "frozen_at_utc":datetime.now(timezone.utc).isoformat(),
                  "status":"frozen_before_test", "selected_strategy":"C",
                  "selection_basis":"Reviewed dev Hit@3 ties B at 10/15, Hit@1 C=9/15 exceeds B=8/15. No resource tie-break needed.",
                  "chunking":read("artifacts/chunking_config.json"),"embedding":read("artifacts/embedding_config.json"),
                  "retrieval":{"store":"PostgreSQL+pgvector","table":"public.day6_chunks","metric":"cosine",
                               "search_type":"exact","top_k":3,"strategies":{"A":"A vectors, no filter","B":"B vectors, no filter","C":"B vectors, supplied question filter only"},
                               "tie_break":"cosine_distance ascending then chunk_id ascending"},
                  "evaluation_policy":"benchmark/evidence_policy.json", "reviewer":reviewed["reviewer"],
                  "reviewed_dev_metrics":reviewed["metrics"],"test_executed":False,
                  "test_rule":"Evaluate all strategies without tuning/reselection. Apply frozen evidence policy; disclose any post-retrieval adjudication separately.",
                  "file_sha256":hashes}
        with TARGET.open("x",encoding="utf-8") as stream:
            stream.write(json.dumps(snapshot,ensure_ascii=False,indent=2)+"\n")
        print("Created pre-test snapshot:",TARGET.relative_to(ROOT))
    frozen=json.loads(TARGET.read_text(encoding="utf-8"))
    changed=[path for path,digest in frozen["file_sha256"].items() if not (ROOT/path).is_file() or fingerprint(ROOT/path)!=digest]
    if changed:
        raise ValueError("Frozen files changed: "+", ".join(changed))
    print(f"PASS: {len(frozen['file_sha256'])} frozen files match; selected strategy {frozen['selected_strategy']}; no test run performed")


if __name__ == "__main__":
    main()
