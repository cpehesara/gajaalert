"""Flask API for GajaAlert.

Live pipeline on every dashboard request:
  simulated + officer-verified herd positions
    -> rule engine (explainable flag)  -> fuzzy HEC risk score
    -> Markov forecast pressure        -> zone priority + early warning
    -> nearest-first A* patrol route
"""

import json
import threading
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from .fuzzy import compute_risk_score, evaluate_zone_risk_from_tables
from .fuzzy.fuzzy_engine import _seasonal_value
from .rules import zone_flagger as zf
from .rules.rule_engine import evaluate_rules, get_matching_rules
from .spatial.astar import plan_patrol_route
from .spatial.markov_model import build_transition_matrix, predict_movement
from .spatial.movement_sim import crw_step
from .tables.officer_reports_table import officer_reports
from .tables.weather_table import get_latest_weather, weather_data

ROOT = Path(__file__).resolve().parent
REPORTS_FILE = ROOT / "data" / "officer_reports.json"

HOURS_PER_CYCLE = 6          # one Markov step = one cycle = 6 simulated hours
WINDOW_CYCLES = 28           # "recent" window = 7 days
BASE_ZONE = "Z01"            # patrol departs from Galgamuwa Town
OFFICER = {"id": "DWC-2280", "name": "K. A. Bandara", "role": "Wildlife Ranger · DWC-2280"}  # demo login

# ---------------------------------------------------------------- state
with (ROOT / "data" / "zones.json").open(encoding="utf-8") as handle:
    spatial_zones = {zone["zone_id"]: zone for zone in json.load(handle)}
with (ROOT / "data" / "movement_history.json").open(encoding="utf-8") as handle:
    movement_history = json.load(handle)

cycle_number = max(item["timestamp_cycle"] for item in movement_history)
BASE_CYCLE = cycle_number
# Simulated clock: real time at start-up, +6 h per cycle advance.
CLOCK_ANCHOR = datetime.now().replace(minute=0, second=0, microsecond=0)
matrix = build_transition_matrix(movement_history)
activity_log = []
_lock = threading.Lock()

_submitted_reports = []
try:
    with REPORTS_FILE.open(encoding="utf-8") as handle:
        _submitted_reports = json.load(handle)
    officer_reports.extend(_submitted_reports)
except (OSError, ValueError):
    pass

app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------- helpers
def _sim_time():
    return CLOCK_ANCHOR + timedelta(hours=HOURS_PER_CYCLE * (cycle_number - BASE_CYCLE))


def _log(text):
    activity_log.append({"time": datetime.now().strftime("%I:%M:%S %p"), "text": text})


def _herd_id(key):
    return f"H{int(key[4:]) + 1:02d}"


def _herd_key(display_id):
    try:
        return f"herd{int(str(display_id).lstrip('Hh')) - 1}"
    except ValueError:
        return None


def _herd_state():
    """key -> {zone, previous (last different zone), size, source, verified}."""
    state = {}
    for item in sorted(movement_history, key=lambda r: r["timestamp_cycle"]):
        key = item["sighting_id"].split("-")[-1]
        entry = state.setdefault(key, {"zone": None, "previous": None})
        if entry["zone"] is not None and entry["zone"] != item["zone_id"]:
            entry["previous"] = entry["zone"]
        entry.update(zone=item["zone_id"], size=item["elephant_count"],
                     source=item["source"], verified=item.get("verified", False))
    return state


def _herds():
    return [{"id": _herd_id(key), "name": f"Herd {_herd_id(key)}", "size": e["size"],
             "zone": spatial_zones[e["zone"]]["name"], "zoneId": e["zone"], "source": e["source"],
             "lat": spatial_zones[e["zone"]]["lat"], "lng": spatial_zones[e["zone"]]["lng"]}
            for key, e in sorted(_herd_state().items())]


def _weather(zone_id):
    """Zone record if present, otherwise the most recent regional record."""
    return get_latest_weather(zone_id) or max(weather_data, key=lambda r: r["date"], default=None)


def _season_category(weather):
    drought = (weather or {}).get("drought_index", "Unknown")
    return {"Severe Drought": "High", "Dry": "High", "Normal": "Medium", "Wet": "Low"}.get(drought, "Medium")


def _report_time(report):
    try:
        return datetime.strptime(f"{report['date']} {report['time']}", "%Y-%m-%d %H:%M")
    except (KeyError, ValueError, TypeError):
        return None


