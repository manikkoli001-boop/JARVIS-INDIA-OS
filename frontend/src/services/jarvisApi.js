const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

export async function fetchCoreModules() {
  const response = await fetch(`${API_BASE}/api/v1/core/modules`)
  if (!response.ok) {
    throw new Error('Failed to fetch core modules')
  }
  return response.json()
}

export async function sendAssistantCommand(command) {
  const response = await fetch(`${API_BASE}/api/v1/core/assistant`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command }),
  })

  if (!response.ok) {
    throw new Error('Failed to execute command')
  }

  return response.json()
}
