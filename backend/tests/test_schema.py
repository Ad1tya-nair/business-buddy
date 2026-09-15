from app.schemas.intelligence import MeetingIntelligence


data = {
    "summary": [
        "The team prioritized the mobile release for Q3."
    ],
    "action_items": [
        {
            "id": "ai_001",
            "task": "Complete API testing",
            "owner": "Rahul",
            "due_date": "Friday",
            "confidence": 0.94,
            "source_timestamp": "00:03:18",
            "status": "pending_review"
        }
    ],
    "meeting_requests": [],
    "decisions": [
        {
            "id": "dec_001",
            "decision": "Prioritize the mobile release over the analytics dashboard.",
            "confidence": 0.96,
            "source_timestamp": "00:05:10"
        }
    ],
    "open_questions": []
}


result = MeetingIntelligence.model_validate(data)

print(result)