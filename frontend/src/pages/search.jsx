import { useState } from "react"
import { Link } from "react-router-dom"
import { askQuestion } from "../services/api"

export default function Search() {
  const [query, setQuery] = useState("")
  const [answer, setAnswer] = useState("")
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")

  async function handleSearch(event) {
    event.preventDefault()

    if (!query.trim()) return

    setLoading(true)
    setError("")
    setAnswer("")
    setSources([])

    try {
      const data = await askQuestion(query.trim())

      setAnswer(data.answer || "")
      setSources(data.sources || [])
    } catch (error) {
      setError(error.message || "Failed to get an answer")
    } finally {
      setLoading(false)
    }
  }

  function handleExample(example) {
    setQuery(example)
  }

  return (
    <div className="space-y-8">

      {/* Header */}
      <div>
        <span className="text-xs font-semibold uppercase tracking-wider text-indigo-600">
          Knowledge Retrieval
        </span>
        <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
          Search
        </h1>
        <p className="mt-1.5 text-sm text-slate-500">
          Ask questions across your meeting history using natural language RAG search.
        </p>
      </div>

      {/* Search box */}
      <form onSubmit={handleSearch} className="flex max-w-4xl gap-3">
        <input
          type="text"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Ask something about your meetings..."
          disabled={loading}
          className="flex-1 rounded-2xl border border-slate-200 bg-white px-5 py-3.5 text-sm text-slate-900 shadow-xs outline-none transition placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={loading || !query.trim()}
          className="rounded-2xl bg-indigo-600 px-6 py-3 text-xs font-semibold text-white shadow-xs transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>


      {/* Error */}
      {error && (
        <div className="max-w-4xl rounded-2xl border border-red-200 bg-red-50/80 p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="max-w-4xl rounded-2xl border border-slate-200/80 bg-white p-6 shadow-xs">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 animate-pulse rounded-full bg-indigo-500" />
            <p className="text-sm font-medium text-slate-600">
              Searching meeting knowledge and generating an answer...
            </p>
          </div>
        </div>
      )}

      {/* Answer */}
      {answer && !loading && (
        <div className="max-w-4xl space-y-6">

          <section className="rounded-2xl border border-slate-200/90 bg-white p-6 shadow-xs">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-sm font-bold text-slate-900">
                Answer
              </h2>
              <span className="rounded-lg border border-indigo-100 bg-indigo-50 px-2.5 py-1 text-xs font-semibold text-indigo-700">
                AI · meeting evidence
              </span>
            </div>

            <div className="text-sm leading-7 text-slate-700 whitespace-pre-line">
              {answer}
            </div>
          </section>

          {/* Sources */}
          {sources.length > 0 && (
            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold text-slate-900">
                    Sources
                  </h2>
                  <p className="mt-0.5 text-xs text-slate-500">
                    Supporting transcript evidence used to generate the answer.
                  </p>
                </div>

                <span className="rounded-full border border-slate-200 bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600">
                  {sources.length} source{sources.length !== 1 ? "s" : ""}
                </span>
              </div>

              <div className="space-y-3">
                {sources.map((source, index) => (
                  <Link
                    key={`${source.meeting_id}-${source.start_time}-${index}`}
                    to={`/meetings/${source.meeting_id}`}
                    className="group block rounded-2xl border border-slate-200/80 bg-white p-5 shadow-xs transition-all hover:border-slate-300 hover:shadow-md"
                  >
                    {/* Source header */}
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-semibold text-slate-900 transition-colors group-hover:text-indigo-600">
                          Meeting source
                        </p>
                        <p className="mt-0.5 text-xs text-slate-400 font-medium">
                          {source.start_time.toFixed(2)}s –{" "}
                          {source.end_time.toFixed(2)}s
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-semibold text-slate-600">
                          {(source.score * 100).toFixed(1)}% relevance
                        </span>
                        <span className="text-xs font-semibold text-indigo-600 transition-transform group-hover:translate-x-0.5">
                          →
                        </span>
                      </div>
                    </div>

                    {/* Evidence */}
                    <div className="mt-4 rounded-xl border border-slate-100 bg-slate-50/70 p-4">
                      <p className="text-sm leading-6 text-slate-700">
                        {source.text}
                      </p>
                    </div>

                    <p className="mt-3 text-xs font-semibold text-indigo-600 transition group-hover:text-indigo-700">
                      Open meeting intelligence →
                    </p>
                  </Link>
                ))}
              </div>
            </section>
          )}

        </div>
      )}
    </div>
  )
}