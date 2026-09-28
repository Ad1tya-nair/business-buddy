# BusinessBuddy Architecture

## 1. Overview

BusinessBuddy is an AI-powered meeting intelligence application that converts uploaded audio meetings into structured business artifacts such as action items, decisions, risks, meeting requests, and searchable transcript evidence. The system combines:

- FastAPI backend for orchestration and business logic
- SQLite for operational records and team state
- FAISS for semantic search over transcript chunks
- Groq-hosted LLMs for transcript analysis and grounded Q&A
- faster-whisper for local transcription
- SentenceTransformers for embeddings
- React + Vite frontend for user workflows and dashboards

This project is organized as a monolithic service with a clear separation between:

1. Mutable operational data in SQLite
2. Immutable transcript evidence in FAISS
3. AI-generated intelligence extracted from meeting transcripts
4. A user-facing React application that drives review and action workflows

---

## 2. High-Level Architecture

The application follows a layered architecture:

- Presentation layer: React frontend running in Vite
- API layer: FastAPI server with authenticated endpoints
- Service layer: transcription, intelligence extraction, embeddings, vector indexing, retrieval, and email
- Persistence layer: SQLite database and FAISS vector index
- External AI services: Groq and local transcription model

```text
User / Browser
    |
    v
React Frontend (Vite + React Router)
    |
    | HTTP / JSON / FormData / Bearer token
    v
FastAPI Backend (app/main.py)
    |
    +--> SQLite database (meeting_intelligence.db)
    |
    +--> Transcript + intelligence processing services
    |       - faster-whisper
    |       - Groq LLM
    |       - Pydantic validation
    |
    +--> FAISS vector store (data/faiss/meetings.index + metadata.json)
    |
    +--> Optional SMTP email notifications
```

---

## 3. Project Structure

```text
businessbuddy/
├── architecture.md
├── requirement.txt
├── backend/
│   ├── generate_clean_demo_ppt.py
│   ├── generate_presentation.py
│   ├── app/
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── schemas/
│   │   │   └── intelligence.py
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── email.py
│   │       ├── embeddings.py
│   │       ├── indexer.py
│   │       ├── intelligence.py
│   │       ├── rag.py
│   │       ├── retrieval.py
│   │       ├── transcription.py
│   │       └── vector_store.py
│   ├── data/
│   │   ├── faiss/
│   │   │   ├── meetings.index
│   │   │   └── metadata.json
│   │   ├── outputs/
│   │   ├── recordings/
│   │   └── transcripts/
│   └── tests/
│       ├── test_database.py
│       ├── test_intelligence.py
│       ├── test_pipeline.py
│       ├── test_rag.py
│       ├── test_schema.py
│       ├── test_search.py
│       ├── test_tasks_calendar_email.py
│       └── fixtures/
│           ├── ambiguous_meeting.txt
│           ├── engineering_sync.txt
│           ├── launch_planning.txt
│           └── product_planning.txt
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── eslint.config.js
│   ├── README.md
│   └── src/
│       ├── App.css
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── assets/
│       ├── components/
│       │   ├── common/
│       │   ├── intelligence/
│       │   │   └── askpanel.jsx
│       │   ├── layout/
│       │   │   └── sidebar.jsx
│       │   └── meetings/
│       ├── context/
│       │   └── AuthContext.jsx
│       ├── hooks/
│       ├── pages/
│       │   ├── Assistant.jsx
│       │   ├── Calendar.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Decisions.jsx
│       │   ├── Login.jsx
│       │   ├── MeetingIntelligence.jsx
│       │   ├── Meetings.jsx
│       │   ├── Review.jsx
│       │   ├── Search.jsx
│       │   ├── Tasks.jsx
│       │   └── ...
│       └── services/
│           └── api.js
└── temp/
```

---

## 4. Core Technologies and Libraries

### 4.1 Backend Runtime

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-multipart for file uploads
- python-dotenv for environment loading

### 4.2 AI / ML Stack

- faster-whisper for speech-to-text transcription
- Groq Python SDK for LLM calls
- openai/gpt-oss-20b as the model used in the system
- SentenceTransformers for text embeddings
- FAISS for vector indexing and retrieval

### 4.3 Persistence

- SQLite with WAL mode enabled
- FAISS index and metadata files on disk

### 4.4 Frontend

- React 19
- Vite
- React Router DOM
- Tailwind CSS via @tailwindcss/vite
- ESLint and React refresh plugin

### 4.5 Networking / Integration

- CORS configured for local frontend access
- SMTP support via Python standard library for email notifications

---

## 5. Dependency Summary

