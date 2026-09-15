import json
from pathlib import Path

from fastapi import Depends, FastAPI, File, Header, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.services.indexer import rebuild_index
from app.services.retrieval import search_meetings
from app.services.rag import answer_question
from app.services.transcription import transcribe_audio
from app.services.intelligence import extract_intelligence
from app.services.email import send_action_item_email

from pydantic import BaseModel

from app.database import (
    initialize_database,
    migrate_database,
    get_connection,
    save_meeting,
    record_action_item_history,
    get_user_by_username,
    get_all_team_members,
    toggle_action_item_completion,
)


class LoginRequest(BaseModel):
    username: str
    password: str


class CompleteTaskRequest(BaseModel):
    completed: bool = True



# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="AI Meeting Intelligence Companion",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATABASE
# ============================================================

initialize_database()
migrate_database()


# ============================================================
# FILE STORAGE
# ============================================================

RECORDINGS_DIR = Path("data/recordings")
RECORDINGS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# BASIC
# ============================================================

@app.get("/")
def root():
    return {
        "message": "AI Meeting Intelligence Companion API",
        "status": "running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


# ============================================================
# AUTHENTICATION & TEAM
# ============================================================

@app.post("/auth/login")
def login(request: LoginRequest):
    user = get_user_by_username(request.username)

    if not user or user["password"] != request.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
        )

    return {
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"],
            "email": user["email"],
        },
        "token": f"token_{user['username']}_{user['role']}",
    }


def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = authorization[7:].strip()
    parts = token.split("_")
    if len(parts) >= 2:
        user = get_user_by_username(parts[1])
        if user and token == f"token_{user['username']}_{user['role']}":
            return {
                "id": user["id"],
                "username": user["username"],
                "name": user["name"],
                "role": user["role"],
                "email": user["email"],
            }

    raise HTTPException(status_code=401, detail="Invalid session token")


def require_lead(user: dict = Depends(get_current_user)):
    if user["role"] != "lead":
        raise HTTPException(status_code=403, detail="Team Lead access required")
    return user


@app.get("/auth/me")
def get_me(user: dict = Depends(get_current_user)):
    return user


@app.get("/users")
def get_users():
    return get_all_team_members()



# ============================================================
# ANALYZE MEETING
# ============================================================

@app.post("/meetings/analyze")
async def analyze_meeting(
    file: UploadFile = File(...),
    _user: dict = Depends(require_lead),
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided",
        )

    file_path = RECORDINGS_DIR / file.filename

    contents = await file.read()
    file_path.write_bytes(contents)

    # --------------------------------------------------------
    # Transcription
    # --------------------------------------------------------

    segments = transcribe_audio(
        str(file_path)
    )

    if not segments:
        raise HTTPException(
            status_code=400,
            detail="No speech detected in audio",
        )

    # --------------------------------------------------------
    # Intelligence extraction
    # --------------------------------------------------------

    intelligence = extract_intelligence(
        segments
    )

    # --------------------------------------------------------
    # Save meeting
    # --------------------------------------------------------

    meeting_id = save_meeting(
        filename=file.filename,
        segments=segments,
        intelligence=intelligence,
    )

    # --------------------------------------------------------
    # Rebuild semantic search index
    # --------------------------------------------------------

    rebuild_index()

    return {
        "meeting_id": meeting_id,
        "filename": file.filename,
        "transcript": segments,
        "intelligence": intelligence.model_dump(),
    }


# ============================================================
# ACTION ITEMS
# ============================================================

