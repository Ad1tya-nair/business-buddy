/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState } from "react"
import { loginUser } from "../services/api"

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem("user")
    if (saved && localStorage.getItem("token")) {
      try {
        return JSON.parse(saved)
      } catch {
        return null
      }
    }
    return null
  })
  const loading = false

  async function login(username, password) {
    const data = await loginUser({ username, password })
    if (data && data.user) {
      setUser(data.user)
      localStorage.setItem("user", JSON.stringify(data.user))
      if (data.token) {
        localStorage.setItem("token", data.token)
      }
      return data.user
    }
    throw new Error("Invalid response from server")
  }

  function logout() {
    setUser(null)
    localStorage.removeItem("user")
    localStorage.removeItem("token")
  }

  const isLead = user?.role === "lead"
  const isMember = user?.role === "member"

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
        isLead,
        isMember,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
