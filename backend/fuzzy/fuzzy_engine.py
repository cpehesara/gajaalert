"""Mamdani fuzzy HEC risk assessment and table integration."""

from datetime import datetime
from itertools import product
from pathlib import Path

import numpy as np
from skfuzzy import control as ctrl

from .membership_functions import build_antecedents, build_consequent, membership_label
from ..tables.officer_reports_table import get_latest_report
from ..tables.sightings_table import get_sightings_by_zone
from ..tables.weather_table import get_latest_weather
from ..tables.zone_table import get_zone

_VARIABLES = build_antecedents()
_RISK = build_consequent()
_RISK_ORDER = {"low": 25, "medium": 50, "high": 82, "near": 82, "far": 25, "day": 25, "dusk": 50, "night": 82}


def _build_system():
    rules = []
    for sighting, distance, time, season in product(
        ("low", "medium", "high"),
        ("near", "medium", "far"),
        ("day", "dusk", "night"),
        ("low", "medium", "high"),
    ):
        severity = (
            _RISK_ORDER[sighting] + _RISK_ORDER[season]
            + _RISK_ORDER["high" if distance == "near" else distance]
            + _RISK_ORDER["high" if time == "night" else time]
        ) / 4
        output = "high" if severity >= 64 else "medium" if severity >= 42 else "low"
        rules.append(ctrl.Rule(
            _VARIABLES[0][sighting] & _VARIABLES[1][distance]
            & _VARIABLES[2][time] & _VARIABLES[3][season], _RISK[output]
        ))
    return ctrl.ControlSystem(rules)


_SYSTEM = _build_system()


def _clip(value, lower, upper):
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = lower
    if not np.isfinite(number):
        number = lower
    return float(np.clip(number, lower, upper))


def compute_risk_score(sighting_freq, distance_km, time_of_day, seasonal_risk, zone_id=None):
    """Return a JSON-safe score object for the supplied raw indicators."""
    values = (
        _clip(sighting_freq, 0, 15),
        _clip(distance_km, 0, 10),
        _clip(time_of_day, 0, 24),
        _clip(seasonal_risk, 0, 100),
    )
    simulation = ctrl.ControlSystemSimulation(_SYSTEM)
    for variable, value in zip(_VARIABLES, values):
        simulation.input[variable.label] = value
    try:
        simulation.compute()
        score = float(simulation.output["risk_score"])
    except (KeyError, ValueError, AssertionError):
        score = float(np.mean(values[::2]) * 5 + (10 - values[1]) * 2)
    score = float(np.clip(score, 0, 100))
    level = "High" if score >= 60 else "Medium" if score >= 30 else "Low"
    labels = [membership_label(variable, value)[0] for variable, value in zip(_VARIABLES, values)]
    factors = []
    if labels[0] == "high": factors.append("high sighting frequency")
    if labels[1] == "near": factors.append("near corridor")
    if labels[2] in ("dusk", "night"): factors.append(labels[2])
    if labels[3] == "high": factors.append("high seasonal/weather drought risk")
    if not factors: factors.append("low current HEC indicators")
    return {
        "zone_id": zone_id,
        "risk_score": int(round(score)),
        "risk_level": level,
        "contributing_factors": factors,
    }


def _seasonal_value(weather):
    if not weather:
        return 50.0
    drought = str(weather.get("drought_index", "Normal")).lower()
    base = {"severe drought": 95, "dry": 78, "normal": 45, "wet": 20}.get(drought, 50)
    return float(np.clip(base + max(0, 10 - float(weather.get("rainfall_mm", 0))), 0, 100))


def evaluate_zone_risk_from_tables(zone_id, target_time=None):
    """Build a fuzzy assessment from the shared tables and honor verified reports."""
    zone = get_zone(zone_id)
    if not zone:
        raise ValueError(f"Unknown zone: {zone_id}")
    sightings = get_sightings_by_zone(zone_id)
    latest = sightings[-1] if sightings else {}
    report = get_latest_report(zone_id)
    count = sum(int(item.get("number_of_elephants", 0)) for item in sightings)
    distance = float(latest.get("distance_to_corridor_km", zone.get("distance_to_forest_km", 10)))
    hour = float((target_time or latest.get("time", "12:00")).split(":")[0])
    result = compute_risk_score(count, distance, hour, _seasonal_value(get_latest_weather(zone_id)), zone_id)
    if report and report.get("verified"):
        result["contributing_factors"].append("officer-verified report")
        if report.get("report_type") == "patrol_survey" and report.get("number_of_elephants", 0) == 0:
            result.update(risk_score=0, risk_level="Low", contributing_factors=["officer-verified clear patrol"])
    return result