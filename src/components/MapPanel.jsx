import { MapContainer, TileLayer, CircleMarker, Popup, Circle } from 'react-leaflet'
import { useStore } from '../store'

const GALGAMUWA_CENTER = [8.0, 80.335]

const RISK_COLORS = {
  critical: '#e05a4f',
  high: '#e0a93c',
  moderate: '#e0c93c',
  low: '#5fbf82'
}

export default function MapPanel() {
  const herds = useStore(s => s.herds)
  const zones = useStore(s => s.zones)
  const selectedHerdId = useStore(s => s.selectedHerdId)

  return (
    <section className="flex flex-1 flex-col rounded-lg border border-panelBorder bg-panel p-3">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <h2 className="text-xs font-semibold uppercase tracking-wide text-textMuted">
            Operational map
          </h2>
          <p className="text-xs text-textMuted">
            OpenStreetMap base · {zones.length} analysis zones · live simulation layer
          </p>
        </div>
      </div>

      <div className="h-[480px] overflow-hidden rounded-md">
        <MapContainer
          center={GALGAMUWA_CENTER}
          zoom={12}
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
              radius={900}
              pathOptions={{
                color: RISK_COLORS[z.level] ?? '#5fbf82',
                fillOpacity: 0.15,
                weight: 1
              }}
            >
              <Popup>{z.id} · {z.name}</Popup>
            </Circle>
          ))}

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
                {h.zone} — {h.size} individuals
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </section>
  )
}
