import { useEffect, useState } from 'react'
import { api } from '../api'

export default function AlertCenter() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [threshold, setThreshold] = useState(75)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const loadAlerts = async () => {
    try {
      const data = await api.getAlerts()
      setAlerts(data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  const loadThreshold = async () => {
    try {
      const data = await api.getThreshold()
      setThreshold(data.threshold)
    } catch (e) { console.error(e) }
  }

  useEffect(() => {
    loadThreshold()
    loadAlerts()
    const interval = setInterval(loadAlerts, 10000) // poll every 10s in UI
    return () => clearInterval(interval)
  }, [])

  const saveThreshold = async () => {
    setSaving(true)
    try { await api.setThreshold(threshold) } catch (e) { console.error(e) }
    setSaving(false)
  }

  return (
    <div>
      <div className="panel-title">Alert Center</div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 12 }}>Sentinel Threshold</div>
        <div className="threshold-row">
          <input type="range" min={50} max={95} step={1} value={threshold} onChange={e => setThreshold(Number(e.target.value))} />
          <span style={{ fontSize: 16, fontWeight: 700, color: '#7c6af7', minWidth: 40 }}>{threshold}</span>
          <button onClick={saveThreshold} disabled={saving}>{saving ? 'Saving...' : 'Save'}</button>
        </div>
        <div style={{ fontSize: 12, color: '#64748b' }}>
          Sentinel fires when HAZRA score ≥ {threshold}. Polls every 60s.
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>Alert History ({alerts.length})</div>
        <button className="secondary" onClick={loadAlerts}>Refresh</button>
      </div>

      {loading ? <div className="loading">Loading alerts...</div> : (
        alerts.length === 0 ? (
          <div className="loading">No alerts fired yet.</div>
        ) : (
          alerts.map(a => (
            <div key={a.id} className="alert-item">
              <div className="alert-dot" />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 6, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 13, fontWeight: 600, color: '#f87171' }}>HAZRA {a.hazra_score?.toFixed(1)}</span>
                  <span style={{ fontSize: 12, color: '#64748b' }}>{a.brand} / {a.cluster_id}</span>
                  <span style={{ fontSize: 12, color: a.delta_24h > 0 ? '#34d399' : '#f87171' }}>
                    Δ24h: {a.delta_24h > 0 ? '+' : ''}{a.delta_24h?.toFixed(1)}
                  </span>
                  <span style={{ fontSize: 11, color: '#64748b', marginLeft: 'auto' }}>{a.fired_at?.slice(0, 16).replace('T', ' ')}</span>
                </div>
                <div style={{ fontSize: 13, color: '#94a3b8' }}>{a.recommended_action}</div>
              </div>
            </div>
          ))
        )
      )}
    </div>
  )
}
