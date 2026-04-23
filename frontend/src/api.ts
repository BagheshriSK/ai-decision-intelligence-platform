const BASE = '/api'

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`)
  return res.json()
}

export const api = {
  getRankedSignals: (params: Record<string, string | number>) => {
    const q = new URLSearchParams(params as Record<string, string>).toString()
    return req<any[]>(`/signals/ranked?${q}`)
  },
  getTrends: () => req<any[]>('/trends'),
  forecast: (body: object) => req<any>('/forecast', { method: 'POST', body: JSON.stringify(body) }),
  getCompetitive: (params: Record<string, string | number>) => {
    const q = new URLSearchParams(params as Record<string, string>).toString()
    return req<any>(`/competitive?${q}`)
  },
  getAlerts: () => req<any[]>('/alerts'),
  chat: (body: object) => req<any>('/winston/chat', { method: 'POST', body: JSON.stringify(body) }),
  getChatHistory: (sessionId: string) => req<any[]>(`/winston/history/${sessionId}`),
  generateReport: (brand: string) => req<any>(`/reports/generate?brand=${brand}`, { method: 'POST' }),
  getReports: (brand: string) => req<any[]>(`/reports?brand=${brand}`),
  getThreshold: () => req<any>('/config/threshold'),
  setThreshold: (threshold: number) => req<any>('/config/threshold', { method: 'PATCH', body: JSON.stringify({ threshold }) }),
  ingest: (body: object) => req<any>('/ingest', { method: 'POST', body: JSON.stringify(body) }),
}
