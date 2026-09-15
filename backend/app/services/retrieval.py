from app.services.vector_store import FAISSVectorStore


def search_meetings(query: str, top_k: int = 5) -> list[dict]:
    store = FAISSVectorStore.load()

    return store.search(
        query=query,
        top_k=top_k,
    )