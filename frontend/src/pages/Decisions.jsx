import { useEffect, useState } from "react"
import { Link } from "react-router-dom"
import { getDecisions } from "../services/api"


function Decisions() {
  const [decisions, setDecisions] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)


  useEffect(() => {
    async function loadDecisions() {
      try {
        const data = await getDecisions()

        setDecisions(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadDecisions()
  }, [])


  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <Link
          to="/"
          className="text-xs font-semibold text-slate-500 transition hover:text-indigo-600"
        >
          ← Dashboard
        </Link>

        <div className="mt-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
            Meeting Intelligence
          </span>

          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            Decisions
          </h1>

          <p className="mt-1.5 text-sm text-slate-500">
            Consensus and key architectural or business agreements captured across meetings.
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
          Loading decisions...
        </div>
      )}


      {/* Empty */}
      {!loading && !error && decisions.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center shadow-xs">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-purple-50 text-xl text-purple-600 font-bold">
            ⚖
          </div>

          <h2 className="mt-4 text-base font-semibold text-slate-900">
            No decisions captured yet
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Decisions extracted from analyzed meetings will appear here automatically.
          </p>
        </div>
      )}


      {/* Decisions */}
      {!loading && !error && decisions.length > 0 && (
        <div className="space-y-3.5">
          {decisions.map((decision) => (
            <div
              key={decision.id}
              className="group rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs transition-all hover:border-slate-300 hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-6">
                <div className="min-w-0">
                  <p className="text-base font-semibold leading-relaxed text-slate-900">
                    {decision.decision}
                  </p>

                  <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-2 text-xs text-slate-500">
                    {decision.source_timestamp && (
                      <span className="rounded-md bg-slate-100 px-2 py-0.5 font-mono text-[11px] text-slate-600">
                        {decision.source_timestamp}
                      </span>
                    )}

                    <span>
                      Status:{" "}
                      <span className="font-semibold text-slate-800">
                        {decision.status}
                      </span>
                    </span>
                  </div>
                </div>

                <span className="shrink-0 rounded-full border border-purple-200 bg-purple-50 px-3 py-1 text-xs font-semibold text-purple-700 shadow-2xs">
                  Agreed
                </span>
              </div>

              {/* Source Meeting */}
              <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-3.5">
                <Link
                  to={`/meetings/${decision.meeting_id}`}
                  className="text-xs font-semibold text-indigo-600 transition hover:text-indigo-700"
                >
                  From {decision.filename} →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  )
}

export default Decisions