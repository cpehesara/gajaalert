import { useStore } from '../store'

export default function Header() {
  const meta = useStore(s => s.meta)
  const summary = useStore(s => s.situationSummary)
  const advanceCycle = useStore(s => s.advanceCycle)

  // Simulated clock from the backend (real time at start-up, +6 h per cycle).
  const simClock = meta.simTime
    ? new Date(meta.simTime).toLocaleString('en-US', { weekday: 'short', hour: 'numeric', minute: '2-digit', hour12: true })
    : '—'

  return (
    <header className="flex items-center justify-between border-b border-panelBorder bg-panel px-6 py-3">
      <div>
        <div className="text-xs tracking-wide text-textMuted">DWC · Galgamuwa DS Division</div>
        <h1 className="text-lg font-semibold text-textPrimary">Elephant Movement Intelligence</h1>
      </div>

      <div className="flex items-center gap-3 text-sm">
        <Pill>Cycle {meta.cycle}</Pill>
        <Pill>{meta.windowLabel}</Pill>
        <Pill>Sim clock · {simClock}</Pill>
        {summary.earlyWarnings > 0 && (
          <span className="rounded-md border border-risk-critical px-3 py-1.5 font-medium text-risk-critical">
            ⚠ {summary.earlyWarnings} early warning{summary.earlyWarnings > 1 ? 's' : ''}
          </span>
        )}
        <button
          onClick={advanceCycle}
          className="rounded-md bg-accent px-3 py-1.5 font-medium text-base hover:bg-accentSoft transition-colors"
        >
          Next cycle (+6h)
        </button>
      </div>

      <div className="text-right text-sm">
        <div className="text-textPrimary">{meta.officer.name}</div>
        <div className="text-xs text-textMuted">{meta.officer.role}</div>
      </div>
    </header>
  )
}

function Pill({ children }) {
  return (
    <span className="rounded-md border border-panelBorder px-3 py-1.5 text-textPrimary">
      {children}
    </span>
  )
}