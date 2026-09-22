"""Flask API for the GajaAlert prototype."""

from flask import Flask, jsonify, request
from flask_cors import CORS

from .fuzzy import compute_risk_score, evaluate_zone_risk_from_tables
from .rules.rule_engine import evaluate_rules
from .spatial.astar import get_patrol_route
from .spatial.markov_model import predict_movement
from .tables.officer_reports_table import officer_reports
from .tables.zone_table import zone_data
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent
with (ROOT / "data" / "zones.json").open(encoding="utf-8") as handle:
    spatial_zones = {zone["zone_id"]: zone for zone in json.load(handle)}
with (ROOT / "data" / "movement_history.json").open(encoding="utf-8") as handle:
    movement_history = json.load(handle)
cycle_number = max(item["timestamp_cycle"] for item in movement_history)
activity_log = []

app = Flask(__name__)
CORS(app)


@app.post("/api/rules")
def rules_endpoint():
    data = request.get_json(silent=True) or {}
    return jsonify({"risk": evaluate_rules(data.get("sighting_freq"), data.get("distance"), data.get("time_of_day"), data.get("season"))})


@app.post("/api/fuzzy-risk")
def fuzzy_endpoint():
    data = request.get_json(silent=True) or {}
    if "zone_id" in data and all(key not in data for key in ("sighting_freq", "distance_km", "time_of_day", "seasonal_risk")):
        return jsonify(evaluate_zone_risk_from_tables(data["zone_id"], data.get("target_time")))
    required = ("sighting_freq", "distance_km", "time_of_day", "seasonal_risk")
    if any(key not in data for key in required):
        return jsonify({"error": "missing fuzzy input"}), 400
    return jsonify(compute_risk_score(*(data[key] for key in required), data.get("zone_id")))


@app.post("/api/predict-movement")
def movement_endpoint():
    return jsonify(predict_movement((request.get_json(silent=True) or {}).get("zone_id", "")))


@app.post("/api/patrol-route")
def route_endpoint():
    data = request.get_json(silent=True) or {}
    return jsonify(get_patrol_route(data.get("start_zone", "Z01"), data.get("priority_zones", [])))


@app.post("/api/officer-update")
def officer_update_endpoint():
    report = request.get_json(silent=True) or {}
    report["verified"] = True
    officer_reports.append(report)
    return jsonify(report), 201


@app.get("/api/zones")
def zones_endpoint():
    return jsonify([
        {"id": zone_id, "name": zone["name"], "level": "high" if zone["flood_prone"] else "moderate",
         "center": [zone["lat"], zone["lng"]]}
        for zone_id, zone in spatial_zones.items()
    ])


def _herds():
    latest = {}
    for item in movement_history:
        herd_id = item["sighting_id"].split("-")[-1]
        if item["timestamp_cycle"] <= cycle_number:
            latest[herd_id] = item
    return [
        {"id": herd_id.upper(), "name": f"Herd {herd_id.upper()}", "size": item["elephant_count"],
         "zone": spatial_zones[item["zone_id"]]["name"], "source": item["source"],
         "lat": spatial_zones[item["zone_id"]]["lat"], "lng": spatial_zones[item["zone_id"]]["lng"]}
        for herd_id, item in latest.items()
    ]


def _risk_register(herds):
    counts = defaultdict(int)
    for herd in herds:
        for zone_id, zone in spatial_zones.items():
            if zone["name"] == herd["zone"]:
                counts[zone_id] += herd["size"]
    rows = []
    for zone_id, zone in spatial_zones.items():
        score = compute_risk_score(counts[zone_id], 2 if zone["flood_prone"] else 8, 22, 70, zone_id)
        rows.append({"zone": f"{zone_id} · {zone['name']}", "risk": score["risk_score"],
                     "level": score["risk_level"], "herds": counts[zone_id],
                     "forecastPressure": 0, "triggeredRules": "—"})
    return sorted(rows, key=lambda row: row["risk"], reverse=True)


def _dashboard():
    herds = _herds()
    register = _risk_register(herds)
    priority = [row["zone"].split(" · ")[0] for row in register[:4]]
    route = get_patrol_route("Z01", priority, graph={key: value["neighbors"] for key, value in spatial_zones.items()})
    return {
        "meta": {"cycle": cycle_number, "windowLabel": "Night window · Dry season",
                 "officer": {"name": "K. A. Bandara", "role": "Wildlife Ranger · DWC-2280"}},
        "situationSummary": {"herdsTracked": len(herds), "individuals": sum(h["size"] for h in herds),
                             "highCriticalZones": sum(row["level"] == "High" for row in register),
                             "verifiedSightings": sum(item.get("verified", False) for item in movement_history)},
        "herds": herds, "forecast": _forecast(herds[0]["id"] if herds else ""),
        "patrolRecommendation": {"route": route["route"], "originLabel": spatial_zones["Z01"]["name"],
                                 "distanceKm": route["total_distance_km"], "zoneCount": len(route["route"]),
                                 "note": "cost-weighted toward the highest-risk zones"},
        "zoneRiskRegister": register, "activityLog": activity_log[-10:][::-1],
        "zones": [{"id": key, "name": value["name"], "level": "high" if value["flood_prone"] else "moderate",
                   "center": [value["lat"], value["lng"]]} for key, value in spatial_zones.items()]
    }


def _forecast(herd_id):
    herd = next((item for item in _herds() if item["id"] == herd_id), None)
    if not herd:
        return {"herdId": "—", "herdName": "No herds", "currentZone": "—", "horizonHours": 12,
                "probabilities": [], "mostLikelyPath": []}
    zone_id = next(key for key, value in spatial_zones.items() if value["name"] == herd["zone"])
    prediction = predict_movement(json.load((ROOT / "data" / "transition_matrix.json").open()), zone_id, spatial_zones)
    probabilities = [{"zone": f"{key} · {spatial_zones[key]['name']}", "probability": value}
                     for key, value in prediction["predicted_transitions"].items()]
    return {"herdId": herd_id, "herdName": herd["name"], "currentZone": herd["zone"], "horizonHours": 12,
            "probabilities": probabilities, "mostLikelyPath": [zone_id] + [item["zone"].split(" · ")[0] for item in probabilities[:2]]}


@app.get("/api/dashboard")
def dashboard_endpoint():
    return jsonify(_dashboard())


@app.get("/api/forecast/<herd_id>")
def forecast_endpoint(herd_id):
    return jsonify(_forecast(herd_id))


@app.post("/api/cycle/advance")
def cycle_endpoint():
    global cycle_number
    cycle_number += 1
    activity_log.append({"time": "now", "text": "Cycle advanced (+6h) · movement, risk and patrol recomputed"})
    return jsonify({"cycle": cycle_number})


if __name__ == "__main__":
    app.run(debug=True)