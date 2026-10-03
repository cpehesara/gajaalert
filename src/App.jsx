import Header from './components/Header'
import SidePanel from './components/SidePanel'
import MapPanel from './components/MapPanel'
import ForecastPanel from './components/ForecastPanel'
import PatrolRecommendation from './components/PatrolRecommendation'
import ManualUpdateForm from './components/ManualUpdateForm'
import ZoneRiskTable from './components/ZoneRiskTable'
import ActivityLog from './components/ActivityLog'

export default function App() {
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
