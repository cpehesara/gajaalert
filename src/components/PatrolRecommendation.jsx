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
        Departing {rec.originLabel} · approx. {rec.distanceKm} km
        {rec.estimatedMinutes ? ` (~${rec.estimatedMinutes} min)` : ''} across {rec.zoneCount} zones,{' '}
        {rec.note}.
      </p>
      {rec.priorityZones?.length > 0 && (
        <p className="mt-2 text-xs text-textMuted">
          Priority targets: <span className="font-mono text-textPrimary">{rec.priorityZones.join(', ')}</span>
        </p>
      )}
      {rec.unreachedZones?.length > 0 && (
        <p className="mt-1 text-xs text-risk-critical">
          Not reachable: {rec.unreachedZones.join(', ')}
        </p>
      )}
    </section>
  )
}