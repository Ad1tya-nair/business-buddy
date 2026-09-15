import os
import json
import sqlite3
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_connection, migrate_database
from app.services.email import get_owner_email, send_action_item_email


def test_schema_and_migration():
    migrate_database()
    conn = get_connection()
    cursor = conn.cursor()

    ai_cols = {r["name"] for r in cursor.execute("PRAGMA table_info(action_items)").fetchall()}
    assert "human_modified" in ai_cols
    assert "updated_at" in ai_cols
    assert "email_sent" in ai_cols

    mr_cols = {r["name"] for r in cursor.execute("PRAGMA table_info(meeting_requests)").fetchall()}
    assert "updated_at" in mr_cols

    hist_tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='action_item_history'").fetchall()
    assert len(hist_tables) == 1
    conn.close()
    print("[OK] Schema and migration test passed")


def test_email_service():
    os.environ["OWNER_EMAILS"] = json.dumps({"Alice": "alice@example.com"})
    assert get_owner_email("Alice") == "alice@example.com"
    assert get_owner_email("NonExistent") is None

    # Without SMTP config, should return False without raising
    sent = send_action_item_email(
        task="Write documentation",
        owner_name="Alice",
        owner_email="alice@example.com",
        due_date="Tomorrow",
        meeting_name="Sprint Planning",
    )
    assert sent is False
    print("[OK] Email service test passed")


def test_action_item_edit_history_and_tasks():
    client = TestClient(app)

    conn = get_connection()
    cursor = conn.cursor()

    # Ensure a meeting exists
    meeting = cursor.execute("SELECT id, filename FROM meetings LIMIT 1").fetchone()
    if not meeting:
        cursor.execute("INSERT INTO meetings (filename, summary) VALUES ('Test Meeting', '[]')")
        conn.commit()
        meeting_id = cursor.lastrowid
        filename = "Test Meeting"
    else:
        meeting_id = meeting["id"]
        filename = meeting["filename"]

    # Insert a test action item
    cursor.execute(
        """
        INSERT INTO action_items (meeting_id, task, owner, due_date, confidence, source_timestamp, status, type)
        VALUES (?, 'Test Action Item For Flow', 'Initial Owner', '2026-09-15', 0.9, '01:00', 'pending_review', 'committed')
        """,
        (meeting_id,),
    )
    conn.commit()
    ai_id = cursor.lastrowid
    conn.close()

    # 1. Edit the action item
    res = client.patch(f"/action-items/{ai_id}", json={
        "owner": "Updated Owner",
        "due_date": "2026-09-20",
    })
    assert res.status_code == 200, res.text
    assert res.json()["status"] == "pending_review"

    # Verify history recorded
    conn = get_connection()
    cursor = conn.cursor()
    hist_rows = cursor.execute(
        "SELECT field_name, old_value, new_value FROM action_item_history WHERE action_item_id = ?",
        (ai_id,),
    ).fetchall()
    hist_fields = {r["field_name"]: (r["old_value"], r["new_value"]) for r in hist_rows}
    assert "owner" in hist_fields
    assert hist_fields["owner"] == ("Initial Owner", "Updated Owner")
    assert "due_date" in hist_fields
    assert hist_fields["due_date"] == ("2026-09-15", "2026-09-20")

    # Verify human_modified is set
    item = cursor.execute("SELECT human_modified, status, owner, due_date FROM action_items WHERE id = ?", (ai_id,)).fetchone()
    assert item["human_modified"] == 1
    assert item["status"] == "pending_review"
    assert item["owner"] == "Updated Owner"
    assert item["due_date"] == "2026-09-20"
    conn.close()

    # 2. Confirm the action item
    res = client.patch(f"/action-items/{ai_id}/confirm")
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"

    # 3. Verify it shows up in /tasks
    res = client.get("/tasks")
    assert res.status_code == 200
    tasks = res.json()
    confirmed_task = next((t for t in tasks if t["id"] == ai_id), None)
    assert confirmed_task is not None
    assert confirmed_task["owner"] == "Updated Owner"
    assert confirmed_task["due_date"] == "2026-09-20"
    assert confirmed_task["status"] == "confirmed"

    # Clean up test item
    conn = get_connection()
    conn.execute("DELETE FROM action_item_history WHERE action_item_id = ?", (ai_id,))
    conn.execute("DELETE FROM action_items WHERE id = ?", (ai_id,))
    conn.commit()
    conn.close()

    print("[OK] Action item edit history and tasks flow test passed")


def test_calendar_meeting_requests_flow():
    client = TestClient(app)

    conn = get_connection()
    cursor = conn.cursor()

    meeting = cursor.execute("SELECT id FROM meetings LIMIT 1").fetchone()
    meeting_id = meeting["id"] if meeting else 1

    cursor.execute(
        """
        INSERT INTO meeting_requests (meeting_id, topic, suggested_date, suggested_time, confidence, source_timestamp, status)
        VALUES (?, 'Architecture Review', 'September 22nd', '3:00 PM', 0.85, '04:30', 'pending_review')
        """,
        (meeting_id,),
    )
    conn.commit()
    mr_id = cursor.lastrowid
    conn.close()

    # 1. Verify in /calendar
    res = client.get("/calendar")
    assert res.status_code == 200
    cal = res.json()
    req = next((r for r in cal if r["id"] == mr_id), None)
    assert req is not None
    assert req["status"] == "pending_review"

    # 2. Edit meeting request
    res = client.patch(f"/meeting-requests/{mr_id}", json={
        "topic": "Architecture Review (Updated)",
        "suggested_date": "September 25th",
    })
    assert res.status_code == 200

    # 3. Confirm meeting request
    res = client.patch(f"/meeting-requests/{mr_id}/confirm")
    assert res.status_code == 200
    assert res.json()["status"] == "confirmed"

    # 4. Verify in /calendar as confirmed
    res = client.get("/calendar")
    cal = res.json()
    req = next((r for r in cal if r["id"] == mr_id), None)
    assert req["topic"] == "Architecture Review (Updated)"
    assert req["suggested_date"] == "September 25th"
    assert req["status"] == "confirmed"

    # Clean up test request
    conn = get_connection()
    conn.execute("DELETE FROM meeting_requests WHERE id = ?", (mr_id,))
    conn.commit()
    conn.close()

    print("[OK] Calendar meeting requests flow test passed")


if __name__ == "__main__":
    test_schema_and_migration()
    test_email_service()
    test_action_item_edit_history_and_tasks()
    test_calendar_meeting_requests_flow()
    print("\nALL INTEGRATION TESTS PASSED!")
