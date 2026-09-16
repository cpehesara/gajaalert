import { create } from 'zustand'
import * as mock from './data/mockData'

// USE_MOCK toggles the entire app between static placeholder data and the
// real backend. Flip it to false once your teammates' API is reachable —
// every component reads from this store, never from mockData directly,
// so nothing else has to change.
const USE_MOCK = true

export const useStore = create((set, get) => ({
  loading: USE_MOCK ? false : true,
  meta: mock.meta,
  situationSummary: mock.situationSummary,
  herds: mock.herds,
  selectedHerdId: mock.herds[0].id,
  forecast: mock.forecast,
  patrolRecommendation: mock.patrolRecommendation,
  zoneRiskRegister: mock.zoneRiskRegister,
  activityLog: mock.activityLog,
  zones: mock.zones,

  selectHerd: herdId => set({ selectedHerdId: herdId }),

  // Called by the "Submit verified sighting" form. In mock mode it just
  // appends a fake log line; swap the body for `await api.submitVerifiedSighting(payload)`
  // plus a refetch (or let the socket push the update back down).
  submitVerifiedSighting: payload => {
    const time = new Date().toLocaleTimeString('en-US', { hour12: true })
    set(state => ({
      activityLog: [
        { time, text: `Manual field update · ${payload.herdId} → ${payload.zoneId} (size ${payload.observedSize}) — verified` },
        ...state.activityLog
      ]
    }))
  },

  // Called by "Next cycle (+6h)". In mock mode it's a no-op tick; in real
  // mode this becomes `await api.advanceCycle()` and the socket event
  // CYCLE_UPDATED does the rest.
  advanceCycle: () => {
    set(state => ({ meta: { ...state.meta, cycle: state.meta.cycle + 1 } }))
  }
}))
