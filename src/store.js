import { create } from 'zustand'
import { api } from './services/api'
import {
  activityLog as mockActivityLog,
  forecast as mockForecast,
  herds as mockHerds,
  meta as mockMeta,
  patrolRecommendation as mockPatrolRecommendation,
  situationSummary as mockSituationSummary,
  zoneRiskRegister as mockZoneRiskRegister,
  zones as mockZones
} from './data/mockData'

const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA !== 'false'

const createMockDashboard = () => ({
  meta: { ...mockMeta, simTime: new Date().toISOString() },
  situationSummary: { ...mockSituationSummary, earlyWarnings: 0 },
  herds: mockHerds.map(herd => ({ ...herd })),
  selectedHerdId: mockHerds[0]?.id ?? null,
  forecast: { ...mockForecast, probabilities: mockForecast.probabilities.map(item => ({ ...item })), mostLikelyPath: [...mockForecast.mostLikelyPath] },
  patrolRecommendation: { ...mockPatrolRecommendation, route: [...mockPatrolRecommendation.route] },
  zoneRiskRegister: mockZoneRiskRegister.map(zone => ({ ...zone })),
  activityLog: mockActivityLog.map(entry => ({ ...entry })),
  zones: mockZones.map(zone => ({ ...zone, center: [...zone.center] }))
})

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
      const dashboard = USE_MOCK_DATA ? createMockDashboard() : await api.getDashboard()
      const keep = dashboard.herds.some(h => h.id === previous) ? previous : dashboard.herds[0]?.id ?? null
      set({ ...dashboard, loading: false, error: null, selectedHerdId: keep })
      // The dashboard payload carries the first herd's forecast; refetch if another herd is selected.
      if (!USE_MOCK_DATA && keep && keep !== dashboard.herds[0]?.id) {
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
      if (USE_MOCK_DATA) {
        const herd = get().herds.find(item => item.id === herdId)
        if (!herd) throw new Error(`Unknown herd: ${herdId}`)
        set({ forecast: { ...mockForecast, herdId, herdName: herd.name, currentZone: herd.zone } })
      } else {
        set({ forecast: await api.getForecast(herdId) })
      }
    } catch (error) {
      console.error('Forecast loading failed:', error)
      set({ error: messageOf(error, 'Forecast unavailable') })
    }
  },

  submitVerifiedSighting: async payload => {
    try {
      if (USE_MOCK_DATA) {
        const zone = get().zones.find(item => item.id === payload.zoneId)
        const herd = get().herds.find(item => item.id === payload.herdId)
        if (!zone || !herd) throw new Error('Select a valid herd and zone')
        set(state => ({
          herds: state.herds.map(item => item.id === payload.herdId
            ? { ...item, zone: zone.name, lat: zone.center[0], lng: zone.center[1], size: Number(payload.observedSize), source: 'officer-verified' }
            : item),
          situationSummary: { ...state.situationSummary, verifiedSightings: state.situationSummary.verifiedSightings + 1 },
          activityLog: [{ time: new Date().toLocaleTimeString(), text: `Mock sighting recorded for ${herd.name} in ${zone.name}` }, ...state.activityLog]
        }))
        return
      }
      await api.submitVerifiedSighting(payload)
      await get().loadDashboard()
    } catch (error) {
      console.error('Verified sighting submission failed:', error)
      set({ error: messageOf(error, 'Submission failed') })
    }
  },

  advanceCycle: async () => {
    try {
      if (USE_MOCK_DATA) {
        set(state => {
          const nextTime = new Date(state.meta.simTime ?? Date.now())
          nextTime.setHours(nextTime.getHours() + 6)
          return {
            meta: { ...state.meta, cycle: state.meta.cycle + 1, simTime: nextTime.toISOString() },
            activityLog: [{ time: nextTime.toLocaleTimeString(), text: 'Mock cycle advanced (+6h simulated)' }, ...state.activityLog]
          }
        })
        return
      }
      await api.advanceCycle()
      await get().loadDashboard()
    } catch (error) {
      console.error('Cycle advance failed:', error)
      set({ error: messageOf(error, 'Cycle advance failed') })
    }
  }
}))