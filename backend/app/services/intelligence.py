import os

from dotenv import load_dotenv
from groq import Groq

from app.schemas.intelligence import MeetingIntelligence


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_intelligence(transcript: list[dict]) -> MeetingIntelligence:

    timestamped_transcript = "\n".join(
        f"[{int(segment['start'] // 60):02d}:{int(segment['start'] % 60):02d}] "
        f"{segment['text']}"
        for segment in transcript
    )

    prompt = f"""
Analyze this meeting transcript and extract structured meeting intelligence.

Return ONLY valid JSON with exactly these fields:

{{
  "summary": ["string"],
  "action_items": [
    {{
      "id": 1,
      "task": "string",
      "owner": null,
      "due_date": null,
      "confidence": 0.95,
      "source_timestamp": "00:00",
      "status": "pending_review"
    }}
  ],
  "meeting_requests": [
    {{
      "id": 1,
      "topic": "string",
      "suggested_date": null,
      "suggested_time": null,
      "confidence": 0.70,
      "source_timestamp": "00:00",
      "status": "pending_review"
    }}
  ],
  "decisions": [
    {{
      "id": 1,
      "decision": "string",
      "confidence": 0.95,
      "source_timestamp": "00:00",
      "status": "detected"
    }}
  ],
  "open_questions": [
    {{
      "id": 1,
      "question": "string",
      "confidence": 0.80,
      "source_timestamp": "00:00",
      "status": "open"
    }}
  ],
  "risks": [
    {{
      "id": 1,
      "risk": "string",
      "confidence": 0.90,
      "source_timestamp": "00:00",
      "status": "open"
    }}
  ]
}}

Rules:

- Use only information explicitly supported by the transcript.
- Do not invent names, owners, dates, times, commitments, or decisions.
- Every extracted item needs its transcript timestamp.
- Copy source_timestamp from the relevant transcript statement.
- Use null when optional information is not available.
- Use [] when a category has no items.
- Action items must be explicit commitments or accepted requests.
- Tentative suggestions are not confirmed actions.
- Action items use status "pending_review".
- Meeting requests use status "pending_review".
- Decisions must be actual agreements, approvals, selections, or conclusions.
- Decisions use status "detected".
- Open questions must remain unresolved.
- Risks must be concrete blockers, reliability issues, project risks, or implementation problems.
- Risks use status "open".
- Confidence must be between 0.0 and 1.0.
- Summary must contain 3-6 concise important points.
- Preserve dates exactly as spoken. Do not calculate dates.
- Return ONLY the JSON object.

TRANSCRIPT:

{timestamped_transcript}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "system",
                "content": "Return only valid JSON. Never return an empty response."
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        max_tokens=4000,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    return MeetingIntelligence.model_validate_json(content)