import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import {
  getPendingReview,
  confirmActionItem,
  dismissActionItem,
  updateActionItem,
} from "../services/api"


function Review() {
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const [actionLoading, setActionLoading] = useState(null)
  const [editingId, setEditingId] = useState(null)

  const [editForm, setEditForm] = useState({
    task: "",
    owner: "",
    due_date: "",
  })


  async function loadReview() {
    try {
      setLoading(true)
      setError(null)

      const data = await getPendingReview()

      console.log("Pending review:", data)

      setItems(Array.isArray(data) ? data : [])

    } catch (err) {
      console.error("Review loading error:", err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }


  useEffect(() => {
    loadReview()
  }, [])


  function startEditing(item) {
    setEditingId(item.id)

    setEditForm({
      task: item.task || "",
      owner: item.owner || "",
      due_date: item.due_date || "",
    })
  }


  function cancelEditing() {
    setEditingId(null)

    setEditForm({
      task: "",
      owner: "",
      due_date: "",
    })
  }


  function handleEditChange(event) {
    const { name, value } = event.target

    setEditForm((current) => ({
      ...current,
      [name]: value,
    }))
  }


  async function handleSaveEdit(id) {
    if (!editForm.task.trim()) {
      setError("Task cannot be empty.")
      return
    }

    try {
      setActionLoading(id)
      setError(null)

      const updated = await updateActionItem(id, {
        task: editForm.task.trim(),
        owner: editForm.owner.trim() || null,
        due_date: editForm.due_date.trim() || null,
      })

      setItems((current) =>
        current.map((item) =>
          item.id === id
            ? {
                ...item,
                ...updated,
              }
            : item
        )
      )

      cancelEditing()

    } catch (err) {
      console.error("Action item update error:", err)
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }


  async function handleConfirm(id) {
    try {
      setActionLoading(id)
      setError(null)

      await confirmActionItem(id)

      setItems((current) =>
        current.filter((item) => item.id !== id)
      )

    } catch (err) {
      console.error("Action item confirmation error:", err)
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }


  async function handleDismiss(id) {
    try {
      setActionLoading(id)
      setError(null)

      await dismissActionItem(id)

      setItems((current) =>
        current.filter((item) => item.id !== id)
      )

    } catch (err) {
      console.error("Action item dismissal error:", err)
      setError(err.message)
    } finally {
      setActionLoading(null)
    }
  }


  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <Link
          to="/"
          className="text-xs font-semibold text-slate-500 transition hover:text-indigo-600"
        >
          Back to Dashboard
        </Link>

        <div className="mt-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
            Review Queue
          </span>

          <div className="mt-1 flex items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              Pending Review
            </h1>

            {!loading && items.length > 0 && (
              <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-xs font-bold text-amber-700 shadow-2xs">
                {items.length}
              </span>
            )}
          </div>

          <p className="mt-1.5 text-sm text-slate-500">
            Confirm or dismiss AI-detected action items before they become active tasks.
          </p>
        </div>
      </div>


      {/* Error */}
      {error && (
        <div className="rounded-2xl border border-red-200 bg-red-50/80 p-5 text-sm text-red-700">
          {error}
        </div>
      )}


      {/* Loading */}
      {loading && (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-8 text-center text-sm font-medium text-slate-500 shadow-xs">
          Loading review items...
        </div>
      )}


      {/* Empty state */}

      {!loading && !error && items.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-xs">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-emerald-50 text-xl text-emerald-600">
            Done
          </div>

          <h2 className="mt-4 text-base font-semibold text-slate-900">
            Nothing needs review
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            All detected action items have been reviewed.
          </p>
        </div>
      )}


      {/* Review items */}
      {!loading && items.length > 0 && (
        <div className="space-y-4">
          {items.map((item) => {
            const isEditing = editingId === item.id
            const isLoading = actionLoading === item.id

            return (
              <div
                key={item.id}
                className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs"
              >
                {/* Top row */}
                <div className="flex items-start justify-between gap-6">
                  <div className="min-w-0 flex-1">
                    {!isEditing ? (
                      <p className="text-lg font-bold leading-snug text-slate-950">
                        {item.task}
                      </p>
                    ) : (
                      <input
                        type="text"
                        name="task"
                        value={editForm.task}
                        onChange={handleEditChange}
                        className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                        placeholder="Action item"
                      />
                    )}

                    <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
                      {!isEditing ? (
                        <>
                          <span>
                            Owner:{" "}
                            <span className="font-semibold text-slate-800">
                              {item.owner || "Unassigned"}
                            </span>
                          </span>
                          <span>
                            Due:{" "}
                            <span className="font-semibold text-slate-800">
                              {item.due_date || "Not specified"}
                            </span>
                          </span>
                        </>
                      ) : (
                        <>
                          <input
                            type="text"
                            name="owner"
                            value={editForm.owner}
                            onChange={handleEditChange}
                            className="rounded-xl border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-700 outline-none focus:border-indigo-500"
                            placeholder="Owner"
                          />
                          <input
                            type="text"
                            name="due_date"
                            value={editForm.due_date}
                            onChange={handleEditChange}
                            className="rounded-xl border border-slate-300 bg-white px-2.5 py-1.5 text-xs text-slate-700 outline-none focus:border-indigo-500"
                            placeholder="Due date"
                          />
                        </>
                      )}

                      {item.source_timestamp && (
                        <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] text-slate-600">
                          {item.source_timestamp}
                        </span>
                      )}
                    </div>
                  </div>


                  {/* Status badges */}
                  <div className="flex shrink-0 flex-col items-end gap-2">
                    <span className="rounded-full border border-amber-200 bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-700 shadow-2xs">
                      Pending review
                    </span>

                  </div>
                </div>


                {/* Evidence */}
                <div className="mt-4 rounded-xl border border-slate-100 bg-slate-50/70 p-4">
                  <div className="flex items-center justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Source evidence
                      </p>
                      <p className="mt-0.5 text-sm text-slate-600">
                        Detected at{" "}
                        <span className="font-semibold text-slate-800">
                          {item.source_timestamp || "unknown timestamp"}
                        </span>
                      </p>
                    </div>

                    {item.meeting_id && (
                      <Link
                        to={`/meetings/${item.meeting_id}`}
                        className="shrink-0 text-xs font-semibold text-indigo-600 transition hover:text-indigo-700"
                      >
                        View meeting
                      </Link>
                    )}
                  </div>

                  {item.filename && (
                    <p className="mt-2 text-xs text-slate-400">
                      From {item.filename}
                    </p>
                  )}
                </div>


                {/* Actions */}
                <div className="mt-4 flex flex-wrap gap-2">
                  {!isEditing ? (
                    <>
                      <button
                        onClick={() => handleConfirm(item.id)}
                        disabled={isLoading}
                        className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isLoading ? "Updating..." : "Confirm"}
                      </button>

                      <button
                        onClick={() => startEditing(item)}
                        disabled={isLoading}
                        className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-2xs transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Edit
                      </button>

                      <button
                        onClick={() => handleDismiss(item.id)}
                        disabled={isLoading}
                        className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-500 shadow-2xs transition hover:bg-slate-50 hover:text-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Dismiss
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={() => handleSaveEdit(item.id)}
                        disabled={isLoading}
                        className="rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        {isLoading ? "Saving..." : "Save changes"}
                      </button>

                      <button
                        onClick={cancelEditing}
                        disabled={isLoading}
                        className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-2xs transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
                      >
                        Cancel
                      </button>
                    </>
                  )}
                </div>

              </div>
            )
          })}
        </div>
      )}

    </div>
  )
}

export default Review

