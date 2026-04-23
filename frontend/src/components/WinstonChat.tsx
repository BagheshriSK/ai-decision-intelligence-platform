import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { v4 as uuidv4 } from 'uuid'

const SESSION_KEY = 'winston_session_id'

export default function WinstonChat() {
  const [sessionId] = useState(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (stored) return stored
    const id = uuidv4()
    localStorage.setItem(SESSION_KEY, id)
    return id
  })
  const [messages, setMessages] = useState<{ role: string; message: string }[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [brand, setBrand] = useState('Samsung')
  const [cluster, setCluster] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    api.getChatHistory(sessionId).then(h => setMessages(h.map(m => ({ role: m.role, message: m.message })))).catch(() => {})
  }, [sessionId])

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async (msg?: string) => {
    const text = msg || input.trim()
    if (!text || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', message: text }])
    setLoading(true)
    try {
      const res = await api.chat({ message: text, session_id: sessionId, context: { brand, cluster_id: cluster || undefined } })
      setMessages(prev => [...prev, { role: 'assistant', message: res.response }])
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', message: 'Error reaching Winston. Please try again.' }])
    }
    setLoading(false)
  }

  const generateReport = () => send('Generate a full executive report for the current brand and cluster.')

  return (
    <div>
      <div className="panel-title">Winston — AI Assistant</div>
      <div className="filter-row">
        <select value={brand} onChange={e => setBrand(e.target.value)}>
          {['Samsung', 'Apple', 'Google Pixel', 'BrandAlpha', 'BrandBeta', 'BrandGamma'].map(b => <option key={b}>{b}</option>)}
        </select>
        <select value={cluster} onChange={e => setCluster(e.target.value)}>
          <option value="">All Clusters</option>
          {['wellness_trends', 'product_sentiment', 'competitor_mentions'].map(c => <option key={c}>{c}</option>)}
        </select>
        <button className="secondary" onClick={generateReport} disabled={loading}>Generate Report</button>
      </div>

      <div className="chat-container card" style={{ padding: 0 }}>
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ color: '#64748b', fontSize: 13, textAlign: 'center', marginTop: 40 }}>
              Ask Winston anything about your brand signals, trends, or forecasts.
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`chat-bubble ${m.role}`} style={{ whiteSpace: 'pre-wrap' }}>{m.message}</div>
          ))}
          {loading && <div className="chat-bubble assistant" style={{ color: '#64748b' }}>Winston is thinking...</div>}
          <div ref={bottomRef} />
        </div>
        <div className="chat-input-row">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && send()}
            placeholder="Ask about signals, trends, forecasts..."
          />
          <button onClick={() => send()} disabled={loading || !input.trim()}>Send</button>
        </div>
      </div>
    </div>
  )
}