def _recent_reports(zone_id):
    now = _sim_time()
    start = now - timedelta(days=7)
    found = []
    for report in officer_reports:
        when = _report_time(report)
        if report.get("zone_id") == zone_id and report.get("verified") and when and start <= when <= now:
            found.append((when, report))
    return [report for _, report in sorted(found, key=lambda pair: pair[0])]


def _arrival_counts():
    """Sightings per zone in the recent window: herd arrivals + standalone officer sightings."""
    counts = defaultdict(int)
    previous = {}
    for item in sorted(movement_history, key=lambda r: r["timestamp_cycle"]):
        key = item["sighting_id"].split("-")[-1]
        if item["timestamp_cycle"] > cycle_number - WINDOW_CYCLES and previous.get(key) != item["zone_id"]:
            counts[item["zone_id"]] += 1
        previous[key] = item["zone_id"]
    for zone_id in spatial_zones:
        counts[zone_id] += sum(1 for r in _recent_reports(zone_id)
                               if r.get("report_type") == "verified_sighting" and not r.get("herd_id"))
    return counts


def _assess_zone(zone_id, count, herds_here):
    now = _sim_time()
    weather = _weather(zone_id)
    season = _season_category(weather)
    distance = zf.categorize_distance(zone_id)
    time_of_day = zf.categorize_time(now)
    sighting = ("High" if count >= zf.SIGHTING_HIGH_MIN
                else "Medium" if count >= zf.SIGHTING_MEDIUM_MIN else "Low")
    rule_risk = evaluate_rules(sighting, distance, time_of_day, season)
    matched = get_matching_rules(sighting, distance, time_of_day, season)
    rule_id = matched[0]["id"] if matched else None

    km = spatial_zones[zone_id].get("distance_to_forest_km")
    fuzzy = compute_risk_score(count, 3.0 if km is None else km, now.hour + now.minute / 60,
                               _seasonal_value(weather), zone_id)
    factors = list(fuzzy["contributing_factors"])
    score, level = fuzzy["risk_score"], fuzzy["risk_level"]

    reports = _recent_reports(zone_id)
    if reports:
        factors.append("officer-verified report")
        last = reports[-1]
        if last.get("report_type") == "patrol_survey" and not last.get("number_of_elephants") and not herds_here:
            score, level, factors = 0, "Low", ["officer-verified clear patrol"]
    if rule_id:
        factors.append(f"rule {rule_id} → {rule_risk}")
    return {"score": score, "level": level, "rule_id": rule_id, "rule_risk": rule_risk,
            "factors": factors, "sighting": sighting, "distance": distance,
            "time": time_of_day, "season": season}


def _register(herds):
    counts = _arrival_counts()
    herds_in_zone = defaultdict(int)
    pressure = defaultdict(float)
    for herd in herds:
        herds_in_zone[herd["zoneId"]] += 1
        transitions = predict_movement(matrix, herd["zoneId"], spatial_zones)["predicted_transitions"]
        for zone_id, probability in transitions.items():
            pressure[zone_id] += probability

    rows = []
    for zone_id, zone in spatial_zones.items():
        a = _assess_zone(zone_id, counts[zone_id], herds_in_zone[zone_id])
        priority = 0.6 * a["score"] + 40 * min(1.0, pressure[zone_id])
        rows.append({
            "zone": f"{zone_id} · {zone['name']}", "zoneId": zone_id,
            "risk": a["score"], "level": "Moderate" if a["level"] == "Medium" else a["level"],
            "herds": herds_in_zone[zone_id], "forecastPressure": round(pressure[zone_id], 2),
            "triggeredRules": f"{a['rule_id']} → {a['rule_risk']}" if a["rule_id"] else "—",
            "priority": round(priority), "earlyWarning": a["level"] == "High" or priority >= 60,
            "factors": a["factors"],
        })
    return sorted(rows, key=lambda row: row["priority"], reverse=True)


