"""Embed each policy doc once and save the vectors to disk."""

import json
from pathlib import Path

from rag.embeddings import embed

POLICY_DIR = Path(__file__).resolve().parent.parent / "policies"
INDEX_PATH = Path(__file__).resolve().parent / "policy_index.json"


def build() -> None:
    docs = [
        {"source": path.name, "text": path.read_text()}
        for path in sorted(POLICY_DIR.glob("*.md"))
    ]
    vectors = embed([d["text"] for d in docs])
    for doc, vector in zip(docs, vectors):
        doc["embedding"] = vector
    INDEX_PATH.write_text(json.dumps(docs))
    print(f"Indexed {len(docs)} policy docs -> {INDEX_PATH}")


if __name__ == "__main__":
    build()
