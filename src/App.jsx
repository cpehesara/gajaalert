import Header from './components/Header'
import SidePanel from './components/SidePanel'
import MapPanel from './components/MapPanel'
import ForecastPanel from './components/ForecastPanel'
import PatrolRecommendation from './components/PatrolRecommendation'
import ManualUpdateForm from './components/ManualUpdateForm'
import ZoneRiskTable from './components/ZoneRiskTable'
import ActivityLog from './components/ActivityLog'
import { useEffect } from 'react'
import { useStore } from './store'

export default function App() {
  const loadDashboard = useStore(s => s.loadDashboard)
  const dismissError = useStore(s => s.dismissError)
  const loading = useStore(s => s.loading)
  const error = useStore(s => s.error)
  const hasData = useStore(s => s.herds.length > 0)

  useEffect(() => { loadDashboard() }, [loadDashboard])

  if (loading) return <div className="flex h-screen items-center justify-center bg-base text-textPrimary">Loading GajaAlert dashboard…</div>
  if (error && !hasData) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 bg-base p-8 text-center text-red-300">
        <div>Unable to load the dashboard: {error}</div>
        <button onClick={loadDashboard} className="rounded-md bg-accent px-4 py-2 font-medium text-base">Retry</button>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col bg-base text-textPrimary">
      <Header />
      {error && (
        <div className="flex items-center justify-between bg-risk-critical/20 px-6 py-2 text-sm text-risk-critical">
          <span>{error}</span>
          <button onClick={dismissError} className="underline">Dismiss</button>
        </div>
      )}

      <div className="flex flex-1 overflow-hidden">
        <SidePanel />

        <main className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
          <MapPanel />
          <ZoneRiskTable />
        </main>

        <aside className="flex w-96 flex-col gap-4 overflow-y-auto border-l border-panelBorder p-4">
          <ForecastPanel />
          <PatrolRecommendation />
          <ManualUpdateForm />
          <ActivityLog />
        </aside>
      </div>
    </div>
  )
}