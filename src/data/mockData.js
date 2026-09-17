// ---------------------------------------------------------------------------
// TEMPORARY MOCK DATA
// ---------------------------------------------------------------------------
// This file exists ONLY so the UI is buildable before the Rule-Based AI,
// Fuzzy Systems, and Spatial Search teammates expose real endpoints.
// Every shape here should match the JSON contract you agree with them
// (see the "API contract" section in the guide). Once the backend is live,
// delete this file and point src/services/api.js at the real endpoints —
// no component below should need to change.
// ---------------------------------------------------------------------------

export const situationSummary = {
  herdsTracked: 6,
  individuals: 23,
  highCriticalZones: 2,
  verifiedSightings: 0
}

export const herds = [
  { id: 'H01', name: 'Wewa Group', size: 11, zone: 'Kumbukwewa Tank Edge', source: 'simulated (CRW)', lat: 7.9822, lng: 80.3529 },
  { id: 'H02', name: 'Palukandewa Bulls', size: 1, zone: 'Kirimetiyawa Scrub', source: 'simulated (CRW)', lat: 8.0266, lng: 80.3677 },
  { id: 'H03', name: 'Usgala Herd', size: 2, zone: 'Kumbukwewa Tank Edge', source: 'simulated (CRW)', lat: 7.9809, lng: 80.3873 },
  { id: 'H04', name: 'Chena Group', size: 1, zone: 'Southern Chena Belt', source: 'simulated (CRW)', lat: 7.9678, lng: 80.3252 },
  { id: 'H05', name: 'Kumbukwewa Herd', size: 1, zone: 'Usgala Siyambalangamuwa', source: 'simulated (CRW)', lat: 8.0508, lng: 80.3347 },
  { id: 'H06', name: 'Lone Tusker', size: 7, zone: 'Usgala Siyambalangamuwa', source: 'simulated (CRW)', lat: 8.0647, lng: 80.2951 }
]

export const forecast = {
  herdId: 'H01',
  herdName: 'Wewa Group',
  currentZone: 'Kumbukwewa Tank Edge',
  horizonHours: 12,
  probabilities: [
    { zone: 'Z10 · Kumbukwewa Tank Edge', probability: 0.41 },
    { zone: 'Z07 · Kirimetiyawa Scrub', probability: 0.151 },
    { zone: 'Z12 · Southern Chena Belt', probability: 0.118 },
    { zone: 'Z09 · Railway Crossing (Galgamuwa Stn.)', probability: 0.09 }
  ],
  mostLikelyPath: ['Z10', 'Z07', 'Z10']
}

export const patrolRecommendation = {
  route: ['Z01', 'Z05', 'Z09', 'Z12', 'Z10', 'Z07'],
  originLabel: 'Galgamuwa Town',
  distanceKm: 18.1,
  zoneCount: 6,
  note: 'cost-weighted toward the highest-risk zones'
}

export const zoneRiskRegister = [
  { zone: 'Z12 · Southern Chena Belt', risk: 86, level: 'Critical', herds: 2, forecastPressure: 0.71, triggeredRules: 'R1' },
  { zone: 'Z03 · Usgala Siyambalangamuwa', risk: 82, level: 'Critical', herds: 3, forecastPressure: 1.26, triggeredRules: 'R1, R2' },
  { zone: 'Z06 · Palukandewa Forest', risk: 45, level: 'Moderate', herds: 1, forecastPressure: 0.81, triggeredRules: '—' },
  { zone: 'Z09 · Railway Crossing (Galgamuwa Stn.)', risk: 38, level: 'Moderate', herds: 0, forecastPressure: 0.3, triggeredRules: 'R1, R5' },
  { zone: 'Z08 · Nabadewa Paddy Tract', risk: 30, level: 'Low', herds: 0, forecastPressure: 0.29, triggeredRules: 'R1' },
  { zone: 'Z04 · Meegalewa Road Belt', risk: 29, level: 'Low', herds: 0, forecastPressure: 0, triggeredRules: 'R1' }
]

export const activityLog = [
  { time: '11:37:09 PM', text: 'Cycle advanced (+6h simulated) · CRW step, Markov matrix rebuilt, risk & patrol recomputed' },
  { time: '11:36:57 PM', text: 'Cycle advanced (+6h simulated) · CRW step, Markov matrix rebuilt, risk & patrol recomputed' },
  { time: '11:36:33 PM', text: 'Cycle advanced (+6h simulated) · CRW step, Markov matrix rebuilt, risk & patrol recomputed' }
]

export const zones = [
  // Rough polygon placeholders around Galgamuwa DS division.
  // Replace with the real GeoJSON your Spatial Search Lead produces
  // (analysis-zone boundaries, tank/reservoir buffers, settlement buffers).
  { id: 'Z10', name: 'Kumbukwewa Tank Edge', level: 'moderate', center: [7.9822, 80.3529] },
  { id: 'Z12', name: 'Southern Chena Belt', level: 'critical', center: [7.9678, 80.3252] },
  { id: 'Z03', name: 'Usgala Siyambalangamuwa', level: 'critical', center: [8.0508, 80.3347] },
  { id: 'Z09', name: 'Railway Crossing (Galgamuwa Stn.)', level: 'moderate', center: [7.9950, 80.3400] }
]

export const meta = {
  cycle: 0,
  windowLabel: 'Night window · Dry season',
  officer: { name: 'K. A. Bandara', role: 'Wildlife Ranger · DWC-2280' }
}
