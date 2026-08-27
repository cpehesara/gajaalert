# GajaAlert — Full Development & Integration Roadmap
### A Week-by-Week Guide for All Four Members, From Setup to Demo-Ready Deployment

This roadmap exists to solve the single biggest risk in a four-person, four-module group project: **each person's code works perfectly in isolation, but the pieces don't fit together when you try to integrate them in Week 7.** Every section below is written specifically to prevent that failure mode — by agreeing on data formats *before* anyone starts coding, testing each module against those formats continuously, and integrating early and often instead of all at once at the end.

---

## Part 0 — Before Anyone Writes a Single Line of Code (Pre-Week 1)

This part is done **together, as a group, in one sitting.** Skipping it is the #1 cause of late-stage integration failure.

### 0.1 Agree on the Shared Data Contracts First

The four modules only work together if they agree on the *exact shape* of the data passing between them. Get this wrong and you'll spend Week 7 debugging "why is this field missing" instead of testing actual logic. Write these down in a shared document (e.g., a `SCHEMA.md` file in the repo root) and treat it as law — nobody changes a field name without telling the other three.

**Zone object (used by Rule-Based, Fuzzy, Markov, and A* modules):**
```json
{
  "zone_id": "Z07",
  "name": "Village A",
  "lat": 7.9821,
  "lng": 80.3120,
  "distance_to_corridor_km": 1.4,
  "distance_to_water_km": 0.6,
  "flood_prone": false,
  "neighbors": { "Z06": 2.4, "Z08": 3.1 }
}
```

**Sighting/position record (used by Rule-Based, Fuzzy, and Markov modules):**
```json
{
  "sighting_id": "S001",
  "zone_id": "Z03",
  "timestamp": "2026-08-10T19:30:00",
  "elephant_count": 3,
  "source": "simulated",
  "verified": false
}
```

**Risk score object (output of Fuzzy module, input to Markov and A*):**
```json
{
  "zone_id": "Z07",
  "risk_score": 84,
  "risk_level": "High",
  "contributing_factors": ["high sighting frequency", "near corridor", "night"]
}
```

**Movement prediction object (output of Markov module, input to A*):**
```json
{
  "zone_id": "Z07",
  "current_probability": 0.55,
  "predicted_transitions": { "Z06": 0.30, "Z08": 0.15 },
  "predicted_risk_window_hours": 6
}
```

**Patrol route object (output of A* module, input to frontend):**
```json
{
  "route": ["Z07", "Z08", "Z09"],
  "total_distance_km": 12.4,
  "estimated_time_minutes": 95
}
```

**Why this matters:** if the Fuzzy Lead decides `risk_level` should be lowercase (`"high"`) but the Spatial Search Lead's Markov module checks for `"High"`, the whole pipeline silently breaks with no error message — it just produces wrong results. Agreeing on exact field names, capitalization, and types *now* prevents this.

### 0.2 Agree on the Repository Structure

```
gajaalert/
├── backend/
│   ├── app.py                  # Flask entry point (Integration Lead)
│   ├── rules/                  # Rule-Based Lead's module
│   │   ├── rule_engine.py
│   │   └── rules_table.py
│   ├── fuzzy/                  # Fuzzy Lead's module
│   │   ├── fuzzy_engine.py
│   │   └── membership_functions.py
│   ├── spatial/                # Spatial Search Lead's module
│   │   ├── zone_graph.py
│   │   ├── gis_extract.py
│   │   ├── movement_sim.py
│   │   ├── markov_model.py
│   │   └── astar.py
│   └── data/
│       ├── zones.json
│       ├── sightings.json
│       └── movement_history.json
├── frontend/                   # Integration Lead + whoever helps
│   └── src/
├── tests/
│   ├── test_rules.py
│   ├── test_fuzzy.py
│   ├── test_spatial.py
│   └── test_integration.py
├── requirements.txt
└── README.md
```

Agree on this on Day 1. Everyone creates their folder immediately, even empty, so nobody's first commit causes a merge conflict over folder creation.

### 0.3 Set Up a Shared Python Environment

```bash
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install flask scikit-fuzzy numpy osmnx geopandas folium pytest
pip freeze > requirements.txt
```

Commit `requirements.txt` immediately. Every member runs `pip install -r requirements.txt` before writing code — this alone prevents the classic "works on my machine" failure on demo day.

### 0.4 Agree on the Git Workflow

- `main` branch is always demo-ready. Nobody pushes directly to it.
- Each member works on their own branch: `feature/rule-engine`, `feature/fuzzy-logic`, `feature/spatial-search`, `feature/backend-integration`.
- Pull requests get reviewed by at least one other member before merging — even a 2-minute glance catches obvious schema mismatches early.
- Merge into `main` at the **end of every week**, not just before deadlines. A module that hasn't been merged in three weeks is a module nobody has actually tested against the others.

---

## Part 1 — Individual Roadmaps by Member

Each member's roadmap below is structured the same way: **what to build, in what order, how to test it in isolation, and exactly what to hand off to the rest of the team.** Following the "test in isolation, then hand off a clean interface" pattern for all four modules is what prevents integration-week chaos.

---

### 1.1 DMNC Dissanayaka — Rule-Based AI Lead

**Mission:** produce a clean function that takes a sighting + context and returns an explainable risk flag.

**Week 1–2 (Foundations):**
- Get comfortable with Python dictionaries and if/elif structures.
- Read Fernando et al. (2005) on Sri Lankan HEC patterns — this gives you *real* domain justification for your rules instead of guessed thresholds.
- Draft the rule table on paper first (as in Appendix A of the proposal) before writing any code. Get it reviewed by the group.

**Week 3–4 (Build the core engine):**
- Implement rules as a list of dictionaries, not nested if-statements — this keeps them inspectable and editable:
```python
RULES = [
    {"sighting": "High", "distance": "Near", "time": "Night", "season": "High", "risk": "High"},
    {"sighting": "Low", "distance": "Far", "time": "Day", "season": "Low", "risk": "Low"},
    # ...
]

def evaluate_rules(sighting_freq, distance, time_of_day, season):
    for rule in RULES:
        if (rule["sighting"] == sighting_freq and rule["distance"] == distance
                and rule["time"] == time_of_day and rule["season"] == season):
            return rule["risk"]
    return "Undetermined"  # IMPORTANT: never let this fall through silently
```
- **Critical error-prevention step:** decide explicitly what happens when no rule matches (a very likely scenario once real/simulated data produces combinations you didn't anticipate). Returning `"Undetermined"` and logging it is far safer than crashing or silently returning `None`, which would break the Fuzzy module downstream.

**Week 5 (Test in isolation):**
- Write `tests/test_rules.py` covering: every rule in your table fires correctly, an unmatched combination returns `"Undetermined"` without crashing, and boundary inputs (e.g., missing `season` field) are handled gracefully.
- Test with at least 10 sample inputs drawn from realistic scenarios your group agrees on.

**Week 6–7 (Handoff):**
- Deliver a single function `evaluate_rules(sighting_freq, distance, time_of_day, season) -> str` that the Fuzzy Lead and Integration Lead can call directly.
- Write a short `README.md` inside `rules/` explaining the function signature and every possible return value.
- **Do not let your module import anything from `fuzzy/` or `spatial/`** — keep it a pure, standalone function so it can be tested and reused without needing the rest of the system running.

**Common pitfalls to avoid:**
- Hardcoding rule values as separate variables instead of a structured table — this makes the rule base impossible to inspect or explain in your viva.
- Case-sensitivity mismatches (`"high"` vs `"High"`) between your rules and what the Fuzzy/Spatial modules send you — agree on exact casing in Part 0.1 and stick to it.
- Forgetting to test what happens with completely missing fields (e.g., a sighting record with no `season` key) — this will happen with real simulated data eventually.

---

### 1.2 KDTH Senadeera — Fuzzy Systems Lead

**Mission:** produce a function that converts raw risk indicators into a graded, defensible risk score.

**Week 1–2 (Foundations):**
- Learn fuzzy set theory basics: membership functions, fuzzification, defuzzification.
- Work through the scikit-fuzzy "tipping problem" tutorial end-to-end before touching your own variables — it's structurally almost identical to what you need to build.

**Week 3–4 (Design membership functions):**
- Define each input variable's membership functions on paper first, reviewed by the group, before coding:

| Variable | Low/Near/Day | Medium | High/Far/Night |
|---|---|---|---|
| Sighting frequency (per week) | 0–2 | 2–5 | 5+ |
| Distance to corridor (km) | 0–1 | 1–3 | 3+ |
| Time of day | — | dusk (17:00–19:00) | night (19:00–06:00) |

- Implement using `scikit-fuzzy`:
```python
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

sighting = ctrl.Antecedent(np.arange(0, 11, 1), 'sighting')
distance = ctrl.Antecedent(np.arange(0, 6, 0.1), 'distance')
risk = ctrl.Consequent(np.arange(0, 101, 1), 'risk')

sighting['low'] = fuzz.trimf(sighting.universe, [0, 0, 3])
sighting['medium'] = fuzz.trimf(sighting.universe, [2, 5, 8])
sighting['high'] = fuzz.trimf(sighting.universe, [6, 10, 10])
# repeat for distance, time, season...
```

**Week 5–6 (Build the rule base and test):**
- Encode the fuzzy rules from Appendix A of the proposal.
- **Critical error-prevention step:** test edge values specifically — a sighting frequency of exactly 0, exactly at a boundary between "Low" and "Medium", and unusually high values (e.g., 50 sightings) that fall outside your expected range. Fuzzy systems can silently produce `NaN` outputs when inputs fall outside the universe you defined — this is one of the most common last-minute crashes in student fuzzy logic projects.
- Write `tests/test_fuzzy.py` with at least 8 scenarios covering low/medium/high combinations and boundary values.

**Week 7 (Handoff):**
- Deliver a function `compute_risk_score(sighting_freq, distance_km, time_of_day, seasonal_risk) -> dict` returning the exact `risk score object` schema agreed in Part 0.1.
- Confirm with the Spatial Search Lead that your output's `risk_level` casing exactly matches what their Markov module expects.

**Common pitfalls to avoid:**
- Leaving a gap between membership functions (e.g., "Low" ends at 3, "Medium" starts at 5) — inputs of 4 would then have zero membership anywhere, producing undefined behaviour. Always overlap adjacent membership functions.
- Not clipping or validating input ranges before passing them to scikit-fuzzy — out-of-range inputs are a common source of `NaN` results that only show up during live testing, not unit testing with "nice" numbers.
- Returning a raw NumPy float instead of a plain Python float/int in your output dict — this can cause silent JSON serialization errors later in the Flask API.

---

### 1.3 KMCP Munasinghe — Spatial Search Lead

**Mission:** build the geographic foundation (zone graph), the movement simulation, the Markov prediction, and the A* routing — the largest and most technically varied module, so break it into four clearly separated sub-stages.

**Week 1–2 (Foundations):**
- Get comfortable with `heapq`, graph representations (adjacency dictionaries), and basic coordinate geometry (Euclidean distance).
- Install and test `osmnx`, `geopandas`, `folium` early — these have real installation friction (compiled dependencies), so do this in Week 1, not Week 5, to leave time to troubleshoot.

**Week 2–3 (GIS extraction — do this first, everything else depends on it):**
```python
import osmnx as ox

place = "Galgamuwa, Kurunegala District, Sri Lanka"
roads = ox.graph_from_place(place, network_type="drive")
water = ox.features_from_place(place, tags={"natural": "water"})
buildings = ox.features_from_place(place, tags={"building": True})
```
- **Critical error-prevention step:** OSM data for smaller Sri Lankan divisions can be sparse or inconsistently tagged. Before building anything else, manually inspect the extracted road/water/building data in `folium` and confirm it actually covers your target area sensibly. If OSM coverage is too thin for Galgamuwa specifically, expand to a wider bounding box or supplement manually — discover this in Week 2, not Week 8.
- Convert the extracted road network into your agreed zone-graph JSON schema (Part 0.1). This is the single most important handoff artifact in the whole project — the Rule-Based, Fuzzy, and A* modules all depend on `zones.json` existing in the correct format.

**Week 3–4 (Build and freeze the zone graph):**
- Simplify the full OSM road graph down to 10–15 representative zones (GN division centres). Don't try to model all 62 GN divisions — it adds complexity without adding marks.
- Write the zone graph as a static `zones.json` file and **commit it to the shared repo by end of Week 4.** Every other module needs this file to exist before they can test against real zone IDs instead of placeholder data.

**Week 4–5 (A* search — build this before the movement simulation, since it's simpler and validates your zone graph):**
```python
import heapq

def astar(graph, coords, start, goal):
    open_set = [(0, start, [start])]
    g_score = {start: 0}
    while open_set:
        f, current, path = heapq.heappop(open_set)
        if current == goal:
            return path, g_score[current]
        for neighbor, weight in graph[current].items():
            tentative_g = g_score[current] + weight
            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                h = euclidean(coords[neighbor], coords[goal])
                heapq.heappush(open_set, (tentative_g + h, neighbor, path + [neighbor]))
    return None, float("inf")  # IMPORTANT: handle unreachable zones explicitly
```
- **Critical error-prevention step:** test A* against a zone that is disconnected from the rest of the graph (no path exists). Returning `None` explicitly and having the caller handle it gracefully prevents a crash when your real OSM-derived graph inevitably has a poorly-connected zone somewhere.
- Test with multiple start/goal pairs, and test the sequential multi-zone version (visiting several high-risk zones in one patrol) before moving on.

**Week 5–7 (Movement simulation and Markov chain):**
```python
import numpy as np

def correlated_random_walk_step(current_zone, prev_heading, zone_graph, attractiveness_fn):
    neighbors = list(zone_graph[current_zone].keys())
    weights = [attractiveness_fn(z) for z in neighbors]
    weights = np.array(weights) / sum(weights)  # normalize — never skip this
    return np.random.choice(neighbors, p=weights)
```
- **Critical error-prevention step:** always normalize your weights before passing them to `np.random.choice` — unnormalized probabilities that don't sum to 1 will raise a runtime error, and this is a very common last-minute bug when attractiveness scores come from real, messy GIS data.
- Run the simulation for enough cycles (e.g., 200+ steps across several herds) to build a transition matrix with enough data to be meaningful — too few simulated steps produces a Markov matrix full of zeros and unreliable predictions.
- Build the transition matrix as a nested dictionary matching your agreed schema, and test that every row's probabilities sum to 1 (a simple but essential sanity check).

**Week 7 (Integration prep):**
- Combine fuzzy risk scores with Markov predictions to produce the final prioritized zone list that feeds A*.
- Deliver three clean functions to the Integration Lead: `get_patrol_route(start_zone, priority_zones) -> dict`, `predict_movement(zone_id) -> dict`, and `run_simulation_cycle() -> None` (updates the shared dataset).

**Common pitfalls to avoid:**
- Building the movement simulation before the zone graph is finalized — any zone ID changes afterward will silently break your transition matrix references.
- Forgetting that A* heuristics must be admissible — using route-network distance instead of straight-line distance as your heuristic will produce non-optimal routes without raising any error, which is far more dangerous than a crash because it fails silently.
- Not handling the case where `priority_zones` is empty (e.g., every zone is currently Low risk) — decide explicitly what the patrol route should be in that case (e.g., a default sweep route) rather than letting A* be called with no destination.

---

### 1.4 SD Mallikarachchi — Systems & Integration Lead

**Mission:** wire all three other modules together behind a working API and a functioning dashboard, and own the end-to-end testing that catches integration errors before demo day.

**Week 1–2 (Foundations):**
- Get comfortable with Flask basics: routes, JSON request/response handling, running a local dev server.
- Set up the skeleton Flask app and the four planned endpoints as stubs returning hardcoded sample data, **before** any other module is ready:
```python
from flask import Flask, jsonify, request
app = Flask(__name__)

@app.route("/api/rules", methods=["POST"])
def rules_endpoint():
    return jsonify({"risk": "High"})  # placeholder — swap in real module later

@app.route("/api/fuzzy-risk", methods=["POST"])
def fuzzy_endpoint():
    return jsonify({"zone_id": "Z07", "risk_score": 50, "risk_level": "Medium"})

@app.route("/api/predict-movement", methods=["POST"])
def predict_endpoint():
    return jsonify({"zone_id": "Z07", "predicted_transitions": {}})

@app.route("/api/patrol-route", methods=["POST"])
def route_endpoint():
    return jsonify({"route": ["Z01", "Z02"], "total_distance_km": 5.0})
```
- **Why this matters:** this lets the frontend (and the other three members) start integrating against a *real, running API* from Week 2 onward, instead of waiting until Week 7 when every module is "supposedly" done. This single decision prevents the most common group-project failure: four people integrating for the first time the week before a deadline.

**Week 2–4 (React frontend skeleton):**
- Build the dashboard's static layout first: zone grid, risk color-coding, route display area, manual override form — using the placeholder API responses above.
- This lets frontend work proceed in parallel with everyone else's backend work, rather than blocking on it.

**Week 5–7 (Swap in real modules as they become ready):**
- As each teammate delivers their function, replace the placeholder in the corresponding endpoint:
```python
from rules.rule_engine import evaluate_rules
from fuzzy.fuzzy_engine import compute_risk_score
from spatial.astar import get_patrol_route
from spatial.markov_model import predict_movement

@app.route("/api/fuzzy-risk", methods=["POST"])
def fuzzy_endpoint():
    data = request.json
    result = compute_risk_score(data["sighting_freq"], data["distance_km"],
                                  data["time_of_day"], data["seasonal_risk"])
    return jsonify(result)
```
- **Critical error-prevention step:** integrate one module at a time, and re-run the full test suite after each swap. If you swap in all three modules at once and something breaks, you won't know which one caused it.
- Build the officer manual-override endpoint (`POST /api/officer-update`) and make sure it correctly sets `verified: true` and overrides simulated data for that zone/time — test this specifically, since it's the one place where two different data sources (simulation and human input) can conflict.

**Week 7–8 (End-to-end integration testing — this is your most important responsibility):**
- Run the full pipeline manually with at least 5 realistic scenarios: a quiet week (all Low risk), an active corridor zone at night during harvest season, a zone with no historical data at all, a disconnected/edge-case zone, and an officer-submitted override that should take precedence over simulated data.
- Confirm the numbers flowing between modules actually make sense end-to-end — e.g., that a "High" risk zone from the Fuzzy module actually appears in the priority list passed to A*, and that A*'s route actually visits it.

**Week 9 (Hardening and demo preparation):**
- Add basic error handling to every endpoint (try/except around each module call, returning a clear JSON error message rather than a raw Flask 500 stack trace) — see Part 3 below.
- Prepare a **offline demo fallback**: a pre-saved set of realistic API responses that can be served if live GIS data fetching or any module fails during the actual presentation. Never rely on live external services (like the OSM API) working perfectly on demo day.

**Common pitfalls to avoid:**
- Waiting until all four modules are "finished" before connecting anything — integrate incrementally from Week 2, not all at once in Week 7.
- Not validating incoming JSON request shapes — a missing field in a request body should return a clear 400 error, not crash the server.
- CORS issues between the React frontend and Flask backend, which are easy to fix early (`flask-cors`) and painful to debug last-minute.

---

## Part 2 — The Master Integration Timeline (All Four Members Together)

| Week | Rule-Based Lead | Fuzzy Lead | Spatial Search Lead | Integration Lead |
|---|---|---|---|---|
| Pre–1 | Python/Git basics | Python/Git basics | Python/Git basics + install osmnx/geopandas | Python/Git basics + Flask setup |
| 1–2 | Draft rule table | Study scikit-fuzzy tutorial | Extract & validate GIS data for Galgamuwa | Build Flask skeleton with 4 stub endpoints |
| 3–4 | Implement rule engine | Define membership functions | **Finalize and commit `zones.json`** | Build React dashboard against stub data |
| 5 | Unit test rule engine | Implement fuzzy rule base | Implement & test A* on `zones.json` | Wire real rule engine into `/api/rules` |
| 6 | Handoff to Fuzzy/Integration | Unit test fuzzy engine | Build movement simulation | Wire real fuzzy engine into `/api/fuzzy-risk` |
| 7 | Support integration testing | Handoff to Spatial/Integration | Build Markov model + handoff | Integrate A* and Markov modules |
| 8 | **Progress Review submission** (all members) | | | Full pipeline demo for Progress Review |
| 9 | Support scenario testing | Support scenario testing | Support scenario testing | End-to-end testing, error handling, offline fallback |
| 10 | **Final submission & presentation** (all members) | | | |

The single row that matters most for avoiding late failures is **Week 4: "Finalize and commit `zones.json`."** Every other module's testing becomes meaningless against placeholder zone IDs — the whole team should treat this file's completion as a hard internal deadline, even though it isn't one of the module's official deliverables.

---

## Part 3 — System-Wide Testing Strategy

Testing happens in three layers. Skipping the middle layer (integration testing) is exactly what causes projects to "work" individually but fail when demoed together.

### 3.1 Unit Testing (each member, ongoing from the week their module starts)
Each member tests their own function in complete isolation, with no dependency on Flask, the frontend, or anyone else's code running. Use `pytest`:
```bash
pytest tests/test_rules.py -v
pytest tests/test_fuzzy.py -v
pytest tests/test_spatial.py -v
```

### 3.2 Integration Testing (Integration Lead, from Week 5 onward, growing weekly)
Test that data passed from one module is correctly consumed by the next:
- Rule engine output → does the Fuzzy module accept it without a type error?
- Fuzzy risk score → does the Markov module correctly identify it as high/medium/low?
- Markov prediction → does A* receive a non-empty, valid zone list?
- A* route → does the frontend render it without crashing on an empty or single-zone route?

### 3.3 End-to-End Scenario Testing (whole team, Week 9)
Run these five scenarios through the *entire* pipeline and manually verify the output is sensible:

| Scenario | What it tests |
|---|---|
| Quiet week, all zones Low risk | System doesn't force a false alarm; A* still returns a sensible default route |
| High sighting frequency near corridor at night, harvest season | Full pipeline correctly escalates to High risk and prioritizes that zone in the route |
| Zone with zero historical sighting data | Rule/Fuzzy modules don't crash on missing/zero data; Markov handles a zone with no transition history |
| Disconnected or poorly-connected zone in the graph | A* returns a graceful "unreachable" result rather than crashing |
| Officer submits a verified sighting that contradicts the simulation | Officer data correctly overrides simulated data for that zone and time window |

### 3.4 Pre-Demo Checklist (run this the day before presenting)
- [ ] `pip install -r requirements.txt` works on a clean environment (test on a laptop that hasn't been used for development, if possible)
- [ ] The Flask server starts without errors: `python backend/app.py`
- [ ] All five end-to-end scenarios above still pass
- [ ] The offline fallback dataset is ready in case live GIS fetching fails during the demo
- [ ] Every team member can explain every module, not just their own — a lecturer's question can land on anyone
- [ ] The GitHub repo's `README.md` has clear run instructions, in case someone else needs to run it

---

## Part 4 — Common System-Wide Errors and How to Prevent Each One

| Error class | Where it usually appears | Prevention |
|---|---|---|
| Field name/casing mismatch | Between any two modules | Enforce the schemas in Part 0.1 — never change a field name without a group message |
| Silent `NaN` or `None` propagation | Fuzzy module, Markov module | Validate inputs at every function boundary; never let an undefined value silently flow downstream |
| Unnormalized probability weights | Movement simulation | Always divide by the sum before passing to `np.random.choice` |
| Non-admissible A* heuristic | Spatial search | Always use straight-line distance, never route-network distance, as the heuristic |
| Disconnected graph nodes | Spatial search / A* | Explicitly test and handle the "no path found" case |
| JSON serialization crashes | Flask endpoints | Convert NumPy types (`np.float64`, `np.int64`) to native Python types before returning from any function |
| CORS errors | Frontend–backend communication | Install and configure `flask-cors` in Week 2, not Week 9 |
| "Works on my machine" | Demo day | Everyone installs from the same committed `requirements.txt`; test on a clean machine before presenting |
| Merge conflicts on shared data files | `zones.json`, `sightings.json` | Only the Spatial Search Lead edits `zones.json` after Week 4; treat it as read-only for everyone else |
| Live external API failure during demo | GIS/OSM fetching | Pre-fetch and cache all GIS data locally by Week 4; never call the live OSM API during the actual presentation |

---

## Final Note

The single habit that prevents almost every error in this list is **integrating early and often, in small pieces, rather than saving it for the end.** A module that has never been run alongside the other three is a module nobody has actually tested — no matter how well it works on its own. Treat Week 5 through Week 7 as the real core of the project, not the proposal-writing weeks that came before it.
