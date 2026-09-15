import json
import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/meeting_intelligence.db")


def get_connection():
    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    connection = sqlite3.connect(
        DATABASE_PATH,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA busy_timeout=30000")
    connection.execute("PRAGMA foreign_keys=ON")

    return connection

def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.executescript(
        """
        CREATE TABLE IF NOT EXISTS meetings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transcript_segments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            start_time REAL NOT NULL,
            end_time REAL NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS action_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            owner TEXT,
            owner_email TEXT,
            due_date TEXT,
            confidence REAL,
            source_timestamp TEXT,
            status TEXT,
            type TEXT,
            human_modified INTEGER DEFAULT 0,
            updated_at TIMESTAMP,
            email_sent INTEGER DEFAULT 0,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS meeting_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            topic TEXT NOT NULL,
            suggested_date TEXT,
            suggested_time TEXT,
            confidence REAL,
            source_timestamp TEXT,
            status TEXT,
            updated_at TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            decision TEXT NOT NULL,
            confidence REAL,
            source_timestamp TEXT,
            status TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS open_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            confidence REAL,
            source_timestamp TEXT,
            status TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS risks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id INTEGER NOT NULL,
            risk TEXT NOT NULL,
            confidence REAL,
            source_timestamp TEXT,
            status TEXT,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS action_item_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_item_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (action_item_id) REFERENCES action_items(id)
        );

        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT,
            notes TEXT,
            status TEXT DEFAULT 'confirmed',
            source TEXT DEFAULT 'manual',
            meeting_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    connection.commit()
    connection.close()


def migrate_database():
    """
    Apply incremental schema migrations to the existing database.

    Uses PRAGMA table_info() to inspect existing columns before
    running ALTER TABLE statements. This makes the migration safe
    to run every time the application starts.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # ============================================================
    # ACTION ITEMS
    # ============================================================

    existing_action_item_cols = {
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(action_items)"
        ).fetchall()
    }

    if "owner_email" not in existing_action_item_cols:
        cursor.execute(
            """
            ALTER TABLE action_items
            ADD COLUMN owner_email TEXT
            """
        )

    if "human_modified" not in existing_action_item_cols:
        cursor.execute(
            """
            ALTER TABLE action_items
            ADD COLUMN human_modified INTEGER DEFAULT 0
            """
        )

    if "updated_at" not in existing_action_item_cols:
        cursor.execute(
            """
            ALTER TABLE action_items
            ADD COLUMN updated_at TIMESTAMP
            """
        )

    if "email_sent" not in existing_action_item_cols:
        cursor.execute(
            """
            ALTER TABLE action_items
            ADD COLUMN email_sent INTEGER DEFAULT 0
            """
        )

    if "completed" not in existing_action_item_cols:
        cursor.execute(
            """
            ALTER TABLE action_items
            ADD COLUMN completed INTEGER DEFAULT 0
            """
        )

    if "completed_at" not in existing_action_item_cols:
        cursor.execute(
            """
            ALTER TABLE action_items
            ADD COLUMN completed_at TIMESTAMP
            """
        )

    # ============================================================
    # MEETING REQUESTS
    # ============================================================

    existing_meeting_request_cols = {
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(meeting_requests)"
        ).fetchall()
    }

    if "updated_at" not in existing_meeting_request_cols:
        cursor.execute(
            """
            ALTER TABLE meeting_requests
            ADD COLUMN updated_at TIMESTAMP
            """
        )

    # ============================================================
    # ACTION ITEM HISTORY
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_item_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action_item_id INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (action_item_id) REFERENCES action_items(id)
        )
        """
    )

    # ============================================================
    # CALENDAR EVENTS
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT,
            notes TEXT,
            status TEXT DEFAULT 'confirmed',
            source TEXT DEFAULT 'manual',
            meeting_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meeting_id) REFERENCES meetings(id)
        )
        """
    )

    # ============================================================
    # USERS TABLE & SEEDING
    # ============================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    default_users = [
        ("lead", "lead", "Team Lead", "lead", "lead@company.com"),
        ("priya", "priya", "Priya", "member", "priya@example.com"),
        ("simon", "simon", "Simon", "member", "simon@example.com"),
        ("mathew", "mathew", "Mathew", "member", "mathew@example.com"),
        ("joseph", "joseph", "Joseph", "member", "joseph@example.com"),
    ]

    for username, password, name, role, email in default_users:
        cursor.execute(
            """
            INSERT OR IGNORE INTO users (
                username,
                password,
                name,
                role,
                email
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, password, name, role, email),
        )

    for username, email in (
        ("lead", "lead@example.com"),
        ("priya", "priya@example.com"),
        ("simon", "simon@example.com"),
        ("mathew", "mathew@example.com"),
        ("joseph", "joseph@example.com"),
    ):
        cursor.execute(
            "UPDATE users SET email = ? WHERE username = ?",
            (email, username),
        )

    connection.commit()
    connection.close()


def get_user_by_username(username: str):
    """Retrieve user record by username."""
    connection = get_connection()
    cursor = connection.cursor()

    row = cursor.execute(
        """
        SELECT id, username, password, name, role, email
        FROM users
        WHERE username = ?
        """,
        (username.strip().lower(),),
    ).fetchone()

    connection.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "username": row["username"],
        "password": row["password"],
        "name": row["name"],
        "role": row["role"],
        "email": row["email"],
    }


def get_all_team_members():
    """Retrieve all users formatted for team member assignment."""
    connection = get_connection()
    cursor = connection.cursor()

    rows = cursor.execute(
        """
        SELECT id, username, name, role, email
        FROM users
        ORDER BY
            CASE WHEN role = 'lead' THEN 0 ELSE 1 END,
            name ASC
        """
    ).fetchall()

    connection.close()

    return [
        {
            "id": row["id"],
            "username": row["username"],
            "name": row["name"],
            "role": row["role"],
            "email": row["email"],
        }
        for row in rows
    ]


def toggle_action_item_completion(action_item_id: int, completed: int):
    """Update completion state of an action item."""
    connection = get_connection()
    cursor = connection.cursor()

    completed_flag = 1 if completed else 0
    completed_at = "CURRENT_TIMESTAMP" if completed_flag else "NULL"

    cursor.execute(
        f"""
        UPDATE action_items
        SET
            completed = ?,
            completed_at = {completed_at}
        WHERE id = ?
        """,
        (completed_flag, action_item_id),
    )

    connection.commit()

    updated = cursor.execute(
        """
        SELECT
            id,
            meeting_id,
            task,
            owner,
            owner_email,
            due_date,
            status,
            completed,
            completed_at
        FROM action_items
        WHERE id = ?
        """,
        (action_item_id,),
    ).fetchone()

    connection.close()

    if not updated:
        return None

    return dict(updated)


def record_action_item_history(
    cursor,
    action_item_id,
    field_name,
    old_value,
    new_value,
):
    """
    Record one human modification to an action item.

    The caller supplies the cursor so the history entry is part
    of the same SQLite transaction as the action-item update.
    """

    cursor.execute(
        """
        INSERT INTO action_item_history (
            action_item_id,
            field_name,
            old_value,
            new_value
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            action_item_id,
            field_name,
            str(old_value)
            if old_value is not None
            else None,
            str(new_value)
            if new_value is not None
            else None,
        ),
    )


