import { useStore } from '../store'

const LEVEL_COLOR = {
  Critical: 'text-risk-critical',
  High: 'text-risk-high',
  Moderate: 'text-risk-moderate',
  Low: 'text-risk-low'
}

const BAR_COLOR = {
  Critical: 'bg-risk-critical',
  High: 'bg-risk-high',
  Moderate: 'bg-risk-moderate',
  Low: 'bg-risk-low'
}

export default function ZoneRiskTable() {
  const rows = useStore(s => s.zoneRiskRegister)

  return (
    <section className="rounded-lg border border-panelBorder bg-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-xs font-semibold uppercase tracking-wide text-textMuted">
          Zone risk register (rule-based + fuzzy)
        </h2>
        <span className="text-xs text-textMuted">Recomputed each cycle · 12h forecast pressure included</span>
      </div>

      <table className="w-full text-left text-sm">
        <thead>
          <tr className="border-b border-panelBorder text-xs uppercase tracking-wide text-textMuted">
            <th className="py-2 font-medium">Zone</th>
            <th className="py-2 font-medium">Risk</th>
            <th className="py-2 font-medium">Level</th>
            <th className="py-2 font-medium">Herds</th>
            <th className="py-2 font-medium">Forecast pressure</th>
            <th className="py-2 font-medium">Triggered rules</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.zone} className="border-b border-panelBorder/50">
              <td className="py-2 text-textPrimary">{row.zone}</td>
              <td className="py-2">
                <div className="flex items-center gap-2">
                  <div className="h-1.5 w-20 overflow-hidden rounded-full bg-panelBorder">
                    <div
                      className={`h-full ${BAR_COLOR[row.level]}`}
                      style={{ width: `${row.risk}%` }}
                    />
                  </div>
                  <span className="font-mono text-xs text-textMuted">{row.risk}</span>
                </div>
              </td>
              <td className={`py-2 font-medium ${LEVEL_COLOR[row.level]}`}>{row.level}</td>
              <td className="py-2 text-textPrimary">{row.herds}</td>
              <td className="py-2 font-mono text-textMuted">{row.forecastPressure}</td>
              <td className="py-2 font-mono text-textMuted">{row.triggeredRules}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
