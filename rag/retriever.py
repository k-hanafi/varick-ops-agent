"""Retrieve the policy passages most relevant to a query via cosine similarity."""

import json
from pathlib import Path

import numpy as np

from rag.embeddings import embed

INDEX_PATH = Path(__file__).resolve().parent / "policy_index.json"


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def search(query: str, k: int = 3) -> list[dict]:
    if not INDEX_PATH.exists():
        raise FileNotFoundError("Policy index missing. Run: python -m rag.index")
    index = json.loads(INDEX_PATH.read_text())
    query_vec = np.array(embed([query])[0])
    scored = [
        {
            "source": doc["source"],
            "text": doc["text"],
            "score": _cosine(query_vec, np.array(doc["embedding"])),
        }
        for doc in index
    ]
    scored.sort(key=lambda r: r["score"], reverse=True)
    return scored[:k]
