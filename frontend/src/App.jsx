import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom"

import { AuthProvider, useAuth } from "./context/AuthContext"
import Sidebar from "./components/layout/Sidebar"

import Login from "./pages/Login"
import Dashboard from "./pages/dashboard"
import MeetingIntelligence from "./pages/MeetingIntelligence"
import Assistant from "./pages/Assistant"
import Meetings from "./pages/Meetings"
import Review from "./pages/review"
import Decisions from "./pages/decisions"
import Search from "./pages/search"
import Tasks from "./pages/Tasks"
import Calendar from "./pages/Calendar"


function ProtectedLayout() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 text-sm font-medium text-slate-500">
        Loading workspace...
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />

      <main className="flex-1 bg-slate-100 min-h-screen text-slate-900">
        <div className="mx-auto max-w-7xl px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assistant" element={<Assistant />} />
            <Route path="/meetings" element={<Meetings />} />
            <Route path="/meetings/:meetingId" element={<MeetingIntelligence />} />
            <Route path="/review" element={<Review />} />
            <Route path="/decisions" element={<Decisions />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/calendar" element={<Calendar />} />
            <Route path="/search" element={<Search />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  )
}


function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/*" element={<ProtectedLayout />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App