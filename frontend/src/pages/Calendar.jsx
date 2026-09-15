import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import {
  getCalendar,
  createCalendarEvent,
  updateCalendarEvent,
  deleteCalendarEvent,
  updateMeetingRequest,
  confirmMeetingRequest,
  dismissMeetingRequest,
} from "../services/api"

// ============================================================
// EMPTY MANUAL EVENT
// ============================================================

const EMPTY_EVENT = {
  title: "",
  event_date: "",
  event_time: "",
  notes: "",
}

// ============================================================
// DATE / TIME FORMATTERS
// ============================================================

function formatDisplayDate(value) {
  if (!value) {
    return "Date not specified"
  }

  const stringValue = String(value)

  // Native HTML date input format: YYYY-MM-DD
  const match = stringValue.match(
    /^(\d{4})-(\d{2})-(\d{2})$/
  )

  if (match) {
    const [, year, month, day] = match

    const date = new Date(
      Number(year),
      Number(month) - 1,
      Number(day)
    )

    return date.toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    })
  }

  // Fallback if backend returns another valid date format
  const date = new Date(stringValue)

  if (!Number.isNaN(date.getTime())) {
    return date.toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    })
  }

  return stringValue
}

function formatDisplayTime(value) {
  if (!value) {
    return "Time not specified"
  }

  const stringValue = String(value)

  // Handle HH:MM or HH:MM:SS
  const match = stringValue.match(
    /^(\d{1,2}):(\d{2})(?::(\d{2}))?$/
  )

  if (match) {
    const hours = Number(match[1])
    const minutes = Number(match[2])

    const date = new Date()
    date.setHours(hours, minutes, 0, 0)

    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    })
  }

  return stringValue
}

// ============================================================
// CALENDAR PAGE
// ============================================================

