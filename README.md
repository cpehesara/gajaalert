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

The frontend uses mock data by default, so the dashboard can be reviewed without a running backend. In mock mode, sightings and cycle advances are local to the browser session. To use the Flask API instead, set `VITE_USE_MOCK_DATA=false` in a `.env` file at the repository root, then restart Vite. The backend must be running on `http://127.0.0.1:5000` for live mode.

```env
VITE_USE_MOCK_DATA=false
```

API calls are centralized in `src/services/api.js`; live events are handled in `src/services/socket.js`.

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
- Frontend dashboard: mock data by default; set `VITE_USE_MOCK_DATA=false` to connect to the Flask API
- Backend API: port 5000
- Vite frontend: port 5173

The React dashboard loads its data from `GET /api/dashboard`, uses the Flask API
through the Vite proxy, and sends verified sightings and cycle advances back to
the backend. Start both processes for the complete integrated workflow.
