const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000"


// ============================================================
// REQUEST HELPER
// ============================================================

async function request(
  endpoint,
  options = {}
) {
  const token = localStorage.getItem("token")

  const headers = {
    ...(options.headers || {}),
  }

  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  const response = await fetch(
    `${API_BASE}${endpoint}`,
    {
      ...options,
      headers,
    }
  )

  let data

  try {
    data = await response.json()
  } catch {
    data = null
  }

  if (!response.ok) {
    const message =
      data?.detail ||
      data?.message ||
      `Request failed with status ${response.status}`

    throw new Error(message)
  }

  return data
}


// ============================================================
// AUTHENTICATION & USERS
// ============================================================

export async function loginUser(credentials) {
  return request("/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(credentials),
  })
}


export async function getCurrentUser() {
  const token = localStorage.getItem("token")
  if (!token) return null
  return request("/auth/me")
}


export async function getUsers() {
  return request("/users")
}


// ============================================================
// HEALTH
// ============================================================

export async function getHealth() {
  return request("/health")
}


// ============================================================
// MEETINGS
// ============================================================

export async function analyzeMeeting(
  file
) {
  const formData = new FormData()

  formData.append(
    "file",
    file
  )

  return request(
    "/meetings/analyze",
    {
      method: "POST",
      body: formData,
    }
  )
}


export async function getMeetings() {
  return request("/meetings")
}


export async function getMeeting(
  meetingId
) {
  return request(
    `/meetings/${meetingId}`
  )
}


export async function updateMeeting(
  meetingId,
  data
) {
  return request(
    `/meetings/${meetingId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


export async function deleteMeeting(
  meetingId
) {
  return request(
    `/meetings/${meetingId}`,
    {
      method: "DELETE",
    }
  )
}


// ============================================================
// ACTION ITEMS
// ============================================================

export async function getActionItems() {
  return request(
    "/action-items"
  )
}


export async function createActionItem(data) {
  return request("/action-items", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
}


export async function getActionItem(
  actionItemId
) {
  return request(
    `/action-items/${actionItemId}`
  )
}


export async function confirmActionItem(
  actionItemId
) {
  return request(
    `/action-items/${actionItemId}/confirm`,
    {
      method: "PATCH",
    }
  )
}


export async function dismissActionItem(
  actionItemId
) {
  return request(
    `/action-items/${actionItemId}/dismiss`,
    {
      method: "PATCH",
    }
  )
}


export async function reopenActionItem(
  actionItemId
) {
  return request(
    `/action-items/${actionItemId}/reopen`,
    {
      method: "PATCH",
    }
  )
}


export async function updateActionItem(
  actionItemId,
  data
) {
  return request(
    `/action-items/${actionItemId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


// ============================================================
// REVIEW
// ============================================================

export async function getPendingReview() {
  return request(
    "/review"
  )
}


// ============================================================
// TASKS
// ============================================================

export async function getTasks(status = null, owner = null) {
  const params = new URLSearchParams()
  if (status && status !== "all") {
    params.append("status", status)
  }
  if (owner) {
    params.append("owner", owner)
  }
  const queryString = params.toString() ? `?${params.toString()}` : ""
  return request(`/tasks${queryString}`)
}


export async function toggleTaskComplete(actionItemId, completed = true) {
  return request(`/action-items/${actionItemId}/complete`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ completed }),
  })
}



// ============================================================
// MEETING REQUESTS / CALENDAR
// ============================================================

export async function getCalendar() {
  return request(
    "/calendar"
  )
}


export async function updateMeetingRequest(
  requestId,
  data
) {
  return request(
    `/meeting-requests/${requestId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


export async function confirmMeetingRequest(
  requestId
) {
  return request(
    `/meeting-requests/${requestId}/confirm`,
    {
      method: "PATCH",
    }
  )
}


export async function dismissMeetingRequest(
  requestId
) {
  return request(
    `/meeting-requests/${requestId}/dismiss`,
    {
      method: "PATCH",
    }
  )
}


// ============================================================
// MANUAL CALENDAR EVENTS
// ============================================================

export async function createCalendarEvent(
  data
) {
  return request(
    "/calendar/events",
    {
      method: "POST",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


export async function updateCalendarEvent(
  eventId,
  data
) {
  return request(
    `/calendar/events/${eventId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


export async function deleteCalendarEvent(
  eventId
) {
  return request(
    `/calendar/events/${eventId}`,
    {
      method: "DELETE",
    }
  )
}


// ============================================================
// DASHBOARD
// ============================================================

export async function getDashboardStats() {
  return request(
    "/dashboard/stats"
  )
}


// ============================================================
// DECISIONS
// ============================================================

export async function getDecisions() {
  return request(
    "/decisions"
  )
}


export async function updateDecision(
  decisionId,
  data
) {
  return request(
    `/decisions/${decisionId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type":
          "application/json",
      },
      body: JSON.stringify(data),
    }
  )
}


// ============================================================
// SEARCH
// ============================================================

export async function searchMeetings(
  query,
  topK = 5
) {
  const params =
    new URLSearchParams({
      q: query,
      top_k: String(topK),
    })

  return request(
    `/search?${params.toString()}`
  )
}


// ============================================================
// ASK / RAG
// ============================================================

export async function askMeetingKnowledge(
  query,
  topK = 5
) {
  const params =
    new URLSearchParams({
      q: query,
      top_k: String(topK),
    })

  return request(
    `/ask?${params.toString()}`
  )
}
export async function askQuestion(
  query,
  topK = 5
) {
  const params =
    new URLSearchParams({
      q: query,
      top_k: String(topK),
    })

  return request(
    `/ask?${params.toString()}`
  )
}