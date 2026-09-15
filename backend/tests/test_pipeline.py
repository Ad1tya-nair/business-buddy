import sys
from pathlib import Path

from app.services.transcription import transcribe_audio
from app.services.intelligence import extract_intelligence


if len(sys.argv) != 2:
    print("Usage: python -m tests.test_pipeline <audio_file>")
    sys.exit(1)


audio_path = Path(sys.argv[1])

if not audio_path.exists():
    print(f"File not found: {audio_path}")
    sys.exit(1)


print("\n" + "=" * 60)
print("STEP 1: TRANSCRIPTION")
print("=" * 60)

segments = transcribe_audio(str(audio_path))

for segment in segments:
    minutes = int(segment["start"] // 60)
    seconds = int(segment["start"] % 60)

    timestamp = f"[{minutes:02d}:{seconds:02d}]"

    print(
        f"{timestamp} {segment['text']}"
    )


# Convert structured segments into the format
# expected by the intelligence service.

transcript = "\n".join(
    f"[{int(s['start'] // 60):02d}:{int(s['start'] % 60):02d}] {s['text']}"
    for s in segments
)


print("\n" + "=" * 60)
print("STEP 2: INTELLIGENCE EXTRACTION")
print("=" * 60)

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