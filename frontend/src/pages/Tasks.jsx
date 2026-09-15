import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { useAuth } from "../context/AuthContext"
import { getTasks, getUsers, toggleTaskComplete } from "../services/api"

const memberNames = ["Priya", "Simon", "Mathew", "Joseph"]

function Tasks() {
  const { user, isLead } = useAuth()
  const [tasks, setTasks] = useState([])
  const [view, setView] = useState(isLead ? "all" : "mine")
  const [memberFilter, setMemberFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updatingId, setUpdatingId] = useState(null)

  useEffect(() => {
    async function loadTasks() {
      try {
        setLoading(true)
        const owner = !isLead && view === "mine" ? user?.name : null
        const data = await getTasks(null, owner)
        setTasks(data)
        if (isLead) await getUsers()
        setError(null)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    loadTasks()
  }, [isLead, user?.name, view])

  async function handleComplete(task) {
    try {
      setUpdatingId(task.id)
      const updated = await toggleTaskComplete(task.id, !task.completed)
      setTasks((previous) => previous.map((item) => (
        item.id === task.id
          ? { ...item, ...updated, completed: Boolean(updated.completed) }
          : item
      )))
    } catch (err) {
      setError(err.message)
    } finally {
      setUpdatingId(null)
    }
  }

  const filteredTasks = tasks.filter((task) => {
    const matchesMember = memberFilter === "all"
      || (memberFilter === "unassigned" && !task.owner)
      || task.owner?.toLowerCase() === memberFilter.toLowerCase()
    const matchesStatus = statusFilter === "all"
      || (statusFilter === "completed" && task.completed)
      || (statusFilter !== "completed" && task.status === statusFilter && !task.completed)
    return matchesMember && matchesStatus
  })

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="mt-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
            Execution & Tracking
          </span>
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            Tasks
          </h1>
          <p className="mt-1.5 text-sm text-slate-500">
            {isLead
              ? "Monitor and manage action items across the entire team."
              : "Review and complete the action items assigned to you."}
          </p>
        </div>
      </div>

      {/* Member Tabs: My Tasks vs All Team Tasks */}
      {!isLead && (
        <div className="flex gap-2 border-b border-slate-200 pb-3">
          {[
            { id: "mine", label: "My Tasks" },
            { id: "all", label: "All Team Tasks" },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setView(tab.id)}
              className={`rounded-xl px-4 py-2 text-xs font-semibold transition-all ${
                view === tab.id
                  ? "border border-slate-200/80 bg-white text-slate-900 shadow-xs"
                  : "text-slate-500 hover:bg-slate-100/70 hover:text-slate-800"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3 border-b border-slate-200 pb-4">
        {isLead && (
          <select
            value={memberFilter}
            onChange={(event) => setMemberFilter(event.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 shadow-2xs outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          >
            <option value="all">All members</option>
            {memberNames.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
            <option value="unassigned">Unassigned</option>
          </select>
        )}

        <select
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
          className="rounded-xl border border-slate-200 bg-white px-3.5 py-2 text-xs font-medium text-slate-700 shadow-2xs outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
        >
          <option value="all">All statuses</option>
          <option value="confirmed">Confirmed</option>
          <option value="completed">Completed</option>
          <option value="dismissed">Dismissed</option>
        </select>
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
          Loading tasks...
        </div>
      )}

      {/* Empty */}
      {!loading && !error && filteredTasks.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-xs">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-xl text-slate-500">
            ✓
          </div>
          <h3 className="mt-4 text-base font-semibold text-slate-900">
            No tasks found
          </h3>
          <p className="mt-1 text-sm text-slate-500">
            No tasks match your selected view and status filters.
          </p>
        </div>
      )}

      {/* Tasks List */}
      {!loading && filteredTasks.length > 0 && (
        <div className="space-y-3.5">
          {filteredTasks.map((task) => (
            <div
              key={task.id}
              className="group rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs transition-all hover:border-slate-300 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-6">
                <div className="min-w-0">
                  <p
                    className={`text-base font-semibold leading-6 transition-colors ${
                      task.completed ? "text-slate-400 line-through" : "text-slate-900"
                    }`}
                  >
                    {task.task}
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-slate-500">
                    <span>
                      Owner:{" "}
                      <span className="font-semibold text-slate-800">
                        {task.owner || "Unassigned"}
                      </span>
                    </span>

                    <span>
                      Due:{" "}
                      <span className="font-semibold text-slate-800">
                        {task.due_date || "Not specified"}
                      </span>
                    </span>

                    {isLead && task.owner_email && (
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] text-slate-600">
                        {task.owner_email}
                      </span>
                    )}
                  </div>
                </div>

                <div className="flex shrink-0 items-center gap-2.5">
                  {task.completed ? (
                    <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 shadow-2xs">
                      Completed
                    </span>
                  ) : (
                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold shadow-2xs ${
                        task.status === "confirmed"
                          ? "border border-blue-200 bg-blue-50 text-blue-700"
                          : "border border-slate-200 bg-slate-100 text-slate-600"
                      }`}
                    >
                      {task.status === "confirmed" ? "Confirmed" : task.status}
                    </span>
                  )}

                  {!isLead && task.owner?.toLowerCase() === user?.name?.toLowerCase() && (
                    <button
                      type="button"
                      disabled={updatingId === task.id}
                      onClick={() => handleComplete(task)}
                      className={`rounded-xl border px-3.5 py-1.5 text-xs font-semibold transition-all shadow-2xs ${
                        task.completed
                          ? "border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
                          : "border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 hover:border-emerald-400"
                      } disabled:opacity-50`}
                    >
                      {task.completed ? "Undo" : "Mark complete"}
                    </button>
                  )}
                </div>
              </div>

              <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3.5">
                <Link
                  to={`/meetings/${task.meeting_id}`}
                  className="text-xs font-semibold text-indigo-600 transition hover:text-indigo-700"
                >
                  From {task.filename} →
                </Link>
                {task.completed && task.completed_at && (
                  <span className="text-[11px] text-slate-400">
                    Completed on {task.completed_at}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Tasks
