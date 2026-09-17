import { useState } from 'react'
import { useStore } from '../store'

export default function ManualUpdateForm() {
  const herds = useStore(s => s.herds)
  const zones = useStore(s => s.zones)
  const submitVerifiedSighting = useStore(s => s.submitVerifiedSighting)

  const [herdId, setHerdId] = useState(herds[0]?.id ?? '')
  const [zoneId, setZoneId] = useState(zones[0]?.id ?? '')
  const [observedSize, setObservedSize] = useState('')
  const [notes, setNotes] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    if (!observedSize) return
    submitVerifiedSighting({ herdId, zoneId, observedSize, notes })
    setObservedSize('')
    setNotes('')
  }

  return (
    <section className="rounded-lg border border-panelBorder bg-panel p-4">
      <h2 className="mb-1 text-xs font-semibold uppercase tracking-wide text-textMuted">
        Manual field update
      </h2>
      <p className="mb-3 text-xs text-textMuted">
        Patrol-survey sightings override the simulated position and are flagged{' '}
        <span className="text-accent">verified</span>.
      </p>

      <form onSubmit={handleSubmit} className="flex flex-col gap-3 text-sm">
        <Field label="Herd">
          <select
            value={herdId}
            onChange={e => setHerdId(e.target.value)}
            className="w-full rounded-md border border-panelBorder bg-base px-2 py-1.5 text-textPrimary"
          >
            {herds.map(h => (
              <option key={h.id} value={h.id}>
                {h.id} · {h.name}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Zone">
          <select
            value={zoneId}
            onChange={e => setZoneId(e.target.value)}
            className="w-full rounded-md border border-panelBorder bg-base px-2 py-1.5 text-textPrimary"
          >
            {zones.map(z => (
              <option key={z.id} value={z.id}>
                {z.id} · {z.name}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Observed herd size">
          <input
            type="number"
            min="1"
            value={observedSize}
            onChange={e => setObservedSize(e.target.value)}
            className="w-full rounded-md border border-panelBorder bg-base px-2 py-1.5 text-textPrimary"
          />
        </Field>

        <Field label="Notes">
          <textarea
            rows={2}
            placeholder="e.g. crop damage reported near tank bund"
            value={notes}
            onChange={e => setNotes(e.target.value)}
            className="w-full resize-none rounded-md border border-panelBorder bg-base px-2 py-1.5 text-textPrimary placeholder:text-textMuted"
          />
        </Field>

        <button
          type="submit"
          className="rounded-md bg-accent py-2 font-medium text-base hover:bg-accentSoft transition-colors"
        >
          Submit verified sighting
        </button>
      </form>
    </section>
  )
}

function Field({ label, children }) {
  return (
    <label className="flex flex-col gap-1">
      <span className="text-xs text-textMuted">{label}</span>
      {children}
    </label>
  )
}
