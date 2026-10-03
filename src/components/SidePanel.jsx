import { useStore } from '../store'

export default function SidePanel() {
  const summary = useStore(s => s.situationSummary)
  const herds = useStore(s => s.herds)
  const selectedHerdId = useStore(s => s.selectedHerdId)
  const selectHerd = useStore(s => s.selectHerd)

  return (
    <aside className="flex w-80 flex-col gap-4 overflow-y-auto border-r border-panelBorder p-4">
      <Panel title="Situation summary">
        <div className="grid grid-cols-2 gap-3">
          <Stat value={summary.herdsTracked} label="Herds tracked" />
          <Stat value={summary.individuals} label="Individuals" />
          <Stat value={summary.highCriticalZones} label="High/critical zones" accent />
          <Stat value={summary.verifiedSightings} label="Verified sightings" />
        </div>
      </Panel>

      <Panel title="Herds">
        <div className="flex flex-col gap-2">
          {herds.map(h => (
            <button
              key={h.id}
              onClick={() => selectHerd(h.id)}
              className={`rounded-md border px-3 py-2 text-left transition-colors ${
                h.id === selectedHerdId
                  ? 'border-accent bg-accent/10'
                  : 'border-panelBorder hover:border-accent/40'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium text-textPrimary">
                  {h.id} · {h.name}
                </span>
                <span className="text-xs text-textMuted">{h.size} ind.</span>
              </div>
              <div className="text-xs text-textMuted">
                {h.zone} · {h.source}
              </div>
              <div className="font-mono text-xs text-textMuted">
                {h.lat.toFixed(4)}°N, {h.lng.toFixed(4)}°E
              </div>
            </button>
          ))}
        </div>
      </Panel>
    </aside>
  )
}

function Panel({ title, children }) {
  return (
    <section className="rounded-lg border border-panelBorder bg-panel p-4">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-textMuted">
        {title}
      </h2>
      {children}
    </section>
  )
}

function Stat({ value, label, accent }) {
  return (
    <div>
      <div className={`text-2xl font-semibold ${accent ? 'text-accent' : 'text-textPrimary'}`}>
        {value}
      </div>
      <div className="text-xs text-textMuted">{label}</div>
    </div>
  )
}
