import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { api } from '../api'

const COLORS = ['#7c6af7', '#34d399', '#fbbf24', '#f87171', '#60a5fa', '#fb923c']

export default function TrendDetection() {
  const [trends, setTrends] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<any>(null)

  useEffect(() => {
    api.getTrends().then(d => { setTrends(d); setSelected(d[0] || null) }).catch(console.error).finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="loading">Loading trends...</div>

  return (
    <div>
      <div className="panel-title">Trend Detection</div>
      <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 20 }}>
        {trends.map((t, i) => (
          <div key={`${t.brand}-${t.cluster_id}`} className="card"
            style={{ cursor: 'pointer', minWidth: 200, border: selected?.cluster_id === t.cluster_id && selected?.brand === t.brand ? '1px solid #7c6af7' : undefined }}
            onClick={() => setSelected(t)}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 6 }}>{t.cluster_label}</div>
            <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8 }}>{t.brand}</div>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <span className={`badge badge-${t.trend}`}>{t.trend}</span>
              <span style={{ fontSize: 13, color: t.momentum_score > 0 ? '#34d399' : t.momentum_score < 0 ? '#f87171' : '#94a3b8' }}>
                {t.momentum_score > 0 ? '+' : ''}{t.momentum_score}
              </span>
            </div>
          </div>
        ))}
      </div>

      {selected && (
        <div className="card">
          <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>{selected.cluster_label} — {selected.brand}</div>
          <div style={{ fontSize: 13, color: '#64748b', marginBottom: 16 }}>
            Current avg: {selected.current_avg} | Previous avg: {selected.previous_avg} | Momentum: {selected.momentum_score > 0 ? '+' : ''}{selected.momentum_score}
          </div>
          <ResponsiveContainer width="100%" height={220}>
            <LineChart data={selected.daily_scores}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2235" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={d => d.slice(5)} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
              <Tooltip contentStyle={{ background: '#13151f', border: '1px solid #1e2235', borderRadius: 6 }} />
              <Line type="monotone" dataKey="score" stroke="#7c6af7" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
          {selected.signals?.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8 }}>Sample Signals</div>
              {selected.signals.map((s: any, i: number) => (
                <div key={i} style={{ fontSize: 12, color: '#94a3b8', padding: '4px 0', borderBottom: '1px solid #1e2235' }}>
                  <span className="badge badge-stable" style={{ marginRight: 8 }}>{s.type}</span>{s.content}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