@app.get("/action-items/{action_item_id}")
def get_action_item(
    action_item_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    item = cursor.execute(
        """
        SELECT
            id,
            meeting_id,
            task,
            owner,
            owner_email,
            due_date,
            confidence,
            source_timestamp,
            status,
            type,
            human_modified,
            updated_at,
            email_sent,
            completed,
            completed_at
        FROM action_items
        WHERE id = ?
        """,
        (action_item_id,),
    ).fetchone()

    connection.close()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    return dict(item)


# ============================================================
# CONFIRM ACTION ITEM
# ============================================================

@app.patch("/action-items/{action_item_id}/confirm")
def confirm_action_item(
    action_item_id: int,
    _user: dict = Depends(require_lead),
):
    connection = get_connection()
    cursor = connection.cursor()

    item = cursor.execute(
        """
        SELECT
            action_items.id,
            action_items.task,
            action_items.owner,
            action_items.owner_email,
            action_items.due_date,
            action_items.email_sent,
            meetings.filename
        FROM action_items
        JOIN meetings
            ON action_items.meeting_id = meetings.id
        WHERE action_items.id = ?
        """,
        (action_item_id,),
    ).fetchone()

    if item is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    # --------------------------------------------------------
    # Confirm first.
    #
    # Email failure must never undo confirmation.
    # --------------------------------------------------------

    cursor.execute(
        """
        UPDATE action_items
        SET
            status = 'confirmed',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (action_item_id,),
    )

    connection.commit()

    email_sent = bool(
        item["email_sent"]
    )

    owner_name = (
        item["owner"].strip()
        if item["owner"]
        else None
    )

    owner_email = (
        item["owner_email"].strip()
        if item["owner_email"]
        else None
    )

    # --------------------------------------------------------
    # Send notification if configured.
    # --------------------------------------------------------

    if (
        not email_sent
        and owner_name
        and owner_email
    ):
        sent_success = send_action_item_email(
            task=item["task"],
            owner_name=owner_name,
            owner_email=owner_email,
            due_date=item["due_date"],
            meeting_name=item["filename"],
        )

        if sent_success:
            cursor.execute(
                """
                UPDATE action_items
                SET email_sent = 1
                WHERE id = ?
                """,
                (action_item_id,),
            )

            connection.commit()

            email_sent = True

    connection.close()

    return {
        "id": action_item_id,
        "status": "confirmed",
        "email_sent": email_sent,
    }


# ============================================================
# DISMISS ACTION ITEM
# ============================================================

@app.patch("/action-items/{action_item_id}/dismiss")
def dismiss_action_item(
    action_item_id: int,
    _user: dict = Depends(require_lead),
):
    connection = get_connection()
    cursor = connection.cursor()

    action_item = cursor.execute(
        """
        SELECT id
        FROM action_items
        WHERE id = ?
        """,
        (action_item_id,),
    ).fetchone()

    if action_item is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    cursor.execute(
        """
        UPDATE action_items
        SET
            status = 'dismissed',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (action_item_id,),
    )

    connection.commit()
    connection.close()

    return {
        "id": action_item_id,
        "status": "dismissed",
    }


# ============================================================
# REOPEN ACTION ITEM
# ============================================================

@app.patch("/action-items/{action_item_id}/reopen")
def reopen_action_item(
    action_item_id: int,
    _user: dict = Depends(require_lead),
):
    connection = get_connection()
    cursor = connection.cursor()

    action_item = cursor.execute(
        """
        SELECT id
        FROM action_items
        WHERE id = ?
        """,
        (action_item_id,),
    ).fetchone()

    if action_item is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    cursor.execute(
        """
        UPDATE action_items
        SET
            status = 'pending_review',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (action_item_id,),
    )

    connection.commit()
    connection.close()

    return {
        "id": action_item_id,
        "status": "pending_review",
    }


# ============================================================
# UPDATE ACTION ITEM
# ============================================================

@app.patch("/action-items/{action_item_id}")
def update_action_item(
    action_item_id: int,
    data: dict,
    _user: dict = Depends(require_lead),
):
    connection = get_connection()
    cursor = connection.cursor()

    action_item = cursor.execute(
        """
        SELECT
            id,
            task,
            owner,
            owner_email,
            due_date,
            type
        FROM action_items
        WHERE id = ?
        """,
        (action_item_id,),
    ).fetchone()

    if action_item is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    allowed_fields = {
        "task",
        "owner",
        "owner_email",
        "due_date",
        "type",
    }

    # --------------------------------------------------------
    # Validate email
    # --------------------------------------------------------

    if "owner_email" in data:
        owner_email = data["owner_email"]

        if owner_email is not None:
            owner_email = str(
                owner_email
            ).strip()

            if owner_email:
                if (
                    "@" not in owner_email
                    or "." not in owner_email.split("@")[-1]
                ):
                    connection.close()

                    raise HTTPException(
                        status_code=400,
                        detail="Invalid owner email address",
                    )

                data["owner_email"] = owner_email

            else:
                data["owner_email"] = None

    updates = []
    values = []
    history_records = []

    # --------------------------------------------------------
    # Build update
    # --------------------------------------------------------

    for field in allowed_fields:
        if field not in data:
            continue

        old_val = action_item[field]
        new_val = data[field]

        old_string = (
            str(old_val)
            if old_val is not None
            else ""
        )

        new_string = (
            str(new_val)
            if new_val is not None
            else ""
        )

        if old_string != new_string:
            history_records.append(
                (
                    field,
                    old_val,
                    new_val,
                )
            )

        updates.append(
            f"{field} = ?"
        )

        values.append(new_val)

    if not updates:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="No valid fields provided",
        )

    has_actual_changes = bool(
        history_records
    )

    values.append(action_item_id)

    if has_actual_changes:
        cursor.execute(
            f"""
            UPDATE action_items
            SET
                {", ".join(updates)},
                human_modified = 1,
                updated_at = CURRENT_TIMESTAMP,
                status = 'pending_review',
                email_sent = 0
            WHERE id = ?
            """,
            values,
        )

    else:
        cursor.execute(
            f"""
            UPDATE action_items
            SET
                {", ".join(updates)},
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            values,
        )

    # --------------------------------------------------------
    # Record human modifications
    # --------------------------------------------------------

    for (
        field,
        old_val,
        new_val,
    ) in history_records:
        record_action_item_history(
            cursor,
            action_item_id,
            field,
            old_val,
            new_val,
        )

    connection.commit()
    connection.close()

    return {
        "id": action_item_id,
        "status": (
            "pending_review"
            if has_actual_changes
            else "unchanged"
        ),
    }


# ============================================================
# COMPLETE ACTION ITEM (MEMBER OR LEAD)
# ============================================================

@app.patch("/action-items/{action_item_id}/complete")
def complete_action_item(
    action_item_id: int,
    payload: CompleteTaskRequest | None = None,
    _user: dict = Depends(get_current_user),
):
    completed = True if payload is None else payload.completed
    updated = toggle_action_item_completion(action_item_id, 1 if completed else 0)

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    return updated


# ============================================================
# MEETINGS
# ============================================================

@app.get("/meetings")
def get_meetings():
    connection = get_connection()
    cursor = connection.cursor()

    meetings = cursor.execute(
        """
        SELECT
            id,
            filename,
            summary,
            created_at
        FROM meetings
        ORDER BY created_at DESC
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": meeting["id"],
            "filename": meeting["filename"],
            "summary": (
                json.loads(meeting["summary"])
                if meeting["summary"]
                else []
            ),
            "created_at": meeting["created_at"],
        }
        for meeting in meetings
    ]


# ============================================================
# GET SINGLE MEETING
# ============================================================

@app.get("/meetings/{meeting_id}")
def get_meeting(
    meeting_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    meeting = cursor.execute(
        """
        SELECT
            id,
            filename,
            summary,
            created_at
        FROM meetings
        WHERE id = ?
        """,
        (meeting_id,),
    ).fetchone()

    if meeting is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    # --------------------------------------------------------
    # Transcript
    # --------------------------------------------------------

    transcript = cursor.execute(
        """
        SELECT
            id,
            start_time,
            end_time,
            text
        FROM transcript_segments
        WHERE meeting_id = ?
        ORDER BY start_time
        """,
        (meeting_id,),
    ).fetchall()

    # --------------------------------------------------------
    # Action Items
    # --------------------------------------------------------

    action_items = cursor.execute(
        """
        SELECT
            id,
            task,
            owner,
            owner_email,
            due_date,
            confidence,
            source_timestamp,
            status,
            type,
            human_modified,
            updated_at,
            email_sent,
            completed,
            completed_at
        FROM action_items
        WHERE meeting_id = ?
        ORDER BY id
        """,
        (meeting_id,),
    ).fetchall()

    # --------------------------------------------------------
    # Meeting Requests
    # --------------------------------------------------------

    meeting_requests = cursor.execute(
        """
        SELECT
            id,
            topic,
            suggested_date,
            suggested_time,
            confidence,
            source_timestamp,
            status,
            updated_at
        FROM meeting_requests
        WHERE meeting_id = ?
        ORDER BY id
        """,
        (meeting_id,),
    ).fetchall()

    # --------------------------------------------------------
    # Decisions
    # --------------------------------------------------------

    decisions = cursor.execute(
        """
        SELECT
            id,
            decision,
            confidence,
            source_timestamp,
            status
        FROM decisions
        WHERE meeting_id = ?
        ORDER BY id
        """,
        (meeting_id,),
    ).fetchall()

    # --------------------------------------------------------
    # Open Questions
    # --------------------------------------------------------

    open_questions = cursor.execute(
        """
        SELECT
            id,
            question,
            confidence,
            source_timestamp,
            status
        FROM open_questions
        WHERE meeting_id = ?
        ORDER BY id
        """,
        (meeting_id,),
    ).fetchall()

    # --------------------------------------------------------
    # Risks
    # --------------------------------------------------------

    risks = cursor.execute(
        """
        SELECT
            id,
            risk,
            confidence,
            source_timestamp,
            status
        FROM risks
        WHERE meeting_id = ?
        ORDER BY id
        """,
        (meeting_id,),
    ).fetchall()

    connection.close()

    return {
        "id": meeting["id"],
        "filename": meeting["filename"],
        "summary": (
            json.loads(meeting["summary"])
            if meeting["summary"]
            else []
        ),
        "created_at": meeting["created_at"],

        "transcript": [
            dict(segment)
            for segment in transcript
        ],

        "action_items": [
            dict(item)
            for item in action_items
        ],

        "meeting_requests": [
            dict(request)
            for request in meeting_requests
        ],

        "decisions": [
            dict(decision)
            for decision in decisions
        ],

        "open_questions": [
            dict(question)
            for question in open_questions
        ],

        "risks": [
            dict(risk)
            for risk in risks
        ],
    }


# ============================================================
# UPDATE MEETING
# ============================================================

@app.patch("/meetings/{meeting_id}")
def update_meeting(
    meeting_id: int,
    data: dict,
    _user: dict = Depends(require_lead),
):
    connection = get_connection()
    cursor = connection.cursor()

    meeting = cursor.execute(
        """
        SELECT id
        FROM meetings
        WHERE id = ?
        """,
        (meeting_id,),
    ).fetchone()

    if meeting is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    updates = []
    values = []

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    if "filename" in data:
        filename = str(
            data["filename"]
        ).strip()

        if not filename:
            connection.close()

            raise HTTPException(
                status_code=400,
                detail="Filename cannot be empty",
            )

        updates.append(
            "filename = ?"
        )

        values.append(filename)

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    if "summary" in data:
        if not isinstance(
            data["summary"],
            list,
        ):
            connection.close()

            raise HTTPException(
                status_code=400,
                detail="Summary must be a list",
            )

        cleaned_summary = [
            str(point).strip()
            for point in data["summary"]
            if str(point).strip()
        ]

        updates.append(
            "summary = ?"
        )

        values.append(
            json.dumps(cleaned_summary)
        )

    if not updates:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="No valid fields provided",
        )

    values.append(meeting_id)

    cursor.execute(
        f"""
        UPDATE meetings
        SET {", ".join(updates)}
        WHERE id = ?
        """,
        values,
    )

    connection.commit()
    connection.close()

    return {
        "id": meeting_id,
        "status": "updated",
    }


# ============================================================
# DASHBOARD STATS
# ============================================================

@app.get("/dashboard/stats")
def get_dashboard_stats():
    connection = get_connection()
    cursor = connection.cursor()

    meetings = cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM meetings
        """
    ).fetchone()["count"]

    pending_review = cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM action_items
        WHERE status = 'pending_review'
        """
    ).fetchone()["count"]

    decisions = cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM decisions
        """
    ).fetchone()["count"]

    confirmed_tasks = cursor.execute(
        """
        SELECT COUNT(*) AS count
        FROM action_items
        WHERE status = 'confirmed'
        """
    ).fetchone()["count"]

    connection.close()

    return {
        "meetings": meetings,
        "pending_review": pending_review,
        "decisions": decisions,
        "confirmed_tasks": confirmed_tasks,
    }


