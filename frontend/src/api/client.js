const API_BASE_URL = (
  import.meta.env.VITE_API_URL || "http://localhost:8000"
).replace(/\/$/, "")

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.payload = payload
  }
}

async function request(path, { method = "GET", body, signal } = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      signal,
      headers: body ? { "Content-Type": "application/json" } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
  } catch (error) {
    if (error.name === "AbortError") throw error
    throw new ApiError("Não foi possível conectar à API.", 0, null)
  }

  const text = await response.text()
  let payload = null

  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = text
    }
  }

  if (!response.ok) {
    const detail = payload?.detail
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).filter(Boolean).join(" ") || "Os dados enviados são inválidos."
      : detail || payload?.Status || `A API respondeu com ${response.status}.`
    throw new ApiError(message, response.status, payload)
  }

  return payload
}

export function getDaysByMonth(year, month, signal) {
  const params = new URLSearchParams({ ano: year, mes: month })
  return request(`/dias?${params}`, { signal })
}

export async function getDay(date, signal) {
  try {
    return await request(`/dias/${date}`, { signal })
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null
    throw error
  }
}

export function createDay(day) {
  return request("/dias", { method: "POST", body: day })
}

export function removeDay(date) {
  return request(`/dias/${date}`, { method: "DELETE" })
}

export function createTask(task) {
  return request("/tarefas", { method: "POST", body: task })
}

export function updateTask(taskId, completed) {
  return request(`/tarefas/${taskId}`, {
    method: "PATCH",
    body: { cumprida: completed ? 1 : 0 },
  })
}

export function removeTask(taskId) {
  return request(`/tarefas/${taskId}`, { method: "DELETE" })
}

export function getApiErrorMessage(error) {
  if (error instanceof ApiError) return error.message
  return "Ocorreu um erro inesperado. Tente novamente."
}