The project currently declares these core requirements in [requirement.txt](requirement.txt):

- faster-whisper
- groq
- python-dotenv
- pydantic
- fastapi
- uvicorn
- python-multipart

The frontend package declares the web app dependencies in [frontend/package.json](frontend/package.json):

- react
- react-dom
- react-router-dom
- tailwindcss
- vite
- eslint
- @vitejs/plugin-react

---

## 6. Runtime Flow

### 6.1 Authentication flow

The backend exposes login and token validation endpoints:

- POST /auth/login
- GET /auth/me
- GET /users

The app uses a bearer token pattern:

- User logs in with username and password
- Backend validates credentials against SQLite users table
- A token is generated in the form token_<username>_<role>
- Frontend stores token in localStorage
- All protected endpoints require the Authorization header

The authorization middleware enforces role-based access:

- get_current_user(): validates bearer token
- require_lead(): allows only team lead role

---

### 6.2 Meeting upload and analysis pipeline

The main pipeline is triggered through:

- POST /meetings/analyze

This endpoint:

1. Accepts an uploaded audio file using UploadFile
2. Saves it to backend/data/recordings
3. Calls transcribe_audio(str(file_path))
4. Calls extract_intelligence(segments)
5. Saves the transcript + extracted intelligence to SQLite
6. Rebuilds the FAISS semantic index
7. Returns the meeting_id, transcript, and intelligence payload

This is the primary ingestion pipeline of the system.

---

### 6.3 Transcription stage

In [backend/app/services/transcription.py](backend/app/services/transcription.py):

- the app initializes a local WhisperModel with:
  - model = "small"
  - device = "cpu"
  - compute_type = "int8"
- the model transcribes the uploaded audio
- output segments are normalized into a list of dictionaries containing:
  - start
  - end
  - text

This keeps transcription local and avoids requiring a separate transcription service.

---

### 6.4 Intelligence extraction stage

In [backend/app/services/intelligence.py](backend/app/services/intelligence.py):

- the transcript is converted into a timestamped text block
- a prompt is sent to Groq using the model openai/gpt-oss-20b
- response_format is set to JSON object
- the result is validated against the Pydantic schema in [backend/app/schemas/intelligence.py](backend/app/schemas/intelligence.py)

The system extracts structured meeting intelligence for:

- summary
- action_items
- meeting_requests
- decisions
- open_questions
- risks

These are designed to align with business decision support workflows.

---

### 6.5 Vector search and retrieval stage

The system creates semantic search capability with a dual-step process:

1. Transcript chunks are indexed with embeddings
2. User questions run against that index through retrieval and optional RAG

Files involved:

- [backend/app/services/embeddings.py](backend/app/services/embeddings.py)
- [backend/app/services/vector_store.py](backend/app/services/vector_store.py)
- [backend/app/services/indexer.py](backend/app/services/indexer.py)
- [backend/app/services/retrieval.py](backend/app/services/retrieval.py)
- [backend/app/services/rag.py](backend/app/services/rag.py)

The FAISS store uses an inner-product flat index and stores metadata for each chunk:

- meeting_id
- segment_ids
- start_time
- end_time
- text

The index is persisted in:

- data/faiss/meetings.index
- data/faiss/metadata.json

The app rebuilds this index whenever meetings are added or removed.

---

### 6.6 RAG / question answering

The RAG endpoint:

- GET /ask

calls answer_question(question, top_k). It does the following:

1. Performs semantic retrieval against the FAISS index
2. Builds a context block from the retrieved transcript fragments
3. Sends the question + transcript evidence to Groq
4. Returns:
   - answer
   - sources

This makes the system capable of grounded question answering based on real meeting evidence rather than free-form model memory.

---

## 7. SQLite Database Architecture

The database is initialized in [backend/app/database.py](backend/app/database.py). The primary file is:

- backend/data/meeting_intelligence.db

The database includes these tables:

### 7.1 Core meeting tables

- meetings
  - id
  - filename
  - summary
  - created_at

- transcript_segments
  - id
  - meeting_id
  - start_time
  - end_time
  - text

### 7.2 Action and workflow tables

- action_items
  - id
  - meeting_id
  - task
  - owner
  - owner_email
  - due_date
  - confidence
  - source_timestamp
  - status
  - type
  - human_modified
  - updated_at
  - email_sent
  - completed
  - completed_at

- action_item_history
  - id
  - action_item_id
  - field_name
  - old_value
  - new_value
  - changed_at

### 7.3 Intelligence tables

- meeting_requests
- decisions
- open_questions
- risks

### 7.4 Calendar and users

- calendar_events
- users

### 7.5 Operational behavior

