import { useStore } from '../store'

export default function PatrolRecommendation() {
  const rec = useStore(s => s.patrolRecommendation)

  return (
    <section className="rounded-lg border border-panelBorder bg-panel p-4">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-textMuted">
        A* patrol recommendation
      </h2>
      <p className="mb-2 font-mono text-sm text-accent">{rec.route.join(' → ')}</p>
      <p className="text-xs text-textMuted">
        Departing {rec.originLabel} · approx. {rec.distanceKm} km across {rec.zoneCount} zones,{' '}
        {rec.note}.
      </p>
    </section>
  )
}
