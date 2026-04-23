import { useEffect, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { api } from '../api'

export default function ExecutiveReports() {
  const [reports, setReports] = useState<any[]>([])
  const [selected, setSelected] = useState<any>(null)
  const [brand, setBrand] = useState('Samsung')
  const [loading, setLoading] = useState(false)
  const [generating, setGenerating] = useState(false)

  const loadReports = async () => {
    setLoading(true)
    try {
      const data = await api.getReports(brand)
      setReports(data)
      if (data.length > 0) setSelected(data[0])
    } catch (e) { console.error(e) }
    setLoading(false)
  }

  useEffect(() => { loadReports() }, [brand])

  const generate = async () => {
    setGenerating(true)
    try {
      const report = await api.generateReport(brand)
      setReports(prev => [report, ...prev])
      setSelected(report)
    } catch (e) { console.error(e) }
    setGenerating(false)
  }

  const copyToClipboard = () => {
    if (selected?.content_markdown) navigator.clipboard.writeText(selected.content_markdown)
  }

  const exportPDF = () => {
    const win = window.open('', '_blank')
    if (!win) return
    win.document.write(`<html><head><title>Report</title><style>body{font-family:sans-serif;padding:40px;max-width:800px;margin:auto}</style></head><body>`)
    win.document.write(`<pre style="white-space:pre-wrap">${selected?.content_markdown}</pre>`)
    win.document.write('</body></html>')
    win.document.close()
    win.print()
  }

  return (
    <div>
      <div className="panel-title">Executive Reports</div>
      <div className="filter-row">
        <select value={brand} onChange={e => setBrand(e.target.value)}>
          {['Samsung', 'Apple', 'Google Pixel', 'BrandAlpha', 'BrandBeta', 'BrandGamma'].map(b => <option key={b}>{b}</option>)}
        </select>
        <button onClick={generate} disabled={generating}>{generating ? 'Generating...' : 'Generate New Report'}</button>
        {selected && <button className="secondary" onClick={copyToClipboard}>Copy Markdown</button>}
        {selected && <button className="secondary" onClick={exportPDF}>Export PDF</button>}
      </div>

      <div style={{ display: 'flex', gap: 14 }}>
        {/* Report list */}
        <div style={{ width: 220, flexShrink: 0 }}>
          {loading ? <div className="loading">Loading...</div> : reports.map(r => (
            <div key={r.id} className="card" style={{ cursor: 'pointer', border: selected?.id === r.id ? '1px solid #7c6af7' : undefined }}
              onClick={() => setSelected(r)}>
              <div style={{ fontSize: 12, fontWeight: 600 }}>{r.brand}</div>
              <div style={{ fontSize: 11, color: '#64748b' }}>{r.generated_at?.slice(0, 16).replace('T', ' ')}</div>
            </div>
          ))}
          {!loading && reports.length === 0 && <div style={{ fontSize: 13, color: '#64748b' }}>No reports yet.</div>}
        </div>

        {/* Report content */}
        <div className="card markdown-report" style={{ flex: 1, maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
          {selected ? (
            <ReactMarkdown>{selected.content_markdown}</ReactMarkdown>
          ) : (
            <div style={{ color: '#64748b', fontSize: 13 }}>Select or generate a report.</div>
          )}
        </div>
      </div>
    </div>
  )
}
