from groq import Groq
from dotenv import load_dotenv
import os

from app.services.retrieval import search_meetings

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def answer_question(question: str, top_k: int = 5) -> dict:
    results = search_meetings(
        query=question,
        top_k=top_k,
    )

    if not results:
        return {
            "answer": "I couldn't find relevant information in the meeting records.",
            "sources": [],
        }

    context_parts = []

    for i, result in enumerate(results, start=1):
        metadata = result["metadata"]

        context_parts.append(
            f"""
SOURCE {i}
Meeting ID: {metadata["meeting_id"]}
Timestamp: {metadata["start_time"]} - {metadata["end_time"]}
Transcript:
{metadata["text"]}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
Answer the user's question using ONLY the meeting transcript sources below.

USER QUESTION:
{question}

MEETING SOURCES:
{context}

RULES:
- Use only information supported by the provided sources.
- Do not invent facts.
- If the sources do not contain enough information, say that the meeting records do not provide enough information.
- You may combine information from multiple meetings when relevant.
- Do not mention information that is unrelated to the question.
- Give a concise, direct answer.
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "You are a meeting intelligence assistant. Answer only from the provided meeting evidence.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        max_tokens=1000,
    )

    answer = response.choices[0].message.content.strip()

    sources = [
        {
            "meeting_id": result["metadata"]["meeting_id"],
            "segment_ids": result["metadata"]["segment_ids"],
            "start_time": result["metadata"]["start_time"],
            "end_time": result["metadata"]["end_time"],
            "text": result["metadata"]["text"],
            "score": result["score"],
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources,
    }