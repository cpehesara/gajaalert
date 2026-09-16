"""Flask API for the GajaAlert prototype."""

from flask import Flask, jsonify, request
from flask_cors import CORS

from .fuzzy import compute_risk_score, evaluate_zone_risk_from_tables
from .rules.rule_engine import evaluate_rules
from .spatial.astar import get_patrol_route
from .spatial.markov_model import predict_movement
from .tables.officer_reports_table import officer_reports
from .tables.zone_table import zone_data

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
    return jsonify(zone_data)


if __name__ == "__main__":
    app.run(debug=True)