The database uses:

- WAL mode for better concurrency
- busy_timeout for retries under contention
- foreign_keys enforcement
- schema migration logic via migrate_database()

This allows the app to evolve while preserving existing records.

---

## 8. Data Model and Business Semantics

### 8.1 Meeting intelligence schema

The Pydantic schema in [backend/app/schemas/intelligence.py](backend/app/schemas/intelligence.py) defines the expected JSON structure:

- summary: list[str]
- action_items: list[ActionItem]
- meeting_requests: list[MeetingRequest]
- decisions: list[Decision]
- open_questions: list[OpenQuestion]
- risks: list[Risk]

Each extracted item includes a confidence score and source timestamp.

### 8.2 Action item lifecycle

Action items flow through statuses such as:

- pending_review
- confirmed
- dismissed
- completed

The backend supports operations to:

- create action item
- read action item
- confirm action item
- dismiss action item
- reopen action item
- update action item
- complete an action item

The system also tracks human edits in action_item_history.

### 8.3 Meeting request lifecycle

Meeting requests are AI-derived suggestions for scheduling or next meetings. They may be:

- pending_review
- confirmed
- dismissed

When confirmed, a calendar event is created from the request.

### 8.4 Decision and risk handling

The app stores:

- decisions that were reached in the meeting
- open questions still unresolved
- risks that represent blockers or concerns

These objects are treated as reviewable artifacts, not just raw transcript snippets.

---

## 9. Backend API Surface

The backend exposes a broad set of endpoints in [backend/app/main.py](backend/app/main.py).

### 9.1 Authentication

- GET /health
- GET /
- POST /auth/login
- GET /auth/me
- GET /users

### 9.2 Meeting ingestion and retrieval

- POST /meetings/analyze
- GET /meetings
- GET /meetings/{meeting_id}
- PATCH /meetings/{meeting_id}
- DELETE /meetings/{meeting_id}

### 9.3 Action items

- POST /action-items
- GET /action-items/{action_item_id}
- PATCH /action-items/{action_item_id}/confirm
- PATCH /action-items/{action_item_id}/dismiss
- PATCH /action-items/{action_item_id}/reopen
- PATCH /action-items/{action_item_id}
- PATCH /action-items/{action_item_id}/complete

### 9.4 Dashboard and review

- GET /dashboard/stats
- GET /tasks
- GET /review
- GET /decisions
- PATCH /decisions/{decision_id}

### 9.5 Calendar and scheduling

- GET /calendar
- POST /calendar/events
- PATCH /calendar/events/{event_id}
- DELETE /calendar/events/{event_id}
- PATCH /meeting-requests/{request_id}
- PATCH /meeting-requests/{request_id}/confirm
- PATCH /meeting-requests/{request_id}/dismiss

### 9.6 Search and AI assistant

- GET /search
- GET /ask

These are the primary endpoints used by the frontend UI.

---

## 10. Frontend Architecture

The React application is built with Vite and uses client-side routing.

### 10.1 App-level routing

The root app in [frontend/src/App.jsx](frontend/src/App.jsx) configures:

- /login
- /
- /assistant
- /meetings
- /meetings/:meetingId
- /review
- /decisions
- /tasks
- /calendar
- /search

The application wraps routes inside an AuthProvider and protects routes behind authentication.

### 10.2 Auth context

[frontend/src/context/AuthContext.jsx](frontend/src/context/AuthContext.jsx) handles:

- reading saved user and token from localStorage
- login call to backend
- logout
- role detection for lead vs member

### 10.3 Shared API layer

The frontend uses [frontend/src/services/api.js](frontend/src/services/api.js) as a single abstraction for API communication.

This service:

- builds the API base URL from VITE_API_BASE_URL or default localhost:8000
- attaches Authentication bearer token when present
- handles JSON parsing and error extraction
- centralizes HTTP request logic across the app

### 10.4 Page structure

The frontend pages include:

- Login
- Dashboard
- Assistant
- Meetings
- MeetingIntelligence
- Review
- Decisions
- Tasks
- Calendar
- Search

These pages operate on the backend data model and use the API service for meeting analysis, review workflows, and AI assistance.

---

## 11. Search and Retrieval Design

The system uses a hybrid pattern:

- SQLite holds structured records and metadata
- FAISS holds transcript evidence fragments for semantic matching

### 11.1 Indexing design

The indexer groups transcript segments into semantic chunks with a max chunk size of 250 characters. It ensures that:

- adjacent transcript segments are combined
- meeting boundaries are respected
- metadata is preserved for source traceability

### 11.2 Retrieval design

When a query is executed:

