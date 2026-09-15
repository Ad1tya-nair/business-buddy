import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { useAuth } from "../context/AuthContext"

const DEMO_ACCOUNTS = [
  { username: "lead", role: "Team Lead", badge: "Lead" },
  { username: "priya", role: "Member", badge: "Member" },
  { username: "simon", role: "Member", badge: "Member" },
  { username: "mathew", role: "Member", badge: "Member" },
  { username: "joseph", role: "Member", badge: "Member" },
]

export default function Login() {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  async function handleLogin(userVal, passVal) {
    const u = userVal !== undefined ? userVal : username
    const p = passVal !== undefined ? passVal : password

    if (!u.trim() || !p.trim()) {
      setError("Please enter both username and password.")
      return
    }

    try {
      setSubmitting(true)
      setError(null)
      await login(u.trim().toLowerCase(), p.trim())
      navigate("/")
    } catch (err) {
      setError(err.message || "Login failed. Check your credentials.")
    } finally {
      setSubmitting(false)
    }
  }

  function handleQuickLogin(account) {
    setUsername(account.username)
    setPassword(account.username)
    handleLogin(account.username, account.username)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-slate-300 bg-white p-8 shadow-xl shadow-slate-200/70">
        {/* Brand */}
        <div className="text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl border border-teal-700/30 bg-teal-600 text-2xl font-bold text-white shadow-lg shadow-teal-600/20">
            AI
          </div>
          <h2 className="mt-5 text-2xl font-bold tracking-tight text-slate-900">
            Meeting Intelligence Companion
          </h2>
          <p className="mt-2 text-sm text-slate-500">
            Sign in to access your meetings and tasks
          </p>
        </div>

        {/* Quick Login Chips for Demo */}
        <div className="rounded-xl border border-slate-300 bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Quick Demo Accounts (1-Click Login)
          </p>
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3">
            {DEMO_ACCOUNTS.map((acc) => (
              <button
                key={acc.username}
                type="button"
                onClick={() => handleQuickLogin(acc)}
                className="flex flex-col items-center justify-center rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-center transition hover:border-teal-400 hover:bg-teal-50"
              >
                <span className="text-xs font-semibold capitalize text-slate-800">
                  {acc.username}
                </span>
                <span
                  className={`mt-0.5 text-[10px] font-medium ${
                    acc.badge === "Lead" ? "text-teal-700" : "text-emerald-700"
                  }`}
                >
                  {acc.badge}
                </span>
              </button>
            ))}
          </div>
          <p className="mt-2 text-center text-[11px] text-slate-500">
            Password is the same as username (e.g. priya / priya)
          </p>
        </div>

        {/* Error Notification */}
        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-3.5 text-xs text-red-700">
            {error}
          </div>
        )}

        {/* Form */}
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleLogin()
          }}
          className="space-y-4"
        >
          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-slate-500">
              Username
            </label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g. lead, priya, simon..."
              className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium uppercase tracking-wider text-slate-500">
              Password
            </label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="mt-1.5 w-full rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-xl border border-teal-700 bg-teal-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-teal-600/20 transition hover:bg-teal-700 disabled:opacity-50"
          >
            {submitting ? "Signing in..." : "Sign In"}
          </button>
        </form>
      </div>
    </div>
  )
}
