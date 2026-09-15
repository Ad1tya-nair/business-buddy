import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import {
  getMeetings,
  getDashboardStats,
} from "../services/api"


function Dashboard() {
  const [meetings, setMeetings] = useState([])

  const [stats, setStats] = useState({
    meetings: 0,
    pending_review: 0,
    decisions: 0,
    confirmed_tasks: 0,
  })

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)


  useEffect(() => {
    async function loadDashboard() {
      try {
        const [
          meetingsData,
          statsData,
        ] = await Promise.all([
          getMeetings(),
          getDashboardStats(),
        ])

        setMeetings(meetingsData)
        setStats(statsData)

      } catch (err) {
        setError(err.message)

      } finally {
        setLoading(false)
      }
    }

    loadDashboard()
  }, [])


  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
          Executive Overview
        </span>

        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
          Welcome back
        </h1>

        <p className="mt-1.5 text-sm text-slate-500">
          Here is what needs your review and follow-through today.
        </p>
      </div>


      {/* Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">

        {/* Meetings */}
        <Link
          to="/meetings"
          className="group rounded-2xl border border-slate-300/80 bg-white p-6 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-indigo-300 hover:shadow-md"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Meetings
              </p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {stats.meetings}
              </p>
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 transition group-hover:bg-indigo-600 group-hover:text-white">
              ▣
            </div>
          </div>
          <p className="mt-4 flex items-center text-xs font-semibold text-indigo-600">
            View all meetings <span className="ml-1 transition-transform group-hover:translate-x-0.5">→</span>
          </p>
        </Link>


        {/* Pending Review */}
        <Link
          to="/review"
          className="group rounded-2xl border border-slate-300/80 bg-white p-6 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-amber-300 hover:shadow-md"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Pending Review
              </p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {stats.pending_review}
              </p>
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-amber-50 text-amber-600 transition group-hover:bg-amber-500 group-hover:text-white">
              ◉
            </div>
          </div>
          <p className="mt-4 flex items-center text-xs font-semibold text-amber-600">
            Review detected items <span className="ml-1 transition-transform group-hover:translate-x-0.5">→</span>
          </p>
        </Link>


        {/* Confirmed Tasks */}
        <Link
          to="/tasks"
          className="group rounded-2xl border border-slate-300/80 bg-white p-6 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Confirmed Tasks
              </p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {stats.confirmed_tasks || 0}
              </p>
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600 transition group-hover:bg-emerald-600 group-hover:text-white">
              ✓
            </div>
          </div>
          <p className="mt-4 flex items-center text-xs font-semibold text-emerald-600">
            View active tasks <span className="ml-1 transition-transform group-hover:translate-x-0.5">→</span>
          </p>
        </Link>


        {/* Decisions */}
        <Link
          to="/decisions"
          className="group rounded-2xl border border-slate-300/80 bg-white p-6 shadow-xs transition-all duration-200 hover:-translate-y-0.5 hover:border-purple-300 hover:shadow-md"
        >
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Decisions
              </p>
              <p className="mt-2 text-3xl font-bold text-slate-900">
                {stats.decisions}
              </p>
            </div>
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-purple-50 text-purple-600 transition group-hover:bg-purple-600 group-hover:text-white">
              ⚖
            </div>
          </div>
          <p className="mt-4 flex items-center text-xs font-semibold text-purple-600">
            View captured decisions <span className="ml-1 transition-transform group-hover:translate-x-0.5">→</span>
          </p>
        </Link>

      </div>


      {/* Recent Meetings */}
      <section className="space-y-4">

        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-slate-900">
              Recent Meetings
            </h2>
            <p className="text-xs text-slate-500">
              Latest recordings processed and summarized by AI
            </p>
          </div>

          <Link
            to="/meetings"
            className="text-xs font-semibold text-indigo-600 transition hover:text-indigo-700"
          >
            View all meetings →
          </Link>
        </div>


        {/* Loading */}
        {loading && (
          <div className="rounded-2xl border border-slate-300/70 bg-white p-8 text-center text-sm font-medium text-slate-500 shadow-xs">
            Loading meetings...
          </div>
        )}


        {/* Error */}
        {error && (
          <div className="rounded-2xl border border-red-200 bg-red-50/80 p-5 text-sm text-red-700">
            {error}
          </div>
        )}


        {/* Empty */}
        {!loading && !error && meetings.length === 0 && (
          <div className="rounded-2xl border border-dashed border-slate-400/80 bg-white p-12 text-center shadow-xs">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">
              ▣
            </div>
            <h3 className="mt-4 text-base font-semibold text-slate-900">
              No meetings analyzed yet
            </h3>
            <p className="mt-1 text-sm text-slate-500">
              Upload or record a meeting audio file to generate intelligence.
            </p>
            <Link
              to="/assistant"
              className="mt-5 inline-flex items-center rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700"
            >
              Analyze your first meeting →
            </Link>
          </div>
        )}


        {/* Meetings List */}
        {!loading && !error && meetings.length > 0 && (
          <div className="space-y-3">
            {meetings.slice(0, 5).map((meeting) => (
              <Link
                key={meeting.id}
                to={`/meetings/${meeting.id}`}
                className="group block rounded-2xl border border-slate-300/80 bg-white p-5 shadow-xs transition-all duration-150 hover:border-slate-400 hover:shadow-md"
              >
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="text-base font-semibold text-slate-900 transition-colors group-hover:text-indigo-600">
                      {meeting.filename}
                    </h3>
                    <p className="mt-0.5 text-xs text-slate-400 font-medium">
                      Meeting #{meeting.id}
                    </p>
                  </div>

                  <span className="shrink-0 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                    Processed
                  </span>
                </div>

                {meeting.summary?.length > 0 && (
                  <div className="mt-3 space-y-1.5 border-t border-slate-100 pt-3">
                    {meeting.summary.slice(0, 3).map((point, index) => (
                      <p key={index} className="text-sm text-slate-600 line-clamp-1">
                        • {point}
                      </p>
                    ))}
                  </div>
                )}

                <div className="mt-3 flex items-center text-xs font-semibold text-indigo-600">
                  <span>View meeting intelligence</span>
                  <span className="ml-1 transition-transform group-hover:translate-x-1">→</span>
                </div>
              </Link>
            ))}
          </div>
        )}

      </section>

    </div>
  )
}

export default Dashboard