import { create } from 'zustand'
import { api } from './services/api'

const emptyState = {
  loading: true,
  error: null,
  meta: { cycle: 0, windowLabel: 'Night window · Dry season', officer: { name: 'Loading', role: '' } },
  situationSummary: { herdsTracked: 0, individuals: 0, highCriticalZones: 0, verifiedSightings: 0 },
  herds: [],
  selectedHerdId: null,
  forecast: { herdId: '—', herdName: 'Loading', currentZone: '—', horizonHours: 12, probabilities: [], mostLikelyPath: [] },
  patrolRecommendation: { route: [], originLabel: '—', distanceKm: 0, zoneCount: 0, note: '' },
  zoneRiskRegister: [],
  activityLog: [],
  zones: []
}

export const useStore = create((set, get) => ({
  ...emptyState,

  loadDashboard: async () => {
    try {
      const dashboard = await api.getDashboard()
      set({ ...dashboard, loading: false, error: null, selectedHerdId: dashboard.herds[0]?.id ?? null })
    } catch (error) {
      const message = error.response?.data?.error ?? error.message ?? 'Unable to load dashboard'
      set({ loading: false, error: message })
      console.error('Dashboard loading failed:', error)
    }
  },

  selectHerd: async herdId => {
    set({ selectedHerdId: herdId })
    try {
      set({ forecast: await api.getForecast(herdId) })
    } catch (error) {
      console.error('Forecast loading failed:', error)
      set({ error: error.message })
    }
  },

  submitVerifiedSighting: async payload => {
    try {
      await api.submitVerifiedSighting(payload)
      await get().loadDashboard()
    } catch (error) {
      console.error('Verified sighting submission failed:', error)
      set({ error: error.message })
    }
  },

  advanceCycle: async () => {
    try {
      await api.advanceCycle()
      await get().loadDashboard()
    } catch (error) {
      console.error('Cycle advance failed:', error)
      set({ error: error.message })
    }
  }
}))
