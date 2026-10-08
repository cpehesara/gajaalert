import { MapContainer, TileLayer, CircleMarker, Popup, Circle, Polyline, Tooltip } from 'react-leaflet'
import { useStore } from '../store'

const GALGAMUWA_CENTER = [8.0, 80.335]

const RISK_COLORS = {
  critical: '#e05a4f',
  high: '#e05a4f',
  moderate: '#e0c93c',
  low: '#5fbf82'
}

export default function MapPanel() {
  const herds = useStore(s => s.herds)
  const zones = useStore(s => s.zones)
  const route = useStore(s => s.patrolRecommendation.route)
  const selectedHerdId = useStore(s => s.selectedHerdId)

  const centers = Object.fromEntries(zones.map(z => [z.id, z.center]))
  const routePoints = route.map(id => centers[id]).filter(Boolean)
  const firstVisit = {}
  route.forEach((id, i) => { if (!(id in firstVisit)) firstVisit[id] = i + 1 })

  return (
    <section className="flex flex-1 flex-col rounded-lg border border-panelBorder bg-panel p-3">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wide text-textMuted">
            Operational map
          </h2>
          <p className="text-xs text-textMuted">
            {zones.length} zones coloured by current risk · green dots = herds · orange line = A* patrol route
          </p>
        </div>
      </div>

      <div className="h-[480px] overflow-hidden rounded-md">
        <MapContainer
          center={GALGAMUWA_CENTER}
          zoom={11}
          scrollWheelZoom
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {zones.map(z => (
            <Circle
              key={z.id}
              center={z.center}
              radius={2200}
              pathOptions={{
                color: RISK_COLORS[z.level] ?? '#5fbf82',
                fillOpacity: 0.2,
                weight: 1.5
              }}
            >
              <Popup>{z.id} · {z.name}</Popup>
            </Circle>
          ))}

          {routePoints.length > 1 && (
            <Polyline positions={routePoints} pathOptions={{ color: '#f5b942', weight: 4, dashArray: '8 6' }} />
          )}

          {Object.entries(firstVisit).map(([id, order]) =>
            centers[id] ? (
              <CircleMarker
                key={`stop-${id}`}
                center={centers[id]}
                radius={5}
                pathOptions={{ color: '#f5b942', fillColor: '#f5b942', fillOpacity: 1 }}
              >
                <Tooltip permanent direction="top" offset={[0, -6]}>{order === 1 ? 'Start' : order}</Tooltip>
              </CircleMarker>
            ) : null
          )}

          {herds.map(h => (
            <CircleMarker
              key={h.id}
              center={[h.lat, h.lng]}
              radius={h.id === selectedHerdId ? 10 : 6}
              pathOptions={{
                color: '#2fd07a',
                fillColor: '#2fd07a',
                fillOpacity: h.id === selectedHerdId ? 1 : 0.6
              }}
            >
              <Popup>
                <strong>{h.id} · {h.name}</strong>
                <br />
                {h.zone} — {h.size} individuals ({h.source})
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </section>
  )
}