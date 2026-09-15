import { useEffect, useState } from "react"
import {
  Link,
  useNavigate,
  useParams,
} from "react-router-dom"

import {
  getMeeting,
  confirmActionItem,
  dismissActionItem,
  reopenActionItem,
  deleteMeeting,
  updateMeeting,
  updateActionItem,
  updateDecision,
  getUsers,
} from "../services/api"
import { useAuth } from "../context/AuthContext"


function MeetingIntelligence() {
  const { meetingId } = useParams()
  const navigate = useNavigate()
  const { isLead } = useAuth()
  const [teamMembers, setTeamMembers] = useState([])


  const [meeting, setMeeting] =
    useState(null)

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState(null)

  const [activeTab, setActiveTab] =
    useState("overview")

  const [editing, setEditing] =
    useState(false)

  const [saving, setSaving] =
    useState(false)

  const [deleting, setDeleting] =
    useState(false)

  const [actionLoading, setActionLoading] =
    useState(null)

  // Editable fields
  const [meetingName, setMeetingName] =
    useState("")

  const [summaryPoints, setSummaryPoints] =
    useState([])

  const [actionItems, setActionItems] =
    useState([])

  const [decisions, setDecisions] =
    useState([])

  // Per-item inline action item editing
  const [editingItemIds, setEditingItemIds] =
    useState({})

  const [savingItemIds, setSavingItemIds] =
    useState({})


  // ============================================================
  // LOAD MEETING
  // ============================================================

  useEffect(() => {
    async function loadMeeting() {
      try {
        setLoading(true)

        const data =
          await getMeeting(meetingId)

        setMeeting(data)

        setMeetingName(
          data.filename || ""
        )

        setSummaryPoints(
          Array.isArray(data.summary)
            ? [...data.summary]
            : []
        )

        setActionItems(
          Array.isArray(data.action_items)
            ? data.action_items.map(
                (item) => ({
                  ...item,
                })
              )
            : []
        )

        setDecisions(
          Array.isArray(data.decisions)
            ? data.decisions.map(
                (decision) => ({
                  ...decision,
                })
              )
            : []
        )

        if (isLead) {
          setTeamMembers(await getUsers())
        }

        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadMeeting()
  }, [isLead, meetingId])


  // ============================================================
  // START EDITING
  // ============================================================

  function startEditing() {
    setMeetingName(
      meeting.filename || ""
    )

    setSummaryPoints(
      Array.isArray(meeting.summary)
        ? [...meeting.summary]
        : []
    )

    setActionItems(
      Array.isArray(meeting.action_items)
        ? meeting.action_items.map(
            (item) => ({
              ...item,
            })
          )
        : []
    )

    setDecisions(
      Array.isArray(meeting.decisions)
        ? meeting.decisions.map(
            (decision) => ({
              ...decision,
            })
          )
        : []
    )

    setError(null)
    setEditing(true)
  }


  // ============================================================
  // CANCEL EDITING
  // ============================================================

  function cancelEditing() {
    setMeetingName(
      meeting.filename || ""
    )

    setSummaryPoints(
      Array.isArray(meeting.summary)
        ? [...meeting.summary]
        : []
    )

    setActionItems(
      Array.isArray(meeting.action_items)
        ? meeting.action_items.map(
            (item) => ({
              ...item,
            })
          )
        : []
    )

    setDecisions(
      Array.isArray(meeting.decisions)
        ? meeting.decisions.map(
            (decision) => ({
              ...decision,
            })
          )
        : []
    )

    setError(null)
    setEditing(false)
  }


  // ============================================================
  // SAVE ALL CHANGES
  // ============================================================

  async function saveChanges() {
    const trimmedName =
      meetingName.trim()

    if (!trimmedName) {
      setError(
        "Meeting name cannot be empty."
      )
      return
    }

    const cleanedSummary =
      summaryPoints
        .map((point) => point.trim())
        .filter(Boolean)

    const cleanedDecisions =
      decisions
        .map((decision) => ({
          ...decision,
          decision:
            decision.decision?.trim() ||
            "",
        }))
        .filter(
          (decision) =>
            decision.decision
        )

    try {
      setSaving(true)
      setError(null)

      // --------------------------------------------------------
      // Save meeting name + summary
      // --------------------------------------------------------

      await updateMeeting(
        meetingId,
        {
          filename: trimmedName,
          summary: cleanedSummary,
        }
      )


      // --------------------------------------------------------
      // Save decisions
      // --------------------------------------------------------

      for (const decision of cleanedDecisions) {
        await updateDecision(
          decision.id,
          {
            decision:
              decision.decision,
          }
        )
      }


      // --------------------------------------------------------
      // Update local state
      // --------------------------------------------------------

      setMeeting((previous) => ({
        ...previous,

        filename:
          trimmedName,

        summary:
          cleanedSummary,

        decisions:
          cleanedDecisions,
      }))

      setMeetingName(
        trimmedName
      )

      setSummaryPoints(
        cleanedSummary
      )

      setDecisions(
        cleanedDecisions
      )

      setEditing(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }


  // ============================================================
  // SUMMARY EDITING
  // ============================================================

  function updateSummaryPoint(
    index,
    value
  ) {
    setSummaryPoints(
      (previous) => {
        const updated = [
          ...previous,
        ]

        updated[index] = value

        return updated
      }
    )
  }


  function addSummaryPoint() {
    setSummaryPoints(
      (previous) => [
        ...previous,
        "",
      ]
    )
  }


  function removeSummaryPoint(
    index
  ) {
    setSummaryPoints(
      (previous) =>
        previous.filter(
          (_, pointIndex) =>
            pointIndex !== index
        )
    )
  }


  // ============================================================
  // PER-ITEM ACTION ITEM EDITING
  // ============================================================

  function startEditActionItem(item) {
    setEditingItemIds((prev) => ({
      ...prev,
      [item.id]: {
        task: item.task || "",
        owner: item.owner || "",
        owner_email: item.owner_email || "",
        due_date: item.due_date || "",
        type: item.type || "committed",
      },
    }))
    setError(null)
  }

  function cancelEditActionItem(itemId) {
    setEditingItemIds((prev) => {
      const next = { ...prev }
      delete next[itemId]
      return next
    })
  }

  function updateEditingActionField(itemId, field, value) {
    setEditingItemIds((prev) => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value,
      },
    }))
  }

  async function saveEditActionItem(itemId) {
    const editData = editingItemIds[itemId]
    if (!editData) return

    const trimmedTask = editData.task?.trim()
    if (!trimmedTask) {
      setError("Task description cannot be empty.")
      return
    }

    try {
      setSavingItemIds((prev) => ({ ...prev, [itemId]: true }))
      setError(null)

      const payload = {
        task: trimmedTask,
        owner: editData.owner?.trim() || null,
        owner_email: editData.owner_email?.trim() || null,
        due_date: editData.due_date?.trim() || null,
        type: editData.type || "committed",
      }

      await updateActionItem(itemId, payload)

      const updatedFields = {
        ...payload,
        status: "pending_review",
        human_modified: 1,
      }

      setMeeting((previous) => ({
        ...previous,
        action_items: previous.action_items.map((item) =>
          item.id === itemId ? { ...item, ...updatedFields } : item
        ),
      }))

      setActionItems((previous) =>
        previous.map((item) =>
          item.id === itemId ? { ...item, ...updatedFields } : item
        )
      )

      cancelEditActionItem(itemId)
    } catch (err) {
      setError(err.message)
    } finally {
      setSavingItemIds((prev) => ({ ...prev, [itemId]: false }))
    }
  }


  // ============================================================
  // DECISION EDITING
  // ============================================================

  function updateDecisionField(
    decisionId,
    value
  ) {
    setDecisions(
      (previous) =>
        previous.map(
          (decision) =>
            decision.id ===
            decisionId
              ? {
                  ...decision,
                  decision:
                    value,
                }
              : decision
        )
    )
  }


  // ============================================================
  // ACTION STATUS
  // ============================================================

  async function handleAction(
    action,
    actionItemId
  ) {
    try {
      setActionLoading(
        actionItemId
      )

      if (action === "confirm") {
        await confirmActionItem(
          actionItemId
        )

        updateActionStatus(
          actionItemId,
          "confirmed"
        )
      }

      if (action === "dismiss") {
        await dismissActionItem(
          actionItemId
        )

        updateActionStatus(
          actionItemId,
          "dismissed"
        )
      }

      if (action === "reopen") {
        await reopenActionItem(
          actionItemId
        )

        updateActionStatus(
          actionItemId,
          "pending_review"
        )
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }


  function updateActionStatus(
    actionItemId,
    status
  ) {
    setMeeting(
      (previous) => ({
        ...previous,

        action_items:
          previous.action_items.map(
            (item) =>
              item.id ===
              actionItemId
                ? {
                    ...item,
                    status,
                  }
                : item
          ),
      })
    )

    setActionItems(
      (previous) =>
        previous.map((item) =>
          item.id === actionItemId
            ? {
                ...item,
                status,
              }
            : item
        )
    )
  }


  // ============================================================
  // DELETE
  // ============================================================

  async function handleDeleteMeeting() {
    const confirmed =
      window.confirm(
        "Delete this meeting and all of its intelligence?"
      )

    if (!confirmed) {
      return
    }

    try {
      setDeleting(true)

      await deleteMeeting(
        meetingId
      )

      navigate("/meetings")
    } catch (err) {
      setError(err.message)
      setDeleting(false)
    }
  }


  // ============================================================
  // LOADING
  // ============================================================

  if (loading) {
    return (
      <div className="meeting-intelligence-page min-h-screen bg-slate-50 p-8 text-slate-600">
        Loading meeting...
      </div>
    )
  }


  // ============================================================
  // ERROR WITHOUT MEETING
  // ============================================================

  if (error && !meeting) {
    return (
      <div className="meeting-intelligence-page min-h-screen bg-slate-50 p-8">

        <p className="text-red-400">
          {error}
        </p>

        <Link
          to="/meetings"
          className="mt-4 inline-block text-sm text-slate-400 hover:text-white"
        >
          ← Back to meetings
        </Link>

      </div>
    )
  }


  if (!meeting) {
    return null
  }


  const tabs = [
    {
      id: "overview",
      label: "Overview",
    },
    {
      id: "transcript",
      label: "Transcript",
    },
    {
      id: "actions",
      label: "Actions",
    },
    {
      id: "decisions",
      label: "Decisions",
    },
    {
      id: "risks",
      label: "Risks",
    },
  ]


  // ============================================================
  // PAGE
  // ============================================================

  return (
    <div className="meeting-intelligence-page min-h-screen bg-slate-50 text-slate-900">

      {/* ====================================================== */}
      {/* HEADER */}
      {/* ====================================================== */}

      <header className="border-b border-slate-800 bg-slate-950">

        <div className="mx-auto max-w-6xl px-6 py-6">

          <div className="flex items-start justify-between gap-6">

            <div className="min-w-0 flex-1">

              <Link
                to="/meetings"
                className="text-sm text-slate-500 transition hover:text-slate-200"
              >
                ← Back to meetings
              </Link>


              <div className="mt-4">

                {editing ? (

                  <input
                    value={meetingName}
                    onChange={(event) =>
                      setMeetingName(
                        event.target.value
                      )
                    }
                    className="w-full max-w-2xl rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-2xl font-semibold text-white outline-none focus:border-slate-500"
                    autoFocus
                  />

                ) : (

                  <h1 className="truncate text-2xl font-semibold text-white">
                    {meeting.filename}
                  </h1>

                )}

                <p className="mt-2 text-sm text-slate-500">
                  Meeting Intelligence
                </p>

              </div>

            </div>


            {/* ================================================= */}
            {/* GLOBAL ACTIONS */}
            {/* ================================================= */}

            <div className="flex shrink-0 gap-2">

              {isLead && (editing ? (

                <>

                  <button
                    onClick={
                      saveChanges
                    }
                    disabled={saving}
                    className="rounded-lg bg-white px-4 py-2.5 text-sm font-medium text-slate-950 transition hover:bg-slate-200 disabled:opacity-50"
                  >
                    {saving
                      ? "Saving..."
                      : "Save changes"}
                  </button>

                  <button
                    onClick={
                      cancelEditing
                    }
                    disabled={saving}
                    className="meeting-action-button rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900 disabled:opacity-50"
                  >
                    Cancel
                  </button>

                </>

              ) : (

                <button
                  onClick={
                    startEditing
                  }
                  className="rounded-lg border border-slate-700 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:bg-slate-900"
                >
                  Edit
                </button>

              ))}

              {isLead && (
                <button
                  onClick={handleDeleteMeeting}
                  disabled={deleting || editing}
                  className="rounded-lg border border-red-900/70 px-4 py-2.5 text-sm font-medium text-red-400 transition hover:bg-red-950/40 disabled:opacity-40"
                >
                  {deleting ? "Deleting..." : "Delete meeting"}
                </button>
              )}

            </div>

          </div>


          {/* ================================================= */}
          {/* TABS */}
          {/* ================================================= */}

          <div className="mt-8 flex gap-7 border-b border-slate-800">

            {tabs.map((tab) => (

              <button
                key={tab.id}
                onClick={() =>
                  setActiveTab(
                    tab.id
                  )
                }
                className={`rounded-lg border px-4 py-2 text-sm font-semibold transition ${
                  activeTab === tab.id
                    ? "meeting-tab-active border-indigo-600 bg-indigo-600 text-white shadow-sm"
                    : "border-slate-300 bg-white text-slate-700 hover:border-indigo-300 hover:bg-indigo-50 hover:text-indigo-700"
                }`}
              >
                {tab.label}
              </button>

            ))}

          </div>

        </div>

      </header>


      {/* ====================================================== */}
      {/* MAIN */}
      {/* ====================================================== */}

      <main className="mx-auto max-w-6xl px-6 py-8">

        {error && (
          <div className="mb-6 rounded-lg border border-red-900/70 bg-red-950/30 px-4 py-3 text-sm text-red-300">
            {error}
          </div>
        )}


        {/* ==================================================== */}
        {/* OVERVIEW */}
        {/* ==================================================== */}

        {activeTab === "overview" && (

          <div className="space-y-6">

            {/* ------------------------------------------------ */}
            {/* SUMMARY */}
            {/* ------------------------------------------------ */}

            <section className="rounded-xl border border-slate-800 bg-slate-900/60">

              <div className="border-b border-slate-800 px-6 py-5">

                <h2 className="text-lg font-semibold text-white">
                  Summary
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Key points extracted from the meeting.
                </p>

              </div>


              <div className="px-6 py-6">

                {editing ? (

                  <div className="space-y-3">

                    {summaryPoints.map(
                      (
                        point,
                        index
                      ) => (

                        <div
                          key={index}
                          className="flex gap-2"
                        >

                          <input
                            value={point}
                            onChange={(
                              event
                            ) =>
                              updateSummaryPoint(
                                index,
                                event
                                  .target
                                  .value
                              )
                            }
                            placeholder="Enter a summary point..."
                            className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-slate-500"
                          />

                          <button
                            onClick={() =>
                              removeSummaryPoint(
                                index
                              )
                            }
                            className="rounded-lg border border-slate-700 px-3 text-lg text-slate-500 transition hover:border-red-900 hover:text-red-400"
                            title="Remove summary point"
                          >
                            ×
                          </button>

                        </div>

                      )
                    )}

                    <button
                      onClick={
                        addSummaryPoint
                      }
                      className="rounded-lg border border-dashed border-slate-700 px-4 py-2.5 text-sm font-medium text-slate-400 transition hover:border-slate-500 hover:text-white"
                    >
                      + Add summary point
                    </button>

                  </div>

                ) : (

                  meeting.summary?.length >
                  0 ? (

                    <ul className="space-y-4">

                      {meeting.summary.map(
                        (
                          point,
                          index
                        ) => (

                          <li
                            key={index}
                            className="flex gap-3 text-sm leading-6 text-slate-300"
                          >

                            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-500" />

                            <span>
                              {point}
                            </span>

                          </li>

                        )
                      )}

                    </ul>

                  ) : (

                    <div className="rounded-lg border border-dashed border-slate-800 px-4 py-8 text-center text-sm text-slate-500">
                      No summary points yet.
                    </div>

                  )

                )}

              </div>

            </section>


            {/* ------------------------------------------------ */}
            {/* INTELLIGENCE COUNTS */}
            {/* ------------------------------------------------ */}

            <div className="grid gap-4 md:grid-cols-3">

              <button
                onClick={() =>
                  setActiveTab(
                    "actions"
                  )
                }
                className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-left transition hover:border-slate-700 hover:bg-slate-900"
              >

                <p className="text-sm text-slate-500">
                  Action items
                </p>

                <p className="mt-2 text-3xl font-semibold text-white">
                  {meeting.action_items
                    ?.length || 0}
                </p>

              </button>


              <button
                onClick={() =>
                  setActiveTab(
                    "decisions"
                  )
                }
                className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-left transition hover:border-slate-700 hover:bg-slate-900"
              >

                <p className="text-sm text-slate-500">
                  Decisions
                </p>

                <p className="mt-2 text-3xl font-semibold text-white">
                  {meeting.decisions
                    ?.length || 0}
                </p>

              </button>


              <button
                onClick={() =>
                  setActiveTab(
                    "risks"
                  )
                }
                className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 text-left transition hover:border-slate-700 hover:bg-slate-900"
              >

                <p className="text-sm text-slate-500">
                  Risks / blockers
                </p>

                <p className="mt-2 text-3xl font-semibold text-white">
                  {meeting.risks
                    ?.length || 0}
                </p>

              </button>


            </div>

          </div>

        )}


        {/* ==================================================== */}
        {/* TRANSCRIPT */}
        {/* ==================================================== */}

        {activeTab === "transcript" && (

          <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60">

            <div className="border-b border-slate-800 px-6 py-5">

              <h2 className="text-lg font-semibold text-white">
                Transcript
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Transcript generated from the meeting recording.
              </p>

            </div>


            <div className="divide-y divide-slate-800">

              {meeting.transcript?.map(
                (segment) => (

                  <div
                    key={segment.id}
                    className="flex gap-6 px-6 py-5"
                  >

                    <span className="w-16 shrink-0 pt-0.5 text-xs font-medium text-slate-600">
                      {formatTimestamp(
                        segment.start_time
                      )}
                    </span>

                    <p className="text-sm leading-6 text-slate-300">
                      {segment.text}
                    </p>

                  </div>

                )
              )}

            </div>

          </section>

        )}


        {/* ==================================================== */}
        {/* ACTIONS */}
        {/* ==================================================== */}

        {activeTab === "actions" && (

          <section>

            <div className="mb-6">

              <h2 className="text-lg font-semibold text-white">
                Action items
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Review and manage actions extracted from the meeting.
              </p>

            </div>


            <div className="space-y-5">

              {actionItems.length > 0 ? (

                actionItems.map((item) => (

                  <div
                    key={item.id}
                    className="rounded-2xl border border-slate-800 bg-slate-900/80 px-6 py-6"
                  >

                    {editingItemIds[item.id] ? (

                      /* ================================================= */
                      /* PER-ITEM EDIT MODE */
                      /* ================================================= */

                      <div className="space-y-5">

                        <div>

                          <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
                            Task
                          </label>

                          <textarea
                            value={editingItemIds[item.id].task || ""}
                            onChange={(event) =>
                              updateEditingActionField(
                                item.id,
                                "task",
                                event.target.value
                              )
                            }
                            rows={2}
                            className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none focus:border-slate-500"
                          />

                        </div>


                        <div className="grid gap-4 md:grid-cols-2">

<div>
  <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
    Owner
  </label>

  <select
    value={editingItemIds[item.id].owner || ""}
    onChange={(event) => {
      const selected = teamMembers.find(
        (member) => member.name === event.target.value
      )
      updateEditingActionField(item.id, "owner", event.target.value)
      updateEditingActionField(
        item.id,
        "owner_email",
        selected?.email || ""
      )
    }}
    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-slate-500"
  >
    <option value="">Unassigned</option>
    {teamMembers
      .filter((member) => member.role === "member")
      .map((member) => (
        <option key={member.id} value={member.name}>{member.name}</option>
      ))}
  </select>
</div>


<div>
  <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
    Owner email
  </label>

  <input
    type="email"
    value={
      editingItemIds[item.id].owner_email || ""
    }
    onChange={(event) =>
      updateEditingActionField(
        item.id,
        "owner_email",
        event.target.value
      )
    }
    placeholder="owner@example.com"
    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-slate-500"
  />
</div>


<div>
  <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
    Due date
  </label>

  <input
    value={editingItemIds[item.id].due_date || ""}
    onChange={(event) =>
      updateEditingActionField(
        item.id,
        "due_date",
        event.target.value
      )
    }
    placeholder="Not specified"
    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none placeholder:text-slate-600 focus:border-slate-500"
  />
</div>


<div>
  <label className="mb-2 block text-xs font-medium uppercase tracking-wide text-slate-500">
    Type
  </label>

  <select
    value={
      editingItemIds[item.id].type ||
      "committed"
    }
    onChange={(event) =>
      updateEditingActionField(
        item.id,
        "type",
        event.target.value
      )
    }
    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-200 outline-none focus:border-slate-500"
  >
    <option value="committed">
      Committed
    </option>

    <option value="possible">
      Possible
    </option>
  </select>
</div>

</div>


                        <div className="flex flex-wrap items-center gap-3 pt-2">

                          <button
                            onClick={() => saveEditActionItem(item.id)}
                            disabled={savingItemIds[item.id]}
                            className="meeting-save-button rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:opacity-50"
                          >
                            {savingItemIds[item.id] ? "Saving..." : "Save changes"}
                          </button>

                          <button
                            onClick={() => cancelEditActionItem(item.id)}
                            disabled={savingItemIds[item.id]}
                            className="meeting-action-button rounded-lg border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900 disabled:opacity-50"
                          >
                            Cancel
                          </button>

                          <span className="text-xs text-slate-500">
                            Item will remain pending review until explicitly confirmed.
                          </span>

                        </div>

                      </div>

                    ) : (

                      /* ================================================= */
                      /* NORMAL VIEW MODE */
                      /* ================================================= */

                      <>

                        <div className="flex items-start justify-between gap-6">

                          <h3 className="text-lg font-semibold leading-7 text-white">
                            {item.task}
                          </h3>


                          {/* STATUS */}

                          <span
                            className={`
                              shrink-0 rounded-full px-4 py-2 text-sm font-medium
                              ${
                                item.status === "confirmed"
                                  ? "bg-emerald-500/15 text-emerald-400"
                                  : item.status === "dismissed"
                                  ? "meeting-dismissed-status bg-slate-500 text-white"
                                  : "meeting-pending-status bg-amber-100 text-amber-800"
                              }
                            `}
                          >
                            {item.status === "confirmed"
                              ? "Confirmed"
                              : item.status === "dismissed"
                              ? "Dismissed"
                              : "Pending"}
                          </span>

                        </div>


                        {/* METADATA */}

                        <div className="mt-5 flex flex-wrap gap-x-8 gap-y-2 text-sm text-slate-500">

                          <span>
                            Owner:{" "}
                            <span className="text-slate-300">
                              {item.owner || "Unassigned"}
                            </span>
                          </span>

                          <span>
                Email:{" "}
                <span className="text-slate-300">
                  {item.owner_email || "Not specified"}
                </span>
              </span>


                          <span>
                            Due:{" "}
                            <span className="text-slate-300">
                              {item.due_date || "Not specified"}
                            </span>
                          </span>


                          {item.source_timestamp && (

                            <span>
                              Source:{" "}
                              <span className="text-slate-400">
                                {item.source_timestamp}
                              </span>
                            </span>

                          )}

                          {item.type && (

                            <span>
                              Type:{" "}
                              <span className="text-slate-400 capitalize">
                                {item.type}
                              </span>
                            </span>

                          )}

                          {item.human_modified === 1 && (

                            <span className="rounded bg-indigo-500/10 px-2 py-0.5 text-xs text-indigo-400">
                              Edited by human
                            </span>

                          )}

                        </div>


                        {/* DIVIDER */}

                        <div className="my-5 border-t border-slate-800" />


                        {/* SOURCE */}

                        <Link
                          to={`/meetings/${meeting.id}`}
                          className="inline-flex items-center text-sm text-slate-500 transition hover:text-slate-300"
                        >
                          From {meeting.filename} →
                        </Link>


                        {/* ACTION BUTTONS */}

                        <div className="mt-6 flex flex-wrap gap-3">

                          {isLead && item.status === "pending_review" && (

                            <>

                              <button
                                onClick={() => startEditActionItem(item)}
                                className="meeting-action-button rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900"
                              >
                                Edit
                              </button>

                              <button
                                onClick={() =>
                                  handleAction(
                                    "confirm",
                                    item.id
                                  )
                                }
                                disabled={
                                  actionLoading === item.id
                                }
                                className="meeting-confirm-button rounded-lg bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                {actionLoading === item.id
                                  ? "..."
                                  : "Confirm"}
                              </button>


                              <button
                                onClick={() =>
                                  handleAction(
                                    "dismiss",
                                    item.id
                                  )
                                }
                                disabled={
                                  actionLoading === item.id
                                }
                                className="meeting-action-button rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                Dismiss
                              </button>

                            </>

                          )}


                          {isLead && (item.status === "confirmed" ||
                            item.status === "dismissed") && (

                            <>

                              <button
                                onClick={() => startEditActionItem(item)}
                                className="meeting-action-button rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900"
                              >
                                Edit
                              </button>

                              <button
                                onClick={() =>
                                  handleAction(
                                    "reopen",
                                    item.id
                                  )
                                }
                                disabled={
                                  actionLoading === item.id
                                }
                                className="meeting-action-button rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-800 transition hover:border-slate-400 hover:bg-slate-100 hover:text-slate-900 disabled:cursor-not-allowed disabled:opacity-50"
                              >
                                Reopen
                              </button>

                            </>

                          )}

                        </div>

                      </>

                    )}

                  </div>

                ))

              ) : (

                <div className="rounded-2xl border border-dashed border-slate-800 px-6 py-12 text-center">

                  <p className="text-sm text-slate-500">
                    No action items found.
                  </p>

                </div>

              )}

            </div>

          </section>

        )}


        {/* ==================================================== */}
        {/* DECISIONS */}
        {/* ==================================================== */}

        {activeTab === "decisions" && (

          <section className="overflow-hidden rounded-xl border border-slate-800 bg-slate-900/60">

            <div className="border-b border-slate-800 px-6 py-5">

              <h2 className="text-lg font-semibold text-white">
                Decisions
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Agreements and decisions captured from the meeting.
              </p>

            </div>


            <div className="divide-y divide-slate-800">

              {decisions.length >
              0 ? (

                decisions.map(
                  (decision) => (

                    <div
                      key={decision.id}
                      className="px-6 py-6"
                    >

                      {editing ? (

                        <div>

                          <label className="mb-2 block text-xs font-medium text-slate-500">
                            Decision
                          </label>

                          <textarea
                            value={
                              decision.decision ||
                              ""
                            }
                            onChange={(
                              event
                            ) =>
                              updateDecisionField(
                                decision.id,
                                event
                                  .target
                                  .value
                              )
                            }
                            rows={3}
                            className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm leading-6 text-slate-200 outline-none placeholder:text-slate-600 focus:border-slate-500"
                            placeholder="Enter decision..."
                          />

                          {decision.source_timestamp && (
                            <p className="mt-2 text-xs text-slate-600">
                              Source:{" "}
                              {
                                decision.source_timestamp
                              }
                            </p>
                          )}

                        </div>

                      ) : (

                        <>

                          <p className="text-sm leading-6 text-slate-300">
                            {
                              decision.decision
                            }
                          </p>

                          {decision.source_timestamp && (
                            <p className="mt-3 text-xs text-slate-600">
                              Source:{" "}
                              {
                                decision.source_timestamp
                              }
                            </p>
                          )}

                        </>

                      )}

                    </div>

                  )
                )

              ) : (

                <div className="px-6 py-10 text-center text-sm text-slate-500">
                  No decisions found.
                </div>

              )}

            </div>

          </section>

        )}


        {/* ==================================================== */}
        {/* RISKS */}
        {/* ==================================================== */}

        {activeTab === "risks" && (

          <section>

            <div className="mb-6">

              <h2 className="text-lg font-semibold text-white">
                Risks & blockers
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Issues identified during the meeting that may affect delivery, reliability, or implementation.
              </p>

            </div>


            <div className="space-y-5">

              {meeting.risks?.length > 0 ? (

                meeting.risks.map((risk) => (

                  <div
                    key={risk.id}
                    className="rounded-2xl border border-slate-800 bg-slate-900/80 px-6 py-6"
                  >

                    <div className="flex items-start justify-between gap-6">

                      <div className="min-w-0">

                        <h3 className="text-lg font-semibold leading-7 text-white">
                          {risk.risk}
                        </h3>

                        <div className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-sm text-slate-500">

                          {risk.source_timestamp && (

                            <span>
                              Source:{" "}
                              <span className="text-slate-400">
                                {risk.source_timestamp}
                              </span>
                            </span>

                          )}

                        </div>

                      </div>



                    </div>

                  </div>

                ))

              ) : (

                <div className="rounded-2xl border border-dashed border-slate-800 px-6 py-12 text-center">

                  <p className="text-sm text-slate-500">
                    No risks or blockers found.
                  </p>

                </div>

              )}

            </div>

          </section>

        )}

      </main>

    </div>
  )
}


// ============================================================
// TIMESTAMP FORMATTER
// ============================================================

function formatTimestamp(
  seconds
) {
  const totalSeconds =
    Math.floor(
      seconds || 0
    )

  const minutes =
    Math.floor(
      totalSeconds / 60
    )

  const remainingSeconds =
    totalSeconds % 60

  return `${String(
    minutes
  ).padStart(2, "0")}:${String(
    remainingSeconds
  ).padStart(2, "0")}`
}


export default MeetingIntelligence