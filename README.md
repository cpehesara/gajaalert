# GajaAlert

GajaAlert is a decision-support system for monitoring elephant movement risk in the Galgamuwa Divisional Secretariat Division. It combines a React dashboard with a Flask risk-analysis API.

## Features

- Interactive risk and movement dashboard
- Zone risk summary and forecast panels
- Patrol recommendations
- Manual field updates and activity log
- Rule-based and fuzzy risk evaluation
- Movement prediction and spatial patrol routing
- Mock-data mode for frontend review without the backend

## Prerequisites

- Node.js 18 or newer
- npm
- Python 3.13 or a compatible supported Python version

## Installation

Install frontend dependencies:

```powershell
npm install
```

Install backend dependencies in the project virtual environment:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run locally

### 1. Start the backend API

From the repository root:

```powershell
.\venv\Scripts\python.exe -m backend.app
```

The Flask API runs at `http://127.0.0.1:5000`.

### 2. Start the frontend

In a second terminal:

```powershell
npm run dev
```

Open `http://localhost:5173`.

The frontend uses mock data by default, so the dashboard can be reviewed without a running backend. This is controlled in `src/store.js`:

```js
const USE_MOCK = true
```

Set it to `false` when the backend integration is ready. API calls are centralized in `src/services/api.js`; live events are handled in `src/services/socket.js`.

## Testing

Run the complete backend test suite:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Expected result:

```text
19 passed
```

The tests cover fuzzy risk scoring, rule evaluation, API endpoints, movement prediction, patrol routing, and spatial behavior.

Build the frontend:

```powershell
npm run build
```

Preview the production build:

```powershell
npm run preview
```

## Project structure

```text
backend/                 Flask API and risk-analysis modules
frontend/src/            Static frontend prototype
src/                     React dashboard
tests/                   Python test suite
requirements.txt         Python dependencies
package.json             Node scripts and dependencies
```

## Current validation status

- Backend tests: passing, 19 tests
- Frontend production build: passing
- Flask API smoke checks: passing
- Frontend dashboard: connected to the Flask API
- Backend API: port 5000
- Vite frontend: port 5173

The React dashboard loads its data from `GET /api/dashboard`, uses the Flask API
through the Vite proxy, and sends verified sightings and cycle advances back to
the backend. Start both processes for the complete integrated workflow.