# ============================================================
# TASKS
# ============================================================

@app.get("/tasks")
def get_tasks(
    status: str | None = None,
    owner: str | None = None,
):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            action_items.id,
            action_items.meeting_id,
            action_items.task,
            action_items.owner,
            action_items.owner_email,
            action_items.due_date,
            action_items.confidence,
            action_items.source_timestamp,
            action_items.status,
            action_items.type,
            action_items.human_modified,
            action_items.updated_at,
            action_items.email_sent,
            action_items.completed,
            action_items.completed_at,
            meetings.filename
        FROM action_items
        JOIN meetings
            ON action_items.meeting_id = meetings.id
    """

    where_clauses = []
    params = []

    if status:
        where_clauses.append("action_items.status = ?")
        params.append(status)
    else:
        where_clauses.append("action_items.status IN ('confirmed', 'dismissed')")

    if owner:
        where_clauses.append("LOWER(TRIM(COALESCE(action_items.owner, ''))) = LOWER(TRIM(?))")
        params.append(owner)

    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)

    query += """
        ORDER BY
            COALESCE(
                action_items.updated_at,
                ''
            ) DESC,
            action_items.id DESC
    """

    items = cursor.execute(
        query,
        params,
    ).fetchall()

    connection.close()

    return [
        {
            "id": item["id"],
            "meeting_id": item["meeting_id"],
            "task": item["task"],
            "owner": item["owner"],
            "owner_email": item["owner_email"],
            "due_date": item["due_date"],
            "confidence": item["confidence"],
            "source_timestamp": item["source_timestamp"],
            "status": item["status"],
            "type": item["type"],
            "human_modified": item["human_modified"],
            "updated_at": item["updated_at"],
            "email_sent": bool(
                item["email_sent"]
            ),
            "completed": bool(
                item["completed"]
            ),
            "completed_at": item["completed_at"],
            "filename": item["filename"],
        }
        for item in items
    ]


# ============================================================
# CALENDAR
# ============================================================

@app.get("/calendar")
def get_calendar():
    connection = get_connection()
    cursor = connection.cursor()

    # --------------------------------------------------------
    # AI meeting requests
    # --------------------------------------------------------

    requests = cursor.execute(
        """
        SELECT
            meeting_requests.id,
            meeting_requests.meeting_id,
            meeting_requests.topic,
            meeting_requests.suggested_date,
            meeting_requests.suggested_time,
            meeting_requests.confidence,
            meeting_requests.source_timestamp,
            meeting_requests.status,
            meeting_requests.updated_at,
            meetings.filename
        FROM meeting_requests
        JOIN meetings
            ON meeting_requests.meeting_id = meetings.id
        ORDER BY meeting_requests.id DESC
        """
    ).fetchall()

    # --------------------------------------------------------
    # Manual calendar events
    # --------------------------------------------------------

    events = cursor.execute(
        """
        SELECT
            id,
            title,
            event_date,
            event_time,
            notes,
            status,
            source,
            meeting_id,
            created_at,
            updated_at
        FROM calendar_events
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    result = []

    # --------------------------------------------------------
    # AI requests
    # --------------------------------------------------------

    for request in requests:
        result.append(
            {
                "id": request["id"],
                "meeting_id": request["meeting_id"],
                "topic": request["topic"],
                "suggested_date": request["suggested_date"],
                "suggested_time": request["suggested_time"],
                "confidence": request["confidence"],
                "source_timestamp": request["source_timestamp"],
                "status": request["status"],
                "updated_at": request["updated_at"],
                "filename": request["filename"],
                "source": "ai",
                "type": "meeting_request",
            }
        )

    # --------------------------------------------------------
    # Manual events
    # --------------------------------------------------------

    for event in events:
        result.append(
            {
                "id": event["id"],
                "title": event["title"],
                "event_date": event["event_date"],
                "event_time": event["event_time"],
                "notes": event["notes"],
                "status": event["status"],
                "source": event["source"],
                "meeting_id": event["meeting_id"],
                "created_at": event["created_at"],
                "updated_at": event["updated_at"],
                "type": "calendar_event",
            }
        )

    return result


