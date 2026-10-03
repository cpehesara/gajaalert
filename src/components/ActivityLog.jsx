import { useStore } from '../store'

export default function ActivityLog() {
  const log = useStore(s => s.activityLog)

  return (
    <section className="rounded-lg border border-panelBorder bg-panel p-4">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wide text-textMuted">
        Activity log
      </h2>
      <div className="flex max-h-48 flex-col gap-3 overflow-y-auto text-xs">
        {log.map((entry, i) => (
          <div key={i}>
            <div className="text-textMuted">{entry.time}</div>
            <div className="text-textPrimary">{entry.text}</div>
          </div>
        ))}
      </div>
    </section>
  )
}
