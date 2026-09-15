from app.database import get_connection
from app.services.vector_store import FAISSVectorStore


def build_chunks(rows: list[dict], max_chars: int = 250) -> tuple[list[str], list[dict]]:
    """
    Combine consecutive transcript segments into larger semantic chunks.

    A chunk keeps the original transcript wording but combines nearby
    segments so that short fragments such as "problems." are not indexed
    independently.
    """

    texts = []
    metadata = []

    current_text = []
    current_start = None
    current_end = None
    current_meeting_id = None
    current_segment_ids = []

    for row in rows:
        text = row["text"].strip()

        if not text:
            continue

        # Start a new chunk when meeting changes.
        if current_meeting_id is not None and row["meeting_id"] != current_meeting_id:
            if current_text:
                texts.append(" ".join(current_text))
                metadata.append({
                    "meeting_id": current_meeting_id,
                    "segment_ids": current_segment_ids,
                    "start_time": current_start,
                    "end_time": current_end,
                    "text": " ".join(current_text),
                })

            current_text = []
            current_start = None
            current_end = None
            current_segment_ids = []

        # Start the chunk.
        if not current_text:
            current_start = row["start_time"]
            current_meeting_id = row["meeting_id"]

        candidate = " ".join(current_text + [text])

        # If adding this segment would make the chunk too large,
        # save the current chunk first.
        if current_text and len(candidate) > max_chars:
            texts.append(" ".join(current_text))
            metadata.append({
                "meeting_id": current_meeting_id,
                "segment_ids": current_segment_ids,
                "start_time": current_start,
                "end_time": current_end,
                "text": " ".join(current_text),
            })

            current_text = [text]
            current_start = row["start_time"]
            current_end = row["end_time"]
            current_segment_ids = [row["id"]]

        else:
            current_text.append(text)
            current_end = row["end_time"]
            current_segment_ids.append(row["id"])

    # Save final chunk.
    if current_text:
        texts.append(" ".join(current_text))
        metadata.append({
            "meeting_id": current_meeting_id,
            "segment_ids": current_segment_ids,
            "start_time": current_start,
            "end_time": current_end,
            "text": " ".join(current_text),
        })

    return texts, metadata


def rebuild_index() -> FAISSVectorStore:
    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            id,
            meeting_id,
            start_time,
            end_time,
            text
        FROM transcript_segments
        ORDER BY meeting_id, start_time
        """
    ).fetchall()

    connection.close()

    store = FAISSVectorStore()

    texts, metadata = build_chunks(rows)

    store.add(texts, metadata)
    store.save()

    return store