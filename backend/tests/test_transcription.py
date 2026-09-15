import sys
from pathlib import Path

from app.services.transcription import transcribe_audio


if len(sys.argv) != 2:
    print("Usage: python -m tests.test_transcription <audio_file>")
    sys.exit(1)


audio_path = Path(sys.argv[1])

if not audio_path.exists():
    print(f"File not found: {audio_path}")
    sys.exit(1)


print("\nTRANSCRIPT\n")

transcript = transcribe_audio(str(audio_path))

print(transcript)