# ============================================================
# CREATE MANUAL CALENDAR EVENT
# ============================================================

@app.post("/calendar/events")
def create_calendar_event(
    data: dict
):
    title = str(
        data.get("title", "")
    ).strip()

    event_date = str(
        data.get("event_date", "")
    ).strip()

    event_time = data.get(
        "event_time"
    )

    notes = data.get(
        "notes"
    )

    if not title:
        raise HTTPException(
            status_code=400,
            detail="Event title is required",
        )

    if not event_date:
        raise HTTPException(
            status_code=400,
            detail="Event date is required",
        )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO calendar_events (
            title,
            event_date,
            event_time,
            notes,
            status,
            source
        )
        VALUES (?, ?, ?, ?, 'confirmed', 'manual')
        """,
        (
            title,
            event_date,
            event_time,
            notes,
        ),
    )

    event_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return {
        "id": event_id,
        "status": "created",
    }


# ============================================================
# UPDATE MANUAL CALENDAR EVENT
# ============================================================

@app.patch("/calendar/events/{event_id}")
def update_calendar_event(
    event_id: int,
    data: dict,
):
    connection = get_connection()
    cursor = connection.cursor()

    event = cursor.execute(
        """
        SELECT id
        FROM calendar_events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()

    if event is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Calendar event not found",
        )

    allowed_fields = {
        "title",
        "event_date",
        "event_time",
        "notes",
    }

    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(
                f"{field} = ?"
            )
            values.append(
                data[field]
            )

    if not updates:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="No valid fields provided",
        )

    values.append(event_id)

    cursor.execute(
        f"""
        UPDATE calendar_events
        SET
            {", ".join(updates)},
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        values,
    )

    connection.commit()
    connection.close()

    return {
        "id": event_id,
        "status": "updated",
    }


# ============================================================
# DELETE MANUAL CALENDAR EVENT
# ============================================================

@app.delete("/calendar/events/{event_id}")
def delete_calendar_event(
    event_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    event = cursor.execute(
        """
        SELECT id
        FROM calendar_events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()

    if event is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Calendar event not found",
        )

    cursor.execute(
        """
        DELETE FROM calendar_events
        WHERE id = ?
        """,
        (event_id,),
    )

    connection.commit()
    connection.close()

    return {
        "id": event_id,
        "status": "deleted",
    }