- query text is embedded using SentenceTransformers
- FAISS performs nearest-neighbor search
- results include similarity score and matching metadata
- the backend returns source segments and their timestamps

This is used both for the semantic search endpoint and for GPT-backed answer generation.

---

## 12. Email Notification Design

The email service in [backend/app/services/email.py](backend/app/services/email.py) provides a simple SMTP workflow.

It sends an action-item notification when:

- a lead confirms an action item
- the item has an owner and owner_email
- SMTP is configured correctly

The service validates:

- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SMTP_FROM

It fails gracefully without preventing the confirmation action itself from succeeding.

---

## 13. Security and Access Control

The system currently uses a lightweight security pattern:

- username/password login against SQLite users table
- bearer token validation for protected routes
- role-based access checks for lead-only routes

Important notes:

- secrets are expected via environment variables
- .env loading is done with python-dotenv
- CORS is restricted to localhost frontend origins
- no OAuth or JWT signing library is used in the present implementation

---

## 14. Configuration and Environment

This project expects environment-based configuration for AI and email services, especially:

- GROQ_API_KEY
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- SMTP_FROM

The backend loads configuration from environment variables using python-dotenv.

---

## 15. Persistence Strategy

The system intentionally separates two classes of data:

### 15.1 SQLite: operational truth

SQLite is the mutable source of system state:

- meetings
- action items
- meeting requests
- decisions
- risks
- users
- calendar events

This is the system of record for operational workflow changes.

### 15.2 FAISS: transcript evidence store

FAISS collects transcript-derived evidence chunks. This is treated as immutable evidence and is rebuilt from the transcript segments when content changes.

This design allows:

- preserving original spoken content
- enabling semantic search over meeting history
- keeping operational edits separate from evidence

---

## 16. Key Architectural Principles in This Project

1. Monolithic but modular
   - a single FastAPI app manages routes, data access, AI orchestration, and workflows

2. Local-first processing
   - transcription runs locally with faster-whisper
   - FAISS index remains local on disk

3. Evidence-based AI
   - LLM answers are grounded in transcript snippets from the FAISS index

4. Structured extraction
   - model output is validated using strict Pydantic schemas

5. Human review workflow
   - AI-generated outputs are reviewable and editable before confirmation

6. Operational transparency
   - history tables track action item changes
   - status fields represent workflow progression

---

## 17. Typical End-to-End Workflow

A full user journey often looks like this:

1. A lead uploads a meeting recording via the frontend
2. The backend saves the file and transcribes audio locally
3. A Groq model extracts structured meeting intelligence
4. Results are stored in SQLite
5. Transcript chunks are embedded and indexed in FAISS
6. The frontend displays the meeting summary and extracted items
7. The user confirms or edits action items and decisions
8. Confirmed tasks can trigger email alerts
9. Search and Ask features retrieve transcript evidence through semantic retrieval and grounded LLM responses

---

## 18. Current Implementation Notes

This project is not a distributed microservice architecture. It is a single application with a clear separation of responsibilities, optimized for a local development / team productivity environment.

It is best understood as:

- a meeting intelligence workstation
- a local AI workflow engine
- a lightweight business operations dashboard

---

## 19. Notable Files to Review

For code-level understanding, the most relevant files are:

- [backend/app/main.py](backend/app/main.py): API surface and orchestration
- [backend/app/database.py](backend/app/database.py): SQLite schema and migration logic
- [backend/app/services/transcription.py](backend/app/services/transcription.py): transcription pipeline
- [backend/app/services/intelligence.py](backend/app/services/intelligence.py): Groq extraction pipeline
- [backend/app/services/vector_store.py](backend/app/services/vector_store.py): FAISS index implementation
- [backend/app/services/indexer.py](backend/app/services/indexer.py): transcript chunking and indexing
- [backend/app/services/rag.py](backend/app/services/rag.py): answer generation from evidence
- [backend/app/schemas/intelligence.py](backend/app/schemas/intelligence.py): structured intelligence schema
- [frontend/src/App.jsx](frontend/src/App.jsx): frontend routing and app shell
- [frontend/src/services/api.js](frontend/src/services/api.js): API client abstraction

---

## 20. Summary

BusinessBuddy is a local-first AI meeting intelligence application built around FastAPI, SQLite, FAISS, Groq, and React. It ingests audio, transcribes it locally, extracts structured business intelligence, stores operational workflow state, and enables semantic search and grounded Q&A over historical meeting evidence.

The architecture is intentionally simple, practical, and well suited to a team or single deployment environment where AI-enhanced coordination and traceable meeting records matter more than heavy distributed infrastructure.
