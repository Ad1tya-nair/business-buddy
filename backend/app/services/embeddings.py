from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def embed_texts(texts: list[str]):
    """
    Convert a list of text strings into vector embeddings.
    """
    return model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=False,
    )


def embed_query(query: str):
    """
    Convert a search query into a vector embedding.
    """
    return model.encode(
        [query],
        normalize_embeddings=True,
        show_progress_bar=False,
    )[0]