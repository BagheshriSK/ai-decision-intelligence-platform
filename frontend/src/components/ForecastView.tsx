import { useState } from 'react'
import { ComposedChart, Line, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from 'recharts'
import { api } from '../api'

const CLUSTERS = ['camera', 'battery', 'overheating', 'price', 'performance', 'general', 'wellness_trends', 'product_sentiment', 'competitor_mentions']
const BRANDS = ['Samsung', 'Apple', 'Google Pixel', 'BrandAlpha', 'BrandBeta', 'BrandGamma']
const HORIZONS = [7, 14, 28]

export default function ForecastView() {
  const [cluster, setCluster] = useState(CLUSTERS[0])
  const [brand, setBrand] = useState('Samsung')
  const [horizon, setHorizon] = useState(7)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const run = async () => {
    setLoading(true); setError('')
    try {
      const data = await api.forecast({ cluster_id: cluster, brand, horizon_days: horizon })
      setResult(data)
    } catch (e: any) { setError(e.message) }
    setLoading(false)
  }

  const chartData = result ? [
    ...result.historical.slice(-30).map((p: any) => ({ ...p, type: 'historical' })),
    ...result.forecast.map((p: any) => ({ ...p, type: 'forecast' }))
  ] : []

  return (
    <div>
      <div className="panel-title">Forecast View</div>
      <div className="filter-row">
        <select value={brand} onChange={e => setBrand(e.target.value)}>
          {BRANDS.map(b => <option key={b}>{b}</option>)}
        </select>
        <select value={cluster} onChange={e => setCluster(e.target.value)}>
          {CLUSTERS.map(c => <option key={c}>{c}</option>)}
        </select>
        <select value={horizon} onChange={e => setHorizon(Number(e.target.value))}>
          {HORIZONS.map(h => <option key={h} value={h}>{h} days</option>)}
        </select>
        <button onClick={run} disabled={loading}>{loading ? 'Running...' : 'Run Forecast'}</button>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <>
          <div className="grid-3" style={{ marginBottom: 16 }}>
            <div className="card">
              <div className="stat-label">Peak Day</div>
              <div className="stat-value" style={{ fontSize: 16 }}>{result.peak_day}</div>
            </div>
            <div className="card">
              <div className="stat-label">Peak Score</div>
              <div className="stat-value">{result.peak_score}</div>
            </div>
            <div className="card">
              <div className="stat-label">Horizon</div>
              <div className="stat-value" style={{ fontSize: 16 }}>{result.horizon_days}d</div>
            </div>
          </div>

          <div className="card" style={{ marginBottom: 16 }}>
            <ResponsiveContainer width="100%" height={260}>
              <ComposedChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2235" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={d => d.slice(5)} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip contentStyle={{ background: '#13151f', border: '1px solid #1e2235', borderRadius: 6 }} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Area type="monotone" dataKey="yhat_upper" fill="#7c6af720" stroke="none" name="Upper Band" />
                <Area type="monotone" dataKey="yhat_lower" fill="#0f1117" stroke="none" name="Lower Band" />
                <Line type="monotone" dataKey="yhat" stroke="#7c6af7" dot={false} strokeWidth={2} name="Forecast" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ background: '#0d1e2e', borderColor: '#1e3a5f' }}>
            <div style={{ fontSize: 12, color: '#60a5fa', marginBottom: 6, fontWeight: 600 }}>Executive Narrative</div>
            <div style={{ fontSize: 14, color: '#cbd5e1', lineHeight: 1.6 }}>{result.narrative}</div>
          </div>
        </>
      )}
    </div>
  )
}
