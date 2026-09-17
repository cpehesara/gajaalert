# GajaAlert Frontend

GajaAlert is a decision-support dashboard for monitoring elephant movement risk in the Galgamuwa Divisional Secretariat Division. The frontend helps field officers and coordinators view risk zones, forecast movement, review patrol guidance, and submit verified sighting updates.

## Features

- Interactive map view of elephant movement and risk areas
- Zone risk summary table
- Forecast and herd movement information
- Patrol recommendation panel
- Manual field update form for verified sightings
- Activity log for recent events
- Real-time updates support through Socket.IO

## Tech Stack

- React + Vite
- Tailwind CSS
- Zustand for state management
- Leaflet / React Leaflet for map rendering
- Recharts for charts
- Axios for REST API calls
- Socket.IO client for live updates

## Prerequisites

Before running the project, make sure you have:

- Node.js 18+ installed
- npm installed

## Install dependencies

```bash
npm install
```

## Run the frontend locally

```bash
npm run dev
```

Then open:

```text
http://localhost:5173
```

The Vite dev server is configured to proxy API requests to the backend at:

```text
http://localhost:4000
```

This is defined in `vite.config.js`.

## Production build

To create a production build:

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

## Project structure

```text
src/
  App.jsx                  # Main app layout
  store.js                 # Zustand store and app state
  data/
    mockData.js            # Demo/mock data for local development
  services/
    api.js                 # API calls to backend endpoints
    socket.js              # Socket.IO connection and event handlers
  components/
    Header.jsx
    SidePanel.jsx
    MapPanel.jsx
    ForecastPanel.jsx
    PatrolRecommendation.jsx
    ManualUpdateForm.jsx
    ZoneRiskTable.jsx
    ActivityLog.jsx
```

## Working with the backend

The frontend expects a backend API on `http://localhost:4000`.

- API calls are centralized in `src/services/api.js`
- Socket events are handled in `src/services/socket.js`
- Vite forwards requests under `/api` to the backend via proxy

If your backend is not ready yet, the app can run using mock data. This is controlled in `src/store.js`:

```js
const USE_MOCK = true
```

When `USE_MOCK` is `true`, the dashboard uses fake data for development and UI testing. Set it to `false` when the real backend is connected.

## Common development workflow

1. Install dependencies
2. Start backend server if available
3. Run `npm run dev`
4. Open the app in the browser
5. Test UI behavior and data flow
6. When ready, build with `npm run build`

## Notes

This project is a frontend prototype. The app is designed to connect to a backend API and live event stream, but the mock mode allows the UI to work without a backend during early development.
