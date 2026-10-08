import { create } from 'zustand'
import { api } from './services/api'

const emptyState = {
  loading: true,
  error: null,
  meta: { cycle: 0, windowLabel: '', simTime: null, officer: { name: 'Loading', role: '' } },
  situationSummary: { herdsTracked: 0, individuals: 0, highCriticalZones: 0, earlyWarnings: 0, verifiedSightings: 0 },
  herds: [],
  selectedHerdId: null,
  forecast: { herdId: '—', herdName: 'Loading', currentZone: '—', horizonHours: 12, probabilities: [], mostLikelyPath: [] },
  patrolRecommendation: { route: [], originLabel: '—', distanceKm: 0, zoneCount: 0, note: '' },
  zoneRiskRegister: [],
  activityLog: [],
  zones: []
}

const messageOf = (error, fallback) => error.response?.data?.error ?? error.message ?? fallback

export const useStore = create((set, get) => ({
  ...emptyState,

  dismissError: () => set({ error: null }),

  loadDashboard: async () => {
    try {
      const previous = get().selectedHerdId
      const dashboard = await api.getDashboard()
      const keep = dashboard.herds.some(h => h.id === previous) ? previous : dashboard.herds[0]?.id ?? null
      set({ ...dashboard, loading: false, error: null, selectedHerdId: keep })
      // The dashboard payload carries the first herd's forecast; refetch if another herd is selected.
      if (keep && keep !== dashboard.herds[0]?.id) {
        set({ forecast: await api.getForecast(keep) })
      }
    } catch (error) {
      // Keep whatever is already on screen; App shows a dismissible banner instead of a blank page.
      set({ loading: false, error: messageOf(error, 'Unable to load dashboard') })
      console.error('Dashboard loading failed:', error)
    }
  },

  selectHerd: async herdId => {
    set({ selectedHerdId: herdId })
    try {
      set({ forecast: await api.getForecast(herdId) })
    } catch (error) {
      console.error('Forecast loading failed:', error)
      set({ error: messageOf(error, 'Forecast unavailable') })
    }
  },

  submitVerifiedSighting: async payload => {
    try {
      await api.submitVerifiedSighting(payload)
      await get().loadDashboard()
    } catch (error) {
      console.error('Verified sighting submission failed:', error)
      set({ error: messageOf(error, 'Submission failed') })
    }
  },

  advanceCycle: async () => {
    try {
      await api.advanceCycle()
      await get().loadDashboard()
    } catch (error) {
      console.error('Cycle advance failed:', error)
      set({ error: messageOf(error, 'Cycle advance failed') })
    }
  }
}))