function Calendar() {
  const [items, setItems] = useState([])

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [actionLoading, setActionLoading] = useState(null)

  // ----------------------------------------------------------
  // Manual event modal
  // ----------------------------------------------------------

  const [showEventForm, setShowEventForm] = useState(false)

  const [eventForm, setEventForm] = useState(
    EMPTY_EVENT
  )

  const [savingEvent, setSavingEvent] = useState(false)

  const [editingEventId, setEditingEventId] =
    useState(null)

  // ----------------------------------------------------------
  // AI meeting request editing
  // ----------------------------------------------------------

  const [editingRequestId, setEditingRequestId] =
    useState(null)

  const [requestForm, setRequestForm] = useState({
    topic: "",
    suggested_date: "",
    suggested_time: "",
  })

  const [savingRequest, setSavingRequest] =
    useState(false)

  // ----------------------------------------------------------
  // Dismissed visibility
  // ----------------------------------------------------------

  const [showDismissed, setShowDismissed] =
    useState(false)

  // ==========================================================
  // LOAD CALENDAR
  // ==========================================================

  async function loadCalendar() {
    try {
      setLoading(true)
      setError(null)

      const data = await getCalendar()

      setItems(
        Array.isArray(data)
          ? data
          : []
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCalendar()
  }, [])

  // ==========================================================
  // MANUAL EVENT FORM
  // ==========================================================

  function openCreateEvent() {
    setEditingEventId(null)

    setEventForm({
      ...EMPTY_EVENT,
    })

    setError(null)
    setShowEventForm(true)
  }

  function openEditEvent(event) {
    setEditingEventId(event.id)

    setEventForm({
      title: event.title || "",
      event_date: event.event_date || "",
      event_time: event.event_time || "",
      notes: event.notes || "",
    })

    setError(null)
    setShowEventForm(true)
  }

  function closeEventForm() {
    if (savingEvent) {
      return
    }

    setShowEventForm(false)
    setEditingEventId(null)

    setEventForm({
      ...EMPTY_EVENT,
    })
  }

  function updateEventField(field, value) {
    setEventForm((previous) => ({
      ...previous,
      [field]: value,
    }))
  }

  // ==========================================================
  // SAVE MANUAL EVENT
  // ==========================================================

  async function handleSaveEvent() {
    const title =
      eventForm.title.trim()

    const eventDate =
      eventForm.event_date.trim()

    const eventTime =
      eventForm.event_time.trim()

    const notes =
      eventForm.notes.trim()

    if (!title) {
      setError(
        "Event title cannot be empty."
      )
      return
    }

    if (!eventDate) {
      setError(
        "Event date cannot be empty."
      )
      return
    }

    const payload = {
      title,
      event_date: eventDate,
      event_time:
        eventTime || null,
      notes:
        notes || null,
    }

    try {
      setSavingEvent(true)
      setError(null)

      if (editingEventId !== null) {
        const updated =
          await updateCalendarEvent(
            editingEventId,
            payload
          )

        setItems((previous) =>
          previous.map((item) =>
            item.source === "manual" &&
            item.id === editingEventId
              ? {
                  ...item,
                  ...payload,
                  ...(updated || {}),
                }
              : item
          )
        )
      } else {
        const created =
          await createCalendarEvent(
            payload
          )

        if (created) {
          setItems((previous) => [
            ...previous,
            created,
          ])
        } else {
          await loadCalendar()
        }
      }

      closeEventForm()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingEvent(false)
    }
  }

  // ==========================================================
  // DELETE MANUAL EVENT
  // ==========================================================

  async function handleDeleteEvent(eventId) {
    const confirmed =
      window.confirm(
        "Delete this calendar event?"
      )

    if (!confirmed) {
      return
    }

    try {
      setActionLoading(eventId)
      setError(null)

      await deleteCalendarEvent(eventId)

      setItems((previous) =>
        previous.filter(
          (item) =>
            !(
              item.source === "manual" &&
              item.id === eventId
            )
        )
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }

  // ==========================================================
  // AI MEETING REQUEST EDITING
  // ==========================================================

  function startEditRequest(request) {
    setEditingRequestId(
      request.id
    )

    setRequestForm({
      topic:
        request.topic || "",

      suggested_date:
        request.suggested_date || "",

      suggested_time:
        request.suggested_time || "",
    })

    setError(null)
  }

  function cancelEditRequest() {
    setEditingRequestId(null)

    setRequestForm({
      topic: "",
      suggested_date: "",
      suggested_time: "",
    })
  }

  function updateRequestField(field, value) {
    setRequestForm((previous) => ({
      ...previous,
      [field]: value,
    }))
  }

  // ==========================================================
  // SAVE AI REQUEST
  // ==========================================================

  async function handleSaveRequest(requestId) {
    const topic =
      requestForm.topic.trim()

    if (!topic) {
      setError(
        "Meeting topic cannot be empty."
      )
      return
    }

    const payload = {
      topic,

      suggested_date:
        requestForm.suggested_date.trim() ||
        null,

      suggested_time:
        requestForm.suggested_time.trim() ||
        null,
    }

    try {
      setSavingRequest(true)
      setError(null)

      await updateMeetingRequest(
        requestId,
        payload
      )

      setItems((previous) =>
        previous.map((item) =>
          item.source === "ai" &&
          item.id === requestId
            ? {
                ...item,
                ...payload,
              }
            : item
        )
      )

      cancelEditRequest()
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingRequest(false)
    }
  }

  // ==========================================================
  // CONFIRM AI REQUEST
  // ==========================================================

  async function handleConfirmRequest(requestId) {
    try {
      setActionLoading(requestId)
      setError(null)

      await confirmMeetingRequest(
        requestId
      )

      setItems((previous) =>
        previous.map((item) =>
          item.source === "ai" &&
          item.id === requestId
            ? {
                ...item,
                status: "confirmed",
              }
            : item
        )
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }

  // ==========================================================
  // DISMISS AI REQUEST
  // ==========================================================

  async function handleDismissRequest(requestId) {
    try {
      setActionLoading(requestId)
      setError(null)

      await dismissMeetingRequest(
        requestId
      )

      setItems((previous) =>
        previous.map((item) =>
          item.source === "ai" &&
          item.id === requestId
            ? {
                ...item,
                status: "dismissed",
              }
            : item
        )
      )
    } catch (err) {
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }

  // ==========================================================
  // CLASSIFY ITEMS
  // ==========================================================

  /*
    IMPORTANT:

    The backend returns two different record types:

      source === "ai"
        → AI meeting request

      source === "manual"
        → manually created calendar event

    Do NOT infer the record type from meeting_id.

    meeting_id is only a relationship to the originating
    meeting. It does NOT tell us that the record is a
    meeting_request.

    Any malformed/unknown record is ignored by the UI rather
    than being sent to the wrong endpoint.
  */

  const aiRequests =
    items.filter(
      (item) =>
        item &&
        item.source === "ai"
    )

  const manualEvents =
    items.filter(
      (item) =>
        item &&
        item.source === "manual"
    )

  const confirmedAIEvents =
    aiRequests.filter(
      (item) =>
        item.status === "confirmed"
    )

  const pendingRequests =
    aiRequests.filter(
      (item) =>
        item.status === "pending_review"
    )

  const dismissedRequests =
    aiRequests.filter(
      (item) =>
        item.status === "dismissed"
    )

  const confirmedManualEvents =
    manualEvents.filter(
      (item) =>
        item.status !== "dismissed"
    )

  // ==========================================================
  // MANUAL EVENT CARD
  // ==========================================================

  function renderManualEvent(event) {
    const busy =
      actionLoading === event.id

    return (
      <div
        key={`manual-${event.id}`}
        className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700"
      >
        <div className="flex items-start justify-between gap-4">

          <div className="min-w-0">

            <p className="text-base font-medium text-white">
              {event.title}
            </p>

            <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-400">

              <span>
                Date:{" "}
                <span className="text-slate-200">
                  {formatDisplayDate(
                    event.event_date
                  )}
                </span>
              </span>

              <span>
                Time:{" "}
                <span className="text-slate-200">
                  {formatDisplayTime(
                    event.event_time
                  )}
                </span>
              </span>

            </div>

            {event.notes && (
              <p className="mt-3 text-sm leading-6 text-slate-400">
                {event.notes}
              </p>
            )}

          </div>

          <span className="shrink-0 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-medium text-emerald-400">
            Confirmed
          </span>

        </div>

        <div className="mt-4 flex items-center justify-between border-t border-slate-800 pt-3">

          <span className="text-xs text-slate-600">
            Manual event
          </span>

          <div className="flex gap-2">

            <button
              onClick={() =>
                openEditEvent(event)
              }
              disabled={busy}
              className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
            >
              Edit
            </button>

            <button
              onClick={() =>
                handleDeleteEvent(
                  event.id
                )
              }
              disabled={busy}
              className="rounded-lg border border-red-900/60 px-3 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-950/30 disabled:opacity-50"
            >
              {busy
                ? "Deleting..."
                : "Delete"}
            </button>

          </div>

        </div>
      </div>
    )
  }

  // ==========================================================
  // CONFIRMED AI EVENT CARD
  // ==========================================================

  function renderConfirmedAIEvent(event) {
    const busy =
      actionLoading === event.id
  
    const editing =
      editingRequestId === event.id
  
    return (
      <div
        key={`ai-confirmed-${event.id}`}
        className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700"
      >
  
        {editing ? (
  
          <div className="space-y-4">
  
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-400">
                Meeting Topic
              </label>
  
              <input
                type="text"
                value={requestForm.topic}
                onChange={(e) =>
                  updateRequestField(
                    "topic",
                    e.target.value
                  )
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
              />
            </div>
  
            <div className="grid gap-3 md:grid-cols-2">
  
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-400">
                  Date
                </label>
  
                <input
                  type="text"
                  value={requestForm.suggested_date}
                  placeholder="e.g. September 20th"
                  onChange={(e) =>
                    updateRequestField(
                      "suggested_date",
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                />
              </div>
  
              <div>
                <label className="mb-1 block text-xs font-medium text-slate-400">
                  Time
                </label>
  
                <input
                  type="text"
                  value={requestForm.suggested_time}
                  placeholder="e.g. 3:00 PM"
                  onChange={(e) =>
                    updateRequestField(
                      "suggested_time",
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                />
              </div>
  
            </div>
  
            <div className="flex gap-2 pt-2">
  
              <button
                onClick={() =>
                  handleSaveRequest(event.id)
                }
                disabled={savingRequest}
                className="rounded-lg bg-indigo-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-400 disabled:opacity-50"
              >
                {savingRequest
                  ? "Saving..."
                  : "Save Changes"}
              </button>
  
              <button
                onClick={cancelEditRequest}
                disabled={savingRequest}
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
              >
                Cancel
              </button>
  
            </div>
  
          </div>
  
        ) : (
  
          <div>
  
            <div className="flex items-start justify-between gap-4">
  
              <div className="min-w-0">
  
                <p className="text-base font-medium text-white">
                  {event.topic}
                </p>
  
                <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-400">
  
                  <span>
                    Date:{" "}
                    <span className="text-slate-200">
                      {event.suggested_date ||
                        "Date not specified"}
                    </span>
                  </span>
  
                  <span>
                    Time:{" "}
                    <span className="text-slate-200">
                      {event.suggested_time ||
                        "Time not specified"}
                    </span>
                  </span>
  
                </div>
  
              </div>
  
              <span className="shrink-0 rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-medium text-emerald-400">
                Confirmed
              </span>
  
            </div>
  
            <div className="mt-4 flex items-center justify-between border-t border-slate-800 pt-3">
  
              {event.meeting_id ? (
                <Link
                  to={`/meetings/${event.meeting_id}`}
                  className="text-xs text-slate-500 transition hover:text-indigo-400"
                >
                  From {event.filename || "meeting"} →
                </Link>
              ) : (
                <span className="text-xs text-slate-600">
                  AI meeting request
                </span>
              )}
  
              <div className="flex gap-2">
  
                <button
                  onClick={() =>
                    startEditRequest(event)
                  }
                  disabled={busy}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
                >
                  Edit
                </button>
  
                <button
                  onClick={() =>
                    handleDismissRequest(event.id)
                  }
                  disabled={busy}
                  className="rounded-lg border border-red-900/60 px-3 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-950/30 disabled:opacity-50"
                >
                  {busy
                    ? "Removing..."
                    : "Remove"}
                </button>
  
              </div>
  
            </div>
  
          </div>
  
        )}
  
      </div>
    )
  }
  // ==========================================================
  // PENDING AI REQUEST CARD
  // ==========================================================

  function renderPendingRequest(request) {
    const busy =
      actionLoading === request.id

    const editing =
      editingRequestId === request.id

    return (
      <div
        key={`pending-${request.id}`}
        className="rounded-xl border border-slate-800 bg-slate-900 p-5 transition hover:border-slate-700"
      >

        {editing ? (

          <div className="space-y-4">

            <div>

              <label className="mb-1 block text-xs font-medium text-slate-400">
                Meeting Topic
              </label>

              <input
                type="text"
                value={
                  requestForm.topic
                }
                onChange={(e) =>
                  updateRequestField(
                    "topic",
                    e.target.value
                  )
                }
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
              />

            </div>

            <div className="grid gap-3 md:grid-cols-2">

              <div>

                <label className="mb-1 block text-xs font-medium text-slate-400">
                  Suggested Date
                </label>

                <input
                  type="text"
                  value={
                    requestForm.suggested_date
                  }
                  placeholder="e.g. September 20th"
                  onChange={(e) =>
                    updateRequestField(
                      "suggested_date",
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                />

              </div>

              <div>

                <label className="mb-1 block text-xs font-medium text-slate-400">
                  Suggested Time
                </label>

                <input
                  type="text"
                  value={
                    requestForm.suggested_time
                  }
                  placeholder="e.g. 2:00 PM"
                  onChange={(e) =>
                    updateRequestField(
                      "suggested_time",
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-indigo-500"
                />

              </div>

            </div>

            <div className="flex gap-2 pt-2">

              <button
                onClick={() =>
                  handleSaveRequest(
                    request.id
                  )
                }
                disabled={savingRequest}
                className="rounded-lg bg-indigo-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-400 disabled:opacity-50"
              >
                {savingRequest
                  ? "Saving..."
                  : "Save Changes"}
              </button>

              <button
                onClick={
                  cancelEditRequest
                }
                disabled={savingRequest}
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
              >
                Cancel
              </button>

            </div>

          </div>

        ) : (

          <div>

            <div className="flex items-start justify-between gap-6">

              <div className="min-w-0">

                <p className="text-base font-medium text-white">
                  {request.topic}
                </p>

                <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-xs text-slate-500">

                  <span>
                    Suggested Date:{" "}
                    <span className="text-slate-300">
                      {request.suggested_date ||
                        "Not specified"}
                    </span>
                  </span>

                  <span>
                    Suggested Time:{" "}
                    <span className="text-slate-300">
                      {request.suggested_time ||
                        "Not specified"}
                    </span>
                  </span>

                  {request.source_timestamp && (
                    <span>
                      Source:{" "}
                      <span className="text-slate-400">
                        {request.source_timestamp}
                      </span>
                    </span>
                  )}

                </div>

              </div>

              <span className="shrink-0 rounded-full bg-amber-500/15 px-3 py-1 text-xs font-medium text-amber-400">
                Pending Review
              </span>

            </div>

            <div className="mt-4 flex flex-col gap-3 border-t border-slate-800 pt-3 sm:flex-row sm:items-center sm:justify-between">

              {request.meeting_id ? (
                <Link
                  to={`/meetings/${request.meeting_id}`}
                  className="text-xs text-slate-500 transition hover:text-indigo-400"
                >
                  From {request.filename || "meeting"} →
                </Link>
              ) : (
                <span className="text-xs text-slate-600">
                  AI meeting request
                </span>
              )}

              <div className="flex flex-wrap gap-2">

                <button
                  onClick={() =>
                    startEditRequest(
                      request
                    )
                  }
                  disabled={busy}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
                >
                  Edit
                </button>

                <button
                  onClick={() =>
                    handleConfirmRequest(
                      request.id
                    )
                  }
                  disabled={busy}
                  className="rounded-lg bg-indigo-500 px-3 py-1.5 text-xs font-medium text-white transition hover:bg-indigo-400 disabled:opacity-50"
                >
                  {busy
                    ? "Confirming..."
                    : "Confirm Event"}
                </button>

                <button
                  onClick={() =>
                    handleDismissRequest(
                      request.id
                    )
                  }
                  disabled={busy}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
                >
                  Dismiss
                </button>

              </div>

            </div>

          </div>

        )}

      </div>
    )
  }

  // ==========================================================
  // RENDER
  // ==========================================================

  return (
    <div className="calendar-page space-y-8">

      {/* HEADER */}

      <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">

        <div>

          <p className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
            Internal Event Schedule
          </p>

          <h1 className="mt-1 text-3xl font-semibold text-white">
            Calendar
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            Review AI-detected meeting requests and manage
            confirmed internal events.
          </p>

        </div>

        <button
          onClick={
            openCreateEvent
          }
          className="rounded-lg bg-indigo-500 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-400"
        >
          + Add Event
        </button>

      </div>

      {/* ERROR */}

      {error && (
        <div className="rounded-xl border border-red-900 bg-red-950/30 p-4 text-sm text-red-400">
          {error}
        </div>
      )}

      {/* LOADING */}

      {loading && (
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-5 text-sm text-slate-400">
          Loading calendar events...
        </div>
      )}

      {!loading && (

        <div className="space-y-10">

          {/* ==================================================
              CONFIRMED EVENTS
          ================================================== */}

          <section className="space-y-4">

            <div className="border-b border-slate-800 pb-3">

              <h2 className="text-lg font-medium text-white">
                Confirmed Events (
                {
                  confirmedAIEvents.length +
                  confirmedManualEvents.length
                }
                )
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Authorized meetings and manually created
                internal events.
              </p>

            </div>

            {confirmedAIEvents.length === 0 &&
            confirmedManualEvents.length === 0 ? (

              <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-6 text-center text-sm text-slate-500">
                No confirmed events yet.
              </div>

            ) : (

              <div className="grid gap-3 md:grid-cols-2">

                {confirmedAIEvents.map(
                  renderConfirmedAIEvent
                )}

                {confirmedManualEvents.map(
                  renderManualEvent
                )}

              </div>

            )}

          </section>

          {/* ==================================================
              PENDING REVIEW
          ================================================== */}

          <section className="space-y-4">

            <div className="border-b border-slate-800 pb-3">

              <h2 className="text-lg font-medium text-white">
                Pending Review (
                {pendingRequests.length}
                )
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                AI-detected meeting requests awaiting
                human authorization.
              </p>

            </div>

            {pendingRequests.length === 0 ? (

              <div className="rounded-xl border border-slate-800/60 bg-slate-900/40 p-6 text-center text-sm text-slate-500">
                No meeting requests pending review.
              </div>

            ) : (

              <div className="space-y-3">

                {pendingRequests.map(
                  renderPendingRequest
                )}

              </div>

            )}

          </section>

          {/* ==================================================
              DISMISSED
          ================================================== */}

          {dismissedRequests.length > 0 && (

            <section className="space-y-3">

              <button
                onClick={() =>
                  setShowDismissed(
                    (previous) =>
                      !previous
                  )
                }
                className="flex w-full items-center justify-between border-b border-slate-800 pb-3 text-left"
              >

                <div>

                  <h2 className="text-sm font-medium text-slate-400">
                    Dismissed Requests (
                    {dismissedRequests.length}
                    )
                  </h2>

                  <p className="mt-1 text-xs text-slate-600">
                    AI suggestions that were rejected.
                  </p>

                </div>

                <span className="text-xs text-slate-600">
                  {showDismissed
                    ? "Hide"
                    : "Show"}
                </span>

              </button>

              {showDismissed && (

                <div className="space-y-2">

                  {dismissedRequests.map(
                    (request) => (

                      <div
                        key={`dismissed-${request.id}`}
                        className="flex items-center justify-between rounded-lg border border-slate-800/60 bg-slate-950 px-4 py-3"
                      >

                        <div className="min-w-0">

                          <p className="truncate text-sm text-slate-400">
                            {request.topic}
                          </p>

                          <p className="mt-1 text-xs text-slate-600">
                            {
                              request.suggested_date ||
                              "Date not specified"
                            }
                          </p>

                        </div>

                        <button
                          onClick={() =>
                            handleConfirmRequest(
                              request.id
                            )
                          }
                          disabled={
                            actionLoading ===
                            request.id
                          }
                          className="ml-4 shrink-0 text-xs text-indigo-400 transition hover:text-indigo-300 disabled:opacity-50"
                        >
                          Re-confirm
                        </button>

                      </div>

                    )
                  )}

                </div>

              )}

            </section>

          )}

        </div>

      )}

      {/* ======================================================
          ADD / EDIT EVENT MODAL
      ====================================================== */}

      {showEventForm && (

        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 px-4">

          <div className="w-full max-w-lg rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">

            <div className="flex items-start justify-between gap-4">

              <div>

                <p className="text-xs font-medium uppercase tracking-wider text-slate-500">
                  Internal Calendar
                </p>

                <h2 className="mt-1 text-xl font-semibold text-white">
                  {editingEventId !== null
                    ? "Edit Event"
                    : "Add Event"}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Select the date and time using the calendar
                  and time pickers.
                </p>

              </div>

              <button
                onClick={
                  closeEventForm
                }
                disabled={savingEvent}
                className="text-slate-500 transition hover:text-white disabled:opacity-50"
              >
                ✕
              </button>

            </div>

            <div className="mt-6 space-y-4">

              {/* TITLE */}

              <div>

                <label className="mb-1 block text-xs font-medium text-slate-400">
                  Event Title
                </label>

                <input
                  type="text"
                  value={
                    eventForm.title
                  }
                  onChange={(e) =>
                    updateEventField(
                      "title",
                      e.target.value
                    )
                  }
                  placeholder="e.g. Product review"
                  autoFocus
                  className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
                />

              </div>

              {/* DATE + TIME */}

              <div className="grid gap-3 sm:grid-cols-2">

                <div>

                  <label className="mb-1 block text-xs font-medium text-slate-400">
                    Date
                  </label>

                  <input
                    type="date"
                    value={
                      eventForm.event_date
                    }
                    onChange={(e) =>
                      updateEventField(
                        "event_date",
                        e.target.value
                      )
                    }
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
                  />

                </div>

                <div>

                  <label className="mb-1 block text-xs font-medium text-slate-400">
                    Time
                  </label>

                  <input
                    type="time"
                    value={
                      eventForm.event_time
                    }
                    onChange={(e) =>
                      updateEventField(
                        "event_time",
                        e.target.value
                      )
                    }
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
                  />

                </div>

              </div>

              {/* NOTES */}

              <div>

                <label className="mb-1 block text-xs font-medium text-slate-400">
                  Notes
                </label>

                <textarea
                  value={
                    eventForm.notes
                  }
                  onChange={(e) =>
                    updateEventField(
                      "notes",
                      e.target.value
                    )
                  }
                  placeholder="Optional notes..."
                  rows={4}
                  className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2.5 text-sm text-white outline-none focus:border-indigo-500"
                />

              </div>

            </div>

            {/* MODAL ACTIONS */}

            <div className="mt-6 flex justify-end gap-2">

              <button
                onClick={
                  closeEventForm
                }
                disabled={savingEvent}
                className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-300 transition hover:bg-slate-800 disabled:opacity-50"
              >
                Cancel
              </button>

              <button
                onClick={
                  handleSaveEvent
                }
                disabled={savingEvent}
                className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-400 disabled:opacity-50"
              >
                {savingEvent
                  ? "Saving..."
                  : editingEventId !== null
                    ? "Save Changes"
                    : "Add Event"}
              </button>

            </div>

          </div>

        </div>

      )}

    </div>
  )
}

export default Calendar