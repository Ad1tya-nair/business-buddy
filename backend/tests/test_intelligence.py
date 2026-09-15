import sys
from pathlib import Path

from app.services.intelligence import extract_intelligence


if len(sys.argv) != 2:
    print("Usage: python -m tests.test_intelligence <transcript_file>")
    sys.exit(1)


transcript_path = Path(sys.argv[1])

if not transcript_path.exists():
    print(f"File not found: {transcript_path}")
    sys.exit(1)


transcript = transcript_path.read_text(encoding="utf-8")

result = extract_intelligence(transcript)

print("\nSUMMARY")
for item in result.summary:
    print("-", item)

print("\nACTION ITEMS")
for item in result.action_items:
    print(item)

print("\nMEETING REQUESTS")
for item in result.meeting_requests:
    print(item)

print("\nDECISIONS")
for item in result.decisions:
    print(item)

print("\nOPEN QUESTIONS")
for item in result.open_questions:
    print(item)