def _forecast(herd_id, steps=2):
    herd = next((h for h in _herds() if h["id"] == herd_id), None)
    if not herd:
        return {"herdId": "—", "herdName": "No herds", "currentZone": "—", "horizonHours": HOURS_PER_CYCLE * steps,
                "probabilities": [], "mostLikelyPath": []}
    current = herd["zoneId"]
    distribution, path, cursor = {current: 1.0}, [current], current
    for _ in range(steps):
        following = defaultdict(float)
        for zone_id, mass in distribution.items():
            for target, p in predict_movement(matrix, zone_id, spatial_zones)["predicted_transitions"].items():
                following[target] += mass * p
        distribution = dict(following)
        options = predict_movement(matrix, cursor, spatial_zones)["predicted_transitions"]
        cursor = max(options.items(), key=lambda kv: kv[1], default=(cursor, 1.0))[0]
        path.append(cursor)
    ranked = sorted(distribution.items(), key=lambda kv: kv[1], reverse=True)
    return {"herdId": herd_id, "herdName": herd["name"], "currentZone": herd["zone"],
            "horizonHours": HOURS_PER_CYCLE * steps,
            "probabilities": [{"zone": f"{z} · {spatial_zones[z]['name']}", "probability": round(p, 3)}
                              for z, p in ranked[:5] if p > 0.01],
            "mostLikelyPath": path}


def _patrol(register):
    targets = [row["zoneId"] for row in register if row["priority"] >= 30 and row["zoneId"] != BASE_ZONE][:4]
    plan = plan_patrol_route(spatial_zones, BASE_ZONE, targets)
    return {"route": plan["route"], "originLabel": spatial_zones[BASE_ZONE]["name"],
            "distanceKm": round(plan["total_distance_km"], 1), "zoneCount": len(plan["route"]),
            "estimatedMinutes": int(round(plan["total_distance_km"] * 7.5)),
            "priorityZones": targets, "unreachedZones": plan["unreached_zones"],
            "note": "nearest-first A* through the highest-priority zones"}


def _zone_level(row):
    return {"High": "high", "Moderate": "moderate", "Low": "low"}.get(row["level"], "low")


def _dashboard():
    herds = _herds()
    register = _register(herds)
    now = _sim_time()
    weather = _weather(BASE_ZONE)
    season = (weather or {}).get("drought_index", "Unknown")
    return {
        "meta": {"cycle": cycle_number, "simTime": now.isoformat(timespec="minutes"),
                 "windowLabel": f"{zf.categorize_time(now)} window · {season} season",
                 "officer": {"name": OFFICER["name"], "role": OFFICER["role"]}},
        "situationSummary": {
            "herdsTracked": len(herds), "individuals": sum(h["size"] for h in herds),
            "highCriticalZones": sum(row["level"] == "High" for row in register),
            "earlyWarnings": sum(row["earlyWarning"] for row in register),
            "verifiedSightings": sum(1 for r in officer_reports if r.get("verified")
                                     and r.get("report_type") == "verified_sighting"
                                     and (_report_time(r) or datetime.min) >= now - timedelta(days=7))},
        "herds": herds, "forecast": _forecast(herds[0]["id"] if herds else ""),
        "patrolRecommendation": _patrol(register),
        "zoneRiskRegister": register, "activityLog": activity_log[-10:][::-1],
        "zones": [{"id": row["zoneId"], "name": spatial_zones[row["zoneId"]]["name"], "level": _zone_level(row),
                   "center": [spatial_zones[row["zoneId"]]["lat"], spatial_zones[row["zoneId"]]["lng"]]}
                  for row in register],
    }


# ---------------------------------------------------------------- module endpoints
@app.post("/api/rules")
def rules_endpoint():
    data = request.get_json(silent=True) or {}
    args = (data.get("sighting_freq"), data.get("distance"), data.get("time_of_day"), data.get("season"))
    matched = get_matching_rules(*args)
    return jsonify({"risk": evaluate_rules(*args), "triggered_by": matched[0]["id"] if matched else None})


@app.post("/api/fuzzy-risk")
def fuzzy_endpoint():
    data = request.get_json(silent=True) or {}
    required = ("sighting_freq", "distance_km", "time_of_day", "seasonal_risk")
    if "zone_id" in data and all(key not in data for key in required):
        try:
            return jsonify(evaluate_zone_risk_from_tables(data["zone_id"], data.get("target_time")))
        except ValueError as error:
            return jsonify({"error": str(error)}), 404
    if any(key not in data for key in required):
        return jsonify({"error": "missing fuzzy input"}), 400
    return jsonify(compute_risk_score(*(data[key] for key in required), data.get("zone_id")))


