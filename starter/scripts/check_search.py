"""Read-only integration checks of cosine ranking and metadata filters; no benchmark."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "starter/scripts"))
from search_chunks import prepare_search


def main():
    store, embedder = prepare_search("B")
    question = "Báo cáo mô tả các giải pháp lưu trữ năng lượng như thế nào?"
    query = embedder.embed_query(question)
    traces = []
    with np.load(ROOT / "results/embeddings/vectors_B.npz", allow_pickle=False) as saved:
        b_vectors = saved["vectors"].astype(np.float64)
        ids = saved["chunk_ids"].tolist()
    chunks = [json.loads(line) for line in (ROOT / "results/chunking/chunks_B.jsonl").read_text(encoding="utf-8").splitlines()]
    if ids != [chunk["chunk_id"] for chunk in chunks]:
        raise ValueError("Saved vector/chunk order mismatch")
    q = np.asarray(query, dtype=np.float64)
    # Independent numeric oracle only for tests; application retrieval runs in SQL.
    scores = b_vectors @ q / (np.linalg.norm(b_vectors, axis=1) * np.linalg.norm(q))
    for strategy, filters in (("A", None), ("B", None), ("C", None), ("C", {"section": "Renewable Energy"}),
                              ("C", {"section": "Renewable Energy", "report_year": 2021})):
        hits = store.search(strategy, query, filters=filters)
        if len(hits) != 3 or [h["rank"] for h in hits] != [1, 2, 3]:
            raise ValueError("Unexpected top-3 result count/ranks")
        if any(hits[i]["score"] < hits[i+1]["score"] for i in range(len(hits)-1)):
            raise ValueError("Cosine scores are not descending")
        if filters and any(any(hit["metadata"].get(key) != value for key, value in filters.items()) for hit in hits):
            raise ValueError("Metadata filter was not applied")
        if strategy in ("B", "C"):
            eligible = [i for i,c in enumerate(chunks) if not filters or all(c["metadata"].get(k) == v for k,v in filters.items())]
            expected = sorted(eligible, key=lambda i: (-scores[i], ids[i]))[:3]
            if [hit["chunk_id"] for hit in hits] != [ids[i] for i in expected]:
                raise ValueError("SQL top-3 differs from independent cosine ranking")
            if any(not np.isclose(hit["score"], scores[i], atol=1e-5) for hit,i in zip(hits,expected)):
                raise ValueError("SQL cosine score mismatch")
        traces.append({"question": question, "strategy": strategy, "filter": filters, "hits": hits})
    if [h["chunk_id"] for h in traces[1]["hits"]] != [h["chunk_id"] for h in traces[2]["hits"]]:
        raise ValueError("C without filter must equal B")
    for section in ("no-such-section", "Renewable Energy' OR 1=1 --"):
        if store.search("C", query, filters={"section": section}) != []:
            raise ValueError("Unknown or SQL-like filter must not bypass equality")
    # Select a naturally small page, without reading gold questions/test labels.
    page = min({c["page"] for c in chunks}, key=lambda p: sum(c["page"] == p for c in chunks))
    small = store.search("C", query, filters={"page": page})
    expected_count = min(3, sum(c["page"] == page for c in chunks))
    if len(small) != expected_count or any(hit["page"] != page for hit in small):
        raise ValueError("Small candidate set must return only available matches")
    invalid_cases = [dict(query_vector=query[:-1]), dict(query_vector=[0.0]*384),
                     dict(query_vector=[float('nan')]*384), dict(query_vector=query,top_k=0),
                     dict(query_vector=query,filters={"section": 2021}),
                     dict(query_vector=query,filters={"unknown": "x"})]
    for kwargs in invalid_cases:
        try:
            store.search("B", **kwargs)
        except ValueError:
            pass
        else:
            raise ValueError("Invalid search input was accepted")
    out = ROOT / "results/search"
    out.mkdir(parents=True, exist_ok=True)
    (out / "smoke_traces.json").write_text(json.dumps(traces,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary = {"status":"pass", "search_type":"exact_cosine_in_pgvector", "default_top_k":3,
               "checks":["A/B/C top-3", "B/C without filter agree", "section and combined filters", "numeric cosine ranking matches SQL for B/C", "unknown/SQL-like filter yields no matches", "fewer than 3 candidates", "invalid input rejection"],
               "small_candidate_page":page, "small_candidate_results":len(small),
               "benchmark_executed":False, "database_mutated":False}
    (out / "check_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
