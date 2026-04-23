import { useState } from 'react'
import SignalFeed from './components/SignalFeed'
import TrendDetection from './components/TrendDetection'
import ForecastView from './components/ForecastView'
import CompetitiveTimeline from './components/CompetitiveTimeline'
import WinstonChat from './components/WinstonChat'
import ExecutiveReports from './components/ExecutiveReports'
import AlertCenter from './components/AlertCenter'

const NAV = [
  { id: 'signals', label: 'Signal Feed', icon: '📡' },
  { id: 'trends', label: 'Trend Detection', icon: '📈' },
  { id: 'forecast', label: 'Forecast', icon: '🔮' },
  { id: 'competitive', label: 'Competitive', icon: '⚔️' },
  { id: 'winston', label: 'Winston Chat', icon: '🤖' },
  { id: 'reports', label: 'Reports', icon: '📋' },
  { id: 'alerts', label: 'Alert Center', icon: '🚨' },
]

export default function App() {
  const [active, setActive] = useState('signals')

  const renderPanel = () => {
    switch (active) {
      case 'signals': return <SignalFeed />
      case 'trends': return <TrendDetection />
      case 'forecast': return <ForecastView />
      case 'competitive': return <CompetitiveTimeline />
      case 'winston': return <WinstonChat />
      case 'reports': return <ExecutiveReports />
      case 'alerts': return <AlertCenter />
      default: return null
    }
  }

  return (
    <div className="app">
      <nav className="sidebar">
        <div className="sidebar-logo">Decision<span>IQ</span></div>
        {NAV.map(n => (
          <div key={n.id} className={`nav-item ${active === n.id ? 'active' : ''}`} onClick={() => setActive(n.id)}>
            <span>{n.icon}</span>
            <span>{n.label}</span>
          </div>
        ))}
      </nav>
      <main className="main">
        {renderPanel()}
      </main>
    </div>
  )
}