@app.post("/api/predict-movement")
def movement_endpoint():
    zone_id = (request.get_json(silent=True) or {}).get("zone_id", "")
    if zone_id not in spatial_zones:
        return jsonify({"error": f"unknown zone: {zone_id}"}), 404
    return jsonify(predict_movement(matrix, zone_id, spatial_zones))


@app.post("/api/patrol-route")
def route_endpoint():
    data = request.get_json(silent=True) or {}
    start = data.get("start_zone", BASE_ZONE)
    targets = data.get("priority_zones", [])
    unknown = [z for z in [start, *targets] if z not in spatial_zones]
    if unknown:
        return jsonify({"error": f"unknown zone(s): {unknown}"}), 404
    plan = plan_patrol_route(spatial_zones, start, targets)
    plan["estimated_time_minutes"] = int(round(plan["total_distance_km"] * 7.5))
    return jsonify(plan)


# ---------------------------------------------------------------- officer override
@app.post("/api/officer-update")
def officer_update_endpoint():
    global matrix
    data = request.get_json(silent=True) or {}
    zone_id = data.get("zone_id") or data.get("zoneId")
    if zone_id not in spatial_zones:
        return jsonify({"error": f"unknown zone: {zone_id}"}), 400
    try:
        count = int(data.get("number_of_elephants", data.get("observedSize", 0)))
    except (TypeError, ValueError):
        return jsonify({"error": "number of elephants must be a whole number"}), 400
    if count < 0:
        return jsonify({"error": "number of elephants cannot be negative"}), 400

    herd_display = data.get("herd_id") or data.get("herdId")
    key = _herd_key(herd_display) if herd_display else None
    with _lock:
        if herd_display and key not in _herd_state():
            return jsonify({"error": f"unknown herd: {herd_display}"}), 400
        now = _sim_time()
        report = {"report_id": f"OR{len(officer_reports) + 1:03d}", "officer_id": OFFICER["id"],
                  "zone_id": zone_id, "date": now.strftime("%Y-%m-%d"), "time": now.strftime("%H:%M"),
                  "report_type": "verified_sighting" if count > 0 else "patrol_survey",
                  "number_of_elephants": count, "notes": str(data.get("notes", ""))[:500],
                  "verified": True, "herd_id": herd_display or None}
        officer_reports.append(report)
        _submitted_reports.append(report)
        try:
            with REPORTS_FILE.open("w", encoding="utf-8") as handle:
                json.dump(_submitted_reports, handle, indent=2)
        except OSError:
            pass  # in-memory copy still applies this session

        if key and count > 0:  # verified position replaces the simulated one for this cycle
            own = [r for r in movement_history if r["sighting_id"].split("-")[-1] == key]
            latest = max(own, key=lambda r: r["timestamp_cycle"])
            latest.update(zone_id=zone_id, elephant_count=count, source="officer-verified", verified=True)
            matrix = build_transition_matrix(movement_history)
        _log(f"Officer {OFFICER['id']} verified {count} elephant(s) in {zone_id} · {spatial_zones[zone_id]['name']}"
             + (f" · {herd_display} position overridden" if key and count > 0 else ""))
    return jsonify(report), 201


# ---------------------------------------------------------------- dashboard endpoints
@app.get("/api/zones")
def zones_endpoint():
    return jsonify(_dashboard()["zones"])


@app.get("/api/dashboard")
def dashboard_endpoint():
    return jsonify(_dashboard())


@app.get("/api/forecast/<herd_id>")
def forecast_endpoint(herd_id):
    return jsonify(_forecast(herd_id))


@app.post("/api/cycle/advance")
def cycle_endpoint():
    global cycle_number, matrix
    with _lock:
        state = _herd_state()
        cycle_number += 1
        season = "dry" if _season_category(_weather(BASE_ZONE)) == "High" else "normal"
        for key, herd in state.items():
            movement_history.append({
                "sighting_id": f"SIM-{cycle_number}-{key}",
                "zone_id": crw_step(herd["zone"], spatial_zones, season, herd["previous"]),
                "timestamp_cycle": cycle_number, "elephant_count": herd["size"],
                "source": "simulated", "verified": False})
        matrix = build_transition_matrix(movement_history)
        _log(f"Cycle {cycle_number} · clock {_sim_time():%a %H:%M} · herds moved, "
             f"Markov matrix rebuilt, risk & patrol recomputed")
    return jsonify({"cycle": cycle_number})


if __name__ == "__main__":
    app.run(debug=True)