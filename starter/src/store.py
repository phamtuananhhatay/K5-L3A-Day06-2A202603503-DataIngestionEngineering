"""Persistent chunk storage in PostgreSQL + pgvector."""
import math
from typing import Any

import psycopg
from psycopg import sql
from psycopg.types.json import Jsonb

from .models import Chunk


class PgVectorStore:
    def __init__(self, database_url: str, dimensions: int) -> None:
        if not database_url:
            raise ValueError("Database URL must not be empty")
        if type(dimensions) is not int or dimensions <= 0:
            raise ValueError("Dimensions must be a positive integer")
        self.database_url = database_url
        self.dimensions = dimensions

    def create_schema(self) -> None:
        """Create the lab table without dropping or resetting existing data."""
        with psycopg.connect(self.database_url, connect_timeout=10) as connection:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.execute(sql.SQL("""
                CREATE TABLE IF NOT EXISTS public.day6_chunks (
                    strategy text NOT NULL CHECK (length(strategy) > 0),
                    chunk_id text NOT NULL,
                    document_id text NOT NULL,
                    source text NOT NULL,
                    page integer NOT NULL CHECK (page > 0),
                    text text NOT NULL CHECK (length(text) > 0),
                    metadata jsonb NOT NULL CHECK (jsonb_typeof(metadata) = 'object'),
                    embedding vector({dimensions}) NOT NULL,
                    updated_at timestamptz NOT NULL DEFAULT now(),
                    PRIMARY KEY (strategy, chunk_id)
                )
            """).format(dimensions=sql.Literal(self.dimensions)))
            actual = connection.execute("""
                SELECT format_type(atttypid, atttypmod)
                FROM pg_attribute WHERE attrelid = 'public.day6_chunks'::regclass
                AND attname = 'embedding' AND NOT attisdropped
            """).fetchone()
            if actual != (f"vector({self.dimensions})",):
                raise ValueError("Existing embedding column has incompatible dimensions; no data was reset")
            connection.execute("CREATE INDEX IF NOT EXISTS day6_chunks_document_idx ON public.day6_chunks (strategy, document_id)")
            connection.execute("CREATE INDEX IF NOT EXISTS day6_chunks_section_idx ON public.day6_chunks (strategy, (metadata->>'section'))")

    def upsert(self, strategy: str, chunks: list[Chunk], vectors: list[list[float]]) -> None:
        """Replace complete snapshots of the documents supplied for one strategy.

        Supply all chunks of every included document, never a partial batch. Other
        documents/strategies are preserved. Empty input is rejected to prevent an
        ambiguous deletion. Obsolete chunks are removed in the same transaction.
        """
        if not isinstance(strategy, str) or not strategy.strip():
            raise ValueError("Strategy must not be empty")
        if not chunks or len(chunks) != len(vectors):
            raise ValueError("Supply non-empty chunks with exactly one vector per chunk")
        if len({chunk.chunk_id for chunk in chunks}) != len(chunks):
            raise ValueError("Duplicate chunk IDs in input")
        records = []
        for chunk, vector in zip(chunks, vectors):
            if (not chunk.chunk_id or not chunk.document_id or not chunk.source
                    or type(chunk.page) is not int or chunk.page <= 0 or not chunk.text.strip()
                    or not isinstance(chunk.metadata.get("section"), str) or not chunk.metadata["section"].strip()):
                raise ValueError("Chunk requires ID, source, positive page, text and section metadata")
            if len(vector) != self.dimensions:
                raise ValueError(f"Vector must have {self.dimensions} dimensions")
            values = [float(value) for value in vector]
            if not all(math.isfinite(value) for value in values) or not any(values):
                raise ValueError("Vector must be finite and non-zero")
            # Bind a vector text literal as a SQL parameter, never interpolate SQL values.
            literal = "[" + ",".join(repr(value) for value in values) + "]"
            records.append((strategy, chunk.chunk_id, chunk.document_id, chunk.source,
                            chunk.page, chunk.text, Jsonb(chunk.metadata), literal))
        with psycopg.connect(self.database_url, connect_timeout=10) as connection:
            # Serialize small lab imports to avoid racing snapshot deletion/upsert.
            connection.execute("LOCK TABLE public.day6_chunks IN SHARE ROW EXCLUSIVE MODE")
            with connection.cursor() as cursor:
                cursor.executemany("""
                    INSERT INTO public.day6_chunks
                    (strategy, chunk_id, document_id, source, page, text, metadata, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::vector)
                    ON CONFLICT (strategy, chunk_id) DO UPDATE SET
                        document_id = EXCLUDED.document_id, source = EXCLUDED.source,
                        page = EXCLUDED.page, text = EXCLUDED.text, metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding, updated_at = now()
                """, records)
            connection.execute("""
                DELETE FROM public.day6_chunks
                WHERE strategy = %s AND document_id = ANY(%s::text[])
                AND NOT (chunk_id = ANY(%s::text[]))
            """, (strategy, sorted({chunk.document_id for chunk in chunks}), [chunk.chunk_id for chunk in chunks]))

    def search(self, strategy: str, query_vector: list[float], top_k: int = 3,
               filters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Exact cosine top-k after AND filters. C reuses stored B vectors.

        score = cosine similarity = 1 - cosine_distance (higher is closer).
        Supports equality on section/report_year metadata and source/document/page.
        The low-level store accepts filters for any strategy; experiment callers
        must pass no filter for A/B. No matches returns [], with no fallback.
        """
        if strategy not in ("A", "B", "C"):
            raise ValueError("Search strategy must be A, B or C")
        if type(top_k) is not int or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        if len(query_vector) != self.dimensions:
            raise ValueError(f"Query vector must have {self.dimensions} dimensions")
        values = [float(value) for value in query_vector]
        if not all(math.isfinite(value) for value in values) or not any(values):
            raise ValueError("Query vector must be finite and non-zero")
        if filters is not None and not isinstance(filters, dict):
            raise ValueError("Filters must be a dictionary or None")
        allowed = {"section": str, "report_year": int, "document_id": str, "source": str, "page": int}
        predicates = [sql.SQL("strategy = %s")]
        stored_strategy = "B" if strategy == "C" else strategy
        params: list[Any] = [stored_strategy]
        for key, value in sorted((filters or {}).items()):
            if key not in allowed or type(value) is not allowed[key]:
                raise ValueError(f"Unsupported filter or invalid type: {key}")
            if isinstance(value, str) and not value.strip():
                raise ValueError(f"Filter {key} must not be empty")
            if key == "page" and value <= 0:
                raise ValueError("Page filter must be positive")
            if key in ("document_id", "source", "page"):
                predicates.append(sql.SQL("{} = %s").format(sql.Identifier(key)))
                params.append(value)
            elif key == "section":
                predicates.append(sql.SQL("metadata->>'section' = %s"))
                params.append(value)
            else:
                predicates.append(sql.SQL("metadata @> %s"))
                params.append(Jsonb({key: value}))
        literal = "[" + ",".join(repr(value) for value in values) + "]"
        params.extend((literal, top_k))
        # Materializing candidates ensures exact ranking after filtering, even if
        # an approximate vector index is added to the base table in the future.
        query = sql.SQL("""
            WITH candidates AS MATERIALIZED (
                SELECT chunk_id, document_id, source, page, text, metadata, embedding
                FROM public.day6_chunks WHERE {where}
            )
            SELECT chunk_id, document_id, source, page, text, metadata,
                   embedding <=> %s::vector AS cosine_distance
            FROM candidates ORDER BY cosine_distance ASC, chunk_id ASC LIMIT %s
        """).format(where=sql.SQL(" AND ").join(predicates))
        with psycopg.connect(self.database_url, connect_timeout=10) as connection:
            rows = connection.execute(query, params).fetchall()
        return [{"rank": rank, "strategy": strategy, "stored_strategy": stored_strategy,
                 "chunk_id": row[0], "document_id": row[1], "source": row[2], "page": row[3],
                 "text": row[4], "metadata": row[5], "cosine_distance": float(row[6]),
                 "score": 1.0 - float(row[6]), "score_type": "cosine_similarity"}
                for rank, row in enumerate(rows, 1)]
