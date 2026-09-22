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
  const loading = useStore(s => s.loading)
  const error = useStore(s => s.error)

  useEffect(() => { loadDashboard() }, [loadDashboard])

  if (loading) return <div className="flex h-screen items-center justify-center bg-base text-textPrimary">Loading GajaAlert dashboard…</div>
  if (error) return <div className="flex h-screen items-center justify-center bg-base p-8 text-center text-red-300">Unable to load the dashboard: {error}</div>

  return (
    <div className="flex h-screen flex-col bg-base text-textPrimary">
      <Header />

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
