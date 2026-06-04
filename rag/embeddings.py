"""Shared embedding helper. The indexer and retriever MUST use the same model,
or the vectors live in different spaces and similarity is meaningless."""

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

EMBED_MODEL = "text-embedding-3-small"


def embed(texts: list[str]) -> list[list[float]]:
    client = OpenAI()
    resp = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in resp.data]
