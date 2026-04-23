import { useEffect, useState } from 'react'
import { api } from '../api'

const CLUSTERS = ['', 'camera', 'battery', 'overheating', 'price', 'performance', 'general', 'wellness_trends', 'product_sentiment', 'competitor_mentions']
const BRANDS = ['', 'Samsung', 'Apple', 'Google Pixel', 'BrandAlpha', 'BrandBeta', 'BrandGamma']
const TYPES = ['', 'text', 'image', 'video']

export default function SignalFeed() {
  const [signals, setSignals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [cluster, setCluster] = useState('')
  const [brand, setBrand] = useState('Samsung')
  const [type, setType] = useState('')
  const [days, setDays] = useState(30)

  const load = async () => {
    setLoading(true)
    try {
      const params: Record<string, string | number> = { days }
      if (cluster) params.cluster_id = cluster
      if (brand) params.brand = brand
      const data = await api.getRankedSignals(params)
      setSignals(data)
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { load() }, [cluster, brand, days])

  const filtered = type ? signals.filter(s => s.type === type) : signals

  return (
    <div>
      <div className="panel-title">Signal Feed</div>
      <div className="filter-row">
        <select value={brand} onChange={e => setBrand(e.target.value)}>
          {BRANDS.map(b => <option key={b} value={b}>{b || 'All Brands'}</option>)}
        </select>
        <select value={cluster} onChange={e => setCluster(e.target.value)}>
          {CLUSTERS.map(c => <option key={c} value={c}>{c || 'All Clusters'}</option>)}
        </select>
        <select value={type} onChange={e => setType(e.target.value)}>
          {TYPES.map(t => <option key={t} value={t}>{t || 'All Types'}</option>)}
        </select>
        <select value={days} onChange={e => setDays(Number(e.target.value))}>
          {[7, 14, 30, 60, 90].map(d => <option key={d} value={d}>Last {d}d</option>)}
        </select>
      </div>

      {loading ? <div className="loading">Loading signals...</div> : (
        filtered.map(s => (
          <div key={s.id} className="card" style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
            <div className={`score-pill score-${s.color}`}>{s.hazra_score}</div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                <span className={`badge badge-${s.color}`}>{s.color === 'red' ? 'High' : s.color === 'amber' ? 'Medium' : 'Low'}</span>
                <span className="badge badge-stable">{s.type}</span>
                <span style={{ fontSize: 12, color: '#64748b' }}>{s.brand} / {s.cluster_id}</span>
                <span style={{ fontSize: 12, color: '#64748b', marginLeft: 'auto' }}>{s.date?.slice(0, 10)}</span>
              </div>
              <div style={{ fontSize: 13, color: '#94a3b8', marginBottom: 8 }}>{s.content_preview || '—'}</div>
              <div style={{ display: 'flex', gap: 16, fontSize: 12, color: '#64748b' }}>
                <span>Vol: {s.volume?.toFixed(1)}</span>
                <span>Vel: {s.velocity?.toFixed(1)}</span>
                <span>Sent: {s.sentiment?.toFixed(1)}</span>
                <span>Rec: {s.recency?.toFixed(1)}</span>
                <span>src: {s.source}</span>
              </div>
            </div>
          </div>
        ))
      )}
      {!loading && filtered.length === 0 && <div className="loading">No signals found.</div>}
    </div>
  )
}
