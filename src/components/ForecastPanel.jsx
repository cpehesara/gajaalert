import { useStore } from '../store'

export default function ForecastPanel() {
  const forecast = useStore(s => s.forecast)

  return (
    <Panel title={`Markov forecast · ${forecast.herdId}`}>
      <p className="mb-3 text-sm text-textPrimary">
        {forecast.herdName} — currently in{' '}
        <span className="font-semibold text-accent">{forecast.currentZone}</span>
      </p>
      <p className="mb-2 text-xs text-textMuted">
        Probability of presence in the next {forecast.horizonHours} hours:
      </p>

      <div className="flex flex-col gap-2">
        {forecast.probabilities.map(p => (
          <div key={p.zone}>
            <div className="mb-1 flex items-center justify-between text-xs">
              <span className="text-textPrimary">{p.zone}</span>
              <span className="font-mono text-textMuted">{(p.probability * 100).toFixed(1)}%</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-panelBorder">
              <div
                className="h-full rounded-full bg-accent"
                style={{ width: `${p.probability * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      <p className="mt-3 text-xs text-textMuted">
        Most-likely path:{' '}
        <span className="font-mono text-textPrimary">{forecast.mostLikelyPath.join(' → ')}</span>
      </p>
    </Panel>
  )
}

function Panel({ title, children }) {
  return (
    <section className="rounded-lg border border-panelBorder bg-panel p-4">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-textMuted">{title}</h2>
      {children}
    </section>
  )
}