# ============================================================
# MEETING REQUESTS
# ============================================================

@app.patch("/meeting-requests/{request_id}")
def update_meeting_request(
    request_id: int,
    data: dict,
):
    connection = get_connection()
    cursor = connection.cursor()

    req = cursor.execute(
        """
        SELECT id
        FROM meeting_requests
        WHERE id = ?
        """,
        (request_id,),
    ).fetchone()

    if req is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Meeting request not found",
        )

    allowed_fields = {
        "topic",
        "suggested_date",
        "suggested_time",
    }

    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(
                f"{field} = ?"
            )
            values.append(
                data[field]
            )

    if not updates:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="No valid fields provided",
        )

    values.append(request_id)

    cursor.execute(
        f"""
        UPDATE meeting_requests
        SET
            {", ".join(updates)},
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        values,
    )

    connection.commit()
    connection.close()

    return {
        "id": request_id,
        "status": "updated",
    }


# ============================================================
# CONFIRM MEETING REQUEST
# ============================================================

@app.patch("/meeting-requests/{request_id}/confirm")
def confirm_meeting_request(
    request_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    req = cursor.execute(
        """
        SELECT
            id,
            meeting_id,
            topic,
            suggested_date,
            suggested_time
        FROM meeting_requests
        WHERE id = ?
        """,
        (request_id,),
    ).fetchone()

    if req is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Meeting request not found",
        )

    cursor.execute(
        """
        UPDATE meeting_requests
        SET
            status = 'confirmed',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (request_id,),
    )

    # --------------------------------------------------------
    # Create a calendar event from the confirmed AI request.
    #
    # We preserve the AI-extracted date/time exactly as stored.
    # No date arithmetic or normalization happens here.
    # --------------------------------------------------------

    existing_event = cursor.execute(
        """
        SELECT id
        FROM calendar_events
        WHERE source = 'ai'
          AND meeting_id = ?
          AND title = ?
        LIMIT 1
        """,
        (
            req["meeting_id"],
            req["topic"],
        ),
    ).fetchone()

    if existing_event is None:
        cursor.execute(
            """
            INSERT INTO calendar_events (
                title,
                event_date,
                event_time,
                notes,
                status,
                source,
                meeting_id
            )
            VALUES (?, ?, ?, ?, 'confirmed', 'ai', ?)
            """,
            (
                req["topic"],
                req["suggested_date"],
                req["suggested_time"],
                f"Created from meeting request #{request_id}",
                req["meeting_id"],
            ),
        )

    connection.commit()
    connection.close()

    return {
        "id": request_id,
        "status": "confirmed",
    }