def save_meeting(
    filename,
    segments,
    intelligence,
):
    connection = get_connection()
    cursor = connection.cursor()

    # ============================================================
    # MEETING
    # ============================================================

    cursor.execute(
        """
        INSERT INTO meetings (
            filename,
            summary
        )
        VALUES (?, ?)
        """,
        (
            filename,
            json.dumps(
                intelligence.summary
            ),
        ),
    )

    meeting_id = cursor.lastrowid

    # ============================================================
    # TRANSCRIPT SEGMENTS
    # ============================================================

    for segment in segments:
        cursor.execute(
            """
            INSERT INTO transcript_segments (
                meeting_id,
                start_time,
                end_time,
                text
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                meeting_id,
                segment["start"],
                segment["end"],
                segment["text"],
            ),
        )

    # ============================================================
    # ACTION ITEMS
    # ============================================================

    for item in intelligence.action_items:
        cursor.execute(
            """
            INSERT INTO action_items (
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
                email_sent
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meeting_id,
                item.task,
                item.owner,
                None,
                item.due_date,
                item.confidence,
                item.source_timestamp,
                item.status,
                item.type,
                0,
                0,
            ),
        )

    # ============================================================
    # MEETING REQUESTS
    # ============================================================

    for request in intelligence.meeting_requests:
        cursor.execute(
            """
            INSERT INTO meeting_requests (
                meeting_id,
                topic,
                suggested_date,
                suggested_time,
                confidence,
                source_timestamp,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                meeting_id,
                request.topic,
                request.suggested_date,
                request.suggested_time,
                request.confidence,
                request.source_timestamp,
                request.status,
            ),
        )

    # ============================================================
    # DECISIONS
    # ============================================================

    for decision in intelligence.decisions:
        cursor.execute(
            """
            INSERT INTO decisions (
                meeting_id,
                decision,
                confidence,
                source_timestamp,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                meeting_id,
                decision.decision,
                decision.confidence,
                decision.source_timestamp,
                decision.status,
            ),
        )

    # ============================================================
    # OPEN QUESTIONS
    # ============================================================

    for question in intelligence.open_questions:
        cursor.execute(
            """
            INSERT INTO open_questions (
                meeting_id,
                question,
                confidence,
                source_timestamp,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                meeting_id,
                question.question,
                question.confidence,
                question.source_timestamp,
                question.status,
            ),
        )

    # ============================================================
    # RISKS
    # ============================================================

    for risk in intelligence.risks:
        cursor.execute(
            """
            INSERT INTO risks (
                meeting_id,
                risk,
                confidence,
                source_timestamp,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                meeting_id,
                risk.risk,
                risk.confidence,
                risk.source_timestamp,
                risk.status,
            ),
        )

    connection.commit()
    connection.close()

    return meeting_id