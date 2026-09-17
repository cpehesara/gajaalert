import axios from 'axios'

// Every request goes through /api so vite.config.js can proxy it to
// whatever host your backend actually runs on (local, staging, prod)
// without touching this file.
const client = axios.create({ baseURL: '/api' })

export const api = {
  getSituationSummary: () => client.get('/situation-summary').then(r => r.data),
  getHerds: () => client.get('/herds').then(r => r.data),
  getForecast: herdId => client.get(`/forecast/${herdId}`).then(r => r.data),
  getPatrolRecommendation: () => client.get('/patrol-recommendation').then(r => r.data),
  getZoneRiskRegister: () => client.get('/zone-risk-register').then(r => r.data),
  getActivityLog: () => client.get('/activity-log').then(r => r.data),
  getZones: () => client.get('/zones').then(r => r.data),

  // Officer manual override — the one write path in the whole app.
  submitVerifiedSighting: payload => client.post('/sightings', payload).then(r => r.data),

  advanceCycle: () => client.post('/cycle/advance').then(r => r.data)
}