# ============================================================
# DISMISS MEETING REQUEST
# ============================================================

@app.patch("/meeting-requests/{request_id}/dismiss")
def dismiss_meeting_request(
    request_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    req = cursor.execute(
        """
        SELECT id
        FROM meeting_requests
        WHERE id = ?
        """,
        (request_id,),
    ).fetchone()

    if req is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Meeting request not found",
        )

    cursor.execute(
        """
        UPDATE meeting_requests
        SET
            status = 'dismissed',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (request_id,),
    )

    connection.commit()
    connection.close()

    return {
        "id": request_id,
        "status": "dismissed",
    }


# ============================================================
# REVIEW
# ============================================================

@app.get("/review")
def get_pending_review():
    connection = get_connection()
    cursor = connection.cursor()

    items = cursor.execute(
        """
        SELECT
            action_items.id,
            action_items.meeting_id,
            action_items.task,
            action_items.owner,
            action_items.owner_email,
            action_items.due_date,
            action_items.confidence,
            action_items.source_timestamp,
            action_items.status,
            action_items.type,
            action_items.email_sent,
            meetings.filename
        FROM action_items
        JOIN meetings
            ON action_items.meeting_id = meetings.id
        WHERE action_items.status = 'pending_review'
        ORDER BY
            meetings.created_at DESC,
            action_items.id DESC
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": item["id"],
            "meeting_id": item["meeting_id"],
            "task": item["task"],
            "owner": item["owner"],
            "owner_email": item["owner_email"],
            "due_date": item["due_date"],
            "confidence": item["confidence"],
            "source_timestamp": item["source_timestamp"],
            "status": item["status"],
            "type": item["type"],
            "email_sent": bool(
                item["email_sent"]
            ),
            "filename": item["filename"],
        }
        for item in items
    ]


# ============================================================
# DECISIONS
# ============================================================

@app.get("/decisions")
def get_decisions():
    connection = get_connection()
    cursor = connection.cursor()

    decisions = cursor.execute(
        """
        SELECT
            decisions.id,
            decisions.meeting_id,
            decisions.decision,
            decisions.confidence,
            decisions.source_timestamp,
            decisions.status,
            meetings.filename
        FROM decisions
        JOIN meetings
            ON decisions.meeting_id = meetings.id
        ORDER BY
            meetings.created_at DESC,
            decisions.id DESC
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": decision["id"],
            "meeting_id": decision["meeting_id"],
            "decision": decision["decision"],
            "confidence": decision["confidence"],
            "source_timestamp": decision["source_timestamp"],
            "status": decision["status"],
            "filename": decision["filename"],
        }
        for decision in decisions
    ]


# ============================================================
# UPDATE DECISION
# ============================================================

@app.patch("/decisions/{decision_id}")
def update_decision(
    decision_id: int,
    data: dict,
):
    connection = get_connection()
    cursor = connection.cursor()

    decision = cursor.execute(
        """
        SELECT id
        FROM decisions
        WHERE id = ?
        """,
        (decision_id,),
    ).fetchone()

    if decision is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Decision not found",
        )

    if "decision" not in data:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="No valid fields provided",
        )

    decision_text = str(
        data["decision"]
    ).strip()

    if not decision_text:
        connection.close()

        raise HTTPException(
            status_code=400,
            detail="Decision cannot be empty",
        )

    cursor.execute(
        """
        UPDATE decisions
        SET decision = ?
        WHERE id = ?
        """,
        (
            decision_text,
            decision_id,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "id": decision_id,
        "status": "updated",
    }


# ============================================================
# DELETE MEETING
# ============================================================

@app.delete("/meetings/{meeting_id}")
def delete_meeting(
    meeting_id: int
):
    connection = get_connection()
    cursor = connection.cursor()

    meeting = cursor.execute(
        """
        SELECT id
        FROM meetings
        WHERE id = ?
        """,
        (meeting_id,),
    ).fetchone()

    if meeting is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    # --------------------------------------------------------
    # Action item history must be deleted before action items.
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM action_item_history
        WHERE action_item_id IN (
            SELECT id
            FROM action_items
            WHERE meeting_id = ?
        )
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Transcript
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM transcript_segments
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Action items
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM action_items
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Meeting requests
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM meeting_requests
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Decisions
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM decisions
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Open questions
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM open_questions
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Risks
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM risks
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Calendar events generated from this meeting
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM calendar_events
        WHERE meeting_id = ?
        """,
        (meeting_id,),
    )

    # --------------------------------------------------------
    # Meeting
    # --------------------------------------------------------

    cursor.execute(
        """
        DELETE FROM meetings
        WHERE id = ?
        """,
        (meeting_id,),
    )

    connection.commit()
    connection.close()

    # --------------------------------------------------------
    # Rebuild semantic index after deletion.
    # --------------------------------------------------------

    rebuild_index()

    return {
        "id": meeting_id,
        "status": "deleted",
    }


# ============================================================
# SEMANTIC SEARCH
# ============================================================

@app.get("/search")
def search_meetings_endpoint(
    q: str,
    top_k: int = 5,
):
    results = search_meetings(
        query=q,
        top_k=top_k,
    )

    return {
        "query": q,
        "results": results,
    }


# ============================================================
# RAG / ASK
# ============================================================

@app.get("/ask")
def ask_question(
    q: str,
    top_k: int = 5,
):
    return answer_question(
        question=q,
        top_k=top_k,
    )