import json
from pathlib import Path

import faiss
import numpy as np

from app.services.embeddings import embed_texts


INDEX_DIR = Path("data/faiss")
INDEX_PATH = INDEX_DIR / "meetings.index"
METADATA_PATH = INDEX_DIR / "metadata.json"


class FAISSVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata = []

    def add(self, texts: list[str], metadata: list[dict]):
        if not texts:
            return

        embeddings = embed_texts(texts)

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        self.index.add(embeddings)
        self.metadata.extend(metadata)

    def search(self, query: str, top_k: int = 5):
        if self.index.ntotal == 0:
            return []

        query_embedding = embed_texts([query])

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        scores, indices = self.index.search(
            query_embedding,
            min(top_k, self.index.ntotal)
        )

        results = []

        for score, index in zip(scores[0], indices[0]):
            results.append({
                "score": float(score),
                "metadata": self.metadata[index],
            })

        return results

    def save(self):
        INDEX_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        faiss.write_index(
            self.index,
            str(INDEX_PATH)
        )

        with open(
            METADATA_PATH,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.metadata,
                file,
                indent=2
            )

    @classmethod
    def load(cls, dimension: int = 384):
        store = cls(dimension)

        if not INDEX_PATH.exists() or not METADATA_PATH.exists():
            return store

        store.index = faiss.read_index(
            str(INDEX_PATH)
        )

        with open(
            METADATA_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            store.metadata = json.load(file)

        return store