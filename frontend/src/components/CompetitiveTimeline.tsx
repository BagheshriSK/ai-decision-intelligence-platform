import { useEffect, useState } from 'react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend, ReferenceDot } from 'recharts'
import { api } from '../api'

const BRAND_COLORS: Record<string, string> = {
  Samsung: '#7c6af7',
  Apple: '#34d399',
  'Google Pixel': '#fbbf24',
  BrandAlpha: '#60a5fa',
  BrandBeta: '#fb923c',
  BrandGamma: '#f87171',
}

const CustomDot = (props: any) => {
  const { cx, cy, payload, brand, inflections } = props
  const inf = inflections?.find((i: any) => i.date === payload.date)
  if (!inf) return null
  return <circle cx={cx} cy={cy} r={6} fill={inf.direction === 'surge' ? '#34d399' : '#f87171'} stroke="#fff" strokeWidth={1.5} />
}

export default function CompetitiveTimeline() {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)
  const [tooltip, setTooltip] = useState<any>(null)

  const load = () => {
    setLoading(true)
    api.getCompetitive({ client: 'Samsung', competitors: 'Apple,Google Pixel', days })
      .then(setData).catch(console.error).finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [days])

  if (loading) return <div className="loading">Loading competitive data...</div>

  // Merge daily data into unified chart format
  const allDates = new Set<string>()
  if (data?.brands) {
    data.brands.forEach((b: string) => {
      data.data[b]?.daily?.forEach((d: any) => allDates.add(d.date))
    })
  }
  const chartData = Array.from(allDates).sort().map(date => {
    const point: Record<string, any> = { date }
    data?.brands?.forEach((b: string) => {
      const entry = data.data[b]?.daily?.find((d: any) => d.date === date)
      point[b] = entry?.score ?? null
    })
    return point
  })

  return (
    <div>
      <div className="panel-title">Competitive Timeline</div>
      <div className="filter-row">
        <select value={days} onChange={e => setDays(Number(e.target.value))}>
          {[7, 14, 30, 60, 90].map(d => <option key={d} value={d}>Last {d}d</option>)}
        </select>
        <button className="secondary" onClick={load}>Refresh</button>
      </div>

      <div className="card">
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2235" />
            <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={d => d.slice(5)} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#64748b' }} />
            <Tooltip
              contentStyle={{ background: '#13151f', border: '1px solid #1e2235', borderRadius: 6 }}
              formatter={(val: any, name: string) => [val?.toFixed(1), name]}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {data?.brands?.map((b: string) => (
              <Line key={b} type="monotone" dataKey={b} stroke={BRAND_COLORS[b] || '#94a3b8'}
                dot={(props: any) => <CustomDot {...props} brand={b} inflections={data.data[b]?.inflections} />}
                strokeWidth={2} connectNulls />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Inflection points */}
      {data?.brands?.map((b: string) => {
        const infs = data.data[b]?.inflections || []
        if (!infs.length) return null
        return (
          <div key={b} className="card" style={{ marginTop: 10 }}>
            <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: BRAND_COLORS[b] }}>{b} — Inflection Points</div>
            {infs.map((inf: any, i: number) => (
              <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '6px 0', borderBottom: '1px solid #1e2235', fontSize: 13 }}>
                <span style={{ color: '#64748b', minWidth: 90 }}>{inf.date}</span>
                <span className={`badge badge-${inf.direction === 'surge' ? 'emerging' : 'declining'}`}>{inf.direction}</span>
                <span style={{ color: inf.direction === 'surge' ? '#34d399' : '#f87171' }}>{inf.delta > 0 ? '+' : ''}{inf.delta}</span>
                <span style={{ color: '#94a3b8', flex: 1 }}>{inf.label}</span>
              </div>
            ))}
          </div>
        )
      })}
    </div>
  )
}
