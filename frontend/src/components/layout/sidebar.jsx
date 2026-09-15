import { NavLink } from "react-router-dom"
import { useAuth } from "../../context/AuthContext"

const navigation = [
  { name: "Dashboard", path: "/", icon: "⌂" },
  { name: "Assistant", path: "/assistant", icon: "◉" },
  { name: "Meetings", path: "/meetings", icon: "▣" },
  { name: "Tasks", path: "/tasks", icon: "✓" },
  { name: "Calendar", path: "/calendar", icon: "□" },
  { name: "Search", path: "/search", icon: "⌕" },
]

export default function Sidebar() {
  const { user, logout, isLead } = useAuth()

  return (
    <aside
      className={`
        relative
        sticky top-0
        flex h-screen shrink-0 flex-col
        overflow-hidden
        border-r border-slate-700
        bg-slate-800
        py-5
        w-56 px-3
      `}
    >
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-teal-600 text-3xl font-semibold text-white shadow-sm shadow-teal-600/20">
          AI
        </div>

        <div>
          <h1 className="whitespace-nowrap text-lg font-semibold text-white">
            Briefly
          </h1>

          <p className="text-sm text-slate-400">
            Meeting Copilot
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="mt-8 flex flex-col gap-2">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) => `
              flex h-12 w-full items-center gap-4 px-4
              rounded-xl
              transition-colors
              ${
                isActive
                  ? "bg-teal-600 text-white font-semibold shadow-xs shadow-teal-950/20"
                  : "text-slate-300 hover:bg-slate-700 hover:text-white"
              }
            `}
          >
            <span className="w-6 shrink-0 text-center text-xl">
              {item.icon}
            </span>

            <span className="text-base">
              {item.name}
            </span>
          </NavLink>
        ))}
      </nav>

      {/* User Profile & Sign Out Footer */}
      {user && (
        <div className="mt-4 border-t border-slate-700 pt-4">
          <div className="flex items-center justify-between rounded-xl bg-slate-700/70 p-3">
              <div className="flex items-center gap-3 overflow-hidden">
                <div
                  className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-lg font-bold text-white uppercase ${
                    isLead ? "bg-teal-600" : "bg-emerald-600"
                  }`}
                >
                  {user.name ? user.name.charAt(0) : "U"}
                </div>
                <div className="min-w-0">
                  <p className="truncate text-xs font-semibold text-white">
                    {user.name || user.username}
                  </p>
                  <p
                    className={`text-[10px] font-medium uppercase tracking-wider ${
                      isLead ? "text-teal-300" : "text-emerald-300"
                    }`}
                  >
                    {isLead ? "Team Lead" : "Member"}
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={logout}
                title="Sign Out"
                className="shrink-0 rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-600 hover:text-red-300"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                  <polyline points="16 17 21 12 16 7" />
                  <line x1="21" y1="12" x2="9" y2="12" />
                </svg>
              </button>
          </div>
        </div>
      )}

    </aside>
  )
}
