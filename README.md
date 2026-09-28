# BusinessBuddy

BusinessBuddy turns meeting recordings into searchable transcripts and structured follow-up. Upload an audio recording to generate a summary, action items, decisions, open questions, risks, and meeting requests. The app also provides task and calendar views, semantic meeting search, and question answering grounded in transcript content.

## Stack

- Frontend: React, Vite, React Router, and Tailwind CSS
- Backend: FastAPI and SQLite
- Meeting intelligence: Groq API
- Transcription: faster-whisper, running locally on CPU
- Semantic search: SentenceTransformers embeddings and FAISS

## Requirements

- Python 3.11 recommended
- Node.js 20.19+ or 22.12+
- A Groq API key

The backend imports `faiss`, `sentence_transformers`, and `numpy`, which are not currently listed in `requirement.txt`; the install command below includes them.

## Run Locally

### Backend

In PowerShell, from the repository root:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r ..\requirement.txt faiss-cpu sentence-transformers numpy
$env:GROQ_API_KEY = "your_groq_api_key"
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive API documentation is at `http://127.0.0.1:8000/docs` and the health check is at `http://127.0.0.1:8000/health`.

### Frontend

Open a second PowerShell terminal from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal, usually `http://localhost:5173`. The frontend uses `http://127.0.0.1:8000` by default. To use a different API URL, set `VITE_API_BASE_URL` before starting Vite.

The first backend startup may download the Whisper and SentenceTransformers models. These models run locally; meeting analysis also requires a working Groq API key.

## Demo Sign-In

The app seeds these local demo accounts when initializing its database. Each password matches its username:

| Username | Role |
| --- | --- |
| `lead` | Team Lead |
| `priya` | Member |
| `simon` | Member |
| `mathew` | Member |
| `joseph` | Member |

These credentials and the app's simple token-based authentication are for local demonstration only, not production use.

## Optional Email Notifications

Action-item email notifications require SMTP configuration. Set these environment variables before starting the backend:

```text
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM
```

Do not commit API keys, email credentials, or other secrets.

## Local Data

The backend creates its SQLite database and generated meeting data under `backend/data/`. This directory is ignored by Git and is local to each installation.

See [architecture.md](architecture.md) for more detail on the application structure and processing pipeline.