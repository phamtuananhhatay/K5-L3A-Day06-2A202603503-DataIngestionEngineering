"""Choose a real embedding provider (API or local) and implement this contract."""
import hashlib
import json
import logging
from pathlib import Path
from typing import Protocol

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

logger = logging.getLogger(__name__)


class Embedder(Protocol):
    model_name: str
    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per input text, in the same order."""
        ...

    def embed_query(self, question: str) -> list[float]:
        """Return a query vector compatible with the stored document vectors."""
        ...


class MyEmbedder:
    """Pinned multilingual E5 ONNX CPU adapter; no network or mock fallback.

    Follows the model card: query/passage prefixes, masked mean pooling, L2 norm.
    Long input is rejected so evidence is never silently truncated.
    """

    def __init__(self, model_name: str = "intfloat/multilingual-e5-small", *, config_path: Path | None = None) -> None:
        root = Path(__file__).resolve().parents[2]
        self.config = json.loads((config_path or root / "artifacts/embedding_config.json").read_text(encoding="utf-8"))
        if model_name != self.config["model_name"]:
            raise ValueError("Model must match the pinned embedding configuration")
        self.model_name = model_name
        self.dimensions = self.config["dimensions"]
        self.token_counts: list[int] = []
        directory = root / self.config["local_directory"]
        for entry in self.config["files"]:
            path = directory / entry["local_name"]
            if not path.is_file():
                raise FileNotFoundError(f"Missing {path}; run scripts/download_embedding_model.ps1 first")
            digest = self._file_hash(path)
            if digest != entry["sha256"]:
                raise ValueError(f"Model file checksum mismatch: {path}")
        self.tokenizer = Tokenizer.from_file(str(directory / "tokenizer.json"))
        self.tokenizer.no_truncation()
        pad_id = self.tokenizer.token_to_id("<pad>")
        if pad_id is None:
            raise ValueError("Tokenizer has no expected <pad> token")
        self.tokenizer.enable_padding(pad_id=pad_id, pad_token="<pad>")
        options = ort.SessionOptions()
        options.intra_op_num_threads = self.config["cpu_threads"]
        options.inter_op_num_threads = 1
        self.session = ort.InferenceSession(str(directory / "model.onnx"), sess_options=options, providers=["CPUExecutionProvider"])
        if self.session.get_outputs()[0].shape[-1] != self.dimensions:
            raise ValueError("Model output dimensions differ from config")

    @staticmethod
    def _file_hash(path: Path) -> str:
        with path.open("rb") as stream:
            return hashlib.file_digest(stream, "sha256").hexdigest()

    def _encode(self, texts: list[str], prefix: str) -> list[list[float]]:
        if any(not isinstance(text, str) or not text.strip() for text in texts):
            raise ValueError("Embedding input must contain non-empty strings")
        result = []
        batch_size = self.config["batch_size"]
        for start in range(0, len(texts), batch_size):
            encoded = self.tokenizer.encode_batch([prefix + text for text in texts[start:start + batch_size]])
            lengths = [sum(item.attention_mask) for item in encoded]
            if max(lengths) > self.config["max_tokens"]:
                raise ValueError(f"Input exceeds {self.config['max_tokens']} tokens; shorten chunks explicitly")
            available = {"input_ids": np.asarray([item.ids for item in encoded], dtype=np.int64),
                         "attention_mask": np.asarray([item.attention_mask for item in encoded], dtype=np.int64),
                         "token_type_ids": np.asarray([item.type_ids for item in encoded], dtype=np.int64)}
            feeds = {item.name: available[item.name] for item in self.session.get_inputs()}
            hidden = self.session.run(None, feeds)[0]
            mask = available["attention_mask"][..., None].astype(np.float32)
            pooled = (hidden * mask).sum(axis=1) / mask.sum(axis=1)
            norms = np.linalg.norm(pooled, axis=1, keepdims=True)
            if not np.isfinite(pooled).all() or np.any(norms <= 0):
                raise RuntimeError("Embedding backend returned non-finite or zero vectors")
            vectors = (pooled / norms).astype(np.float32)
            if vectors.shape != (len(encoded), self.dimensions):
                raise RuntimeError("Embedding batch shape mismatch")
            result.extend(vectors.tolist())
            self.token_counts.extend(lengths)
            logger.info("Embedded %d/%d inputs", min(start + batch_size, len(texts)), len(texts))
        return result

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts, self.config["document_prefix"])

    def embed_query(self, question: str) -> list[float]:
        return self._encode([question], self.config["query_prefix"])[0]
