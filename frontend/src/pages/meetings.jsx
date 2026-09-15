import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { getMeetings } from "../services/api"

function Meetings() {
  const [meetings, setMeetings] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function loadMeetings() {
      try {
        const data = await getMeetings()
        setMeetings(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadMeetings()
  }, [])

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
          Meeting Library
        </span>

        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
          Meetings
        </h1>

        <p className="mt-1.5 text-sm text-slate-500">
          Browse analyzed meetings, review transcripts, and inspect extracted intelligence.
        </p>
      </div>


      {/* Loading */}
      {loading && (
        <div className="rounded-2xl border border-slate-200/80 bg-white p-8 text-center text-sm font-medium text-slate-500 shadow-xs">
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
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-xs">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-xl text-indigo-600">
            ▣
          </div>

          <h2 className="mt-4 text-base font-semibold text-slate-900">
            No meetings yet
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Upload a recording through the Assistant to analyze your first meeting.
          </p>

          <Link
            to="/assistant"
            className="mt-5 inline-flex rounded-xl bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700"
          >
            Analyze a meeting
          </Link>
        </div>
      )}


      {/* Meetings */}
      {!loading && !error && meetings.length > 0 && (
        <section className="space-y-4">
          {meetings.map((meeting) => (
            <Link
              key={meeting.id}
              to={`/meetings/${meeting.id}`}
              className="group block rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs transition-all duration-150 hover:border-slate-300 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-6">
                <div className="min-w-0">
                  <div className="flex items-center gap-3">
                    <h2 className="truncate text-base font-semibold text-slate-900 transition-colors group-hover:text-indigo-600">
                      {meeting.filename}
                    </h2>

                    <span className="shrink-0 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
                      Processed
                    </span>
                  </div>

                  <p className="mt-1 text-xs text-slate-400 font-medium">
                    {meeting.created_at || "Processed meeting"}
                  </p>
                </div>

                <span className="shrink-0 text-sm font-semibold text-indigo-600 transition-transform group-hover:translate-x-1">
                  View →
                </span>
              </div>


              {/* Summary */}
              {meeting.summary?.length > 0 && (
                <div className="mt-4 space-y-1.5 border-t border-slate-100 pt-3">
                  {meeting.summary.slice(0, 3).map((point, index) => (
                    <p
                      key={index}
                      className="text-sm leading-6 text-slate-600 line-clamp-1"
                    >
                      <span className="mr-2 text-slate-400">•</span>
                      {point}
                    </p>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </section>
      )}

    </div>
  )
}

export default Meetings