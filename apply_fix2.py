"""Fix 2: one source of truth for zone/sighting/weather/officer data.
Run from project root:  python apply_fix2.py
- backend/tables/*  becomes the ONLY real copy (zone_table reads data/zones.json)
- backend/zones, sightings, weather, officer_reports become thin re-exports,
  so rule-module imports and existing tests keep working unchanged.
"""
import os

B = "backend"

FILES = {}

FILES[f"{B}/tables/zone_table.py"] = r'''"""Zone table, built from backend/data/zones.json (single source of truth).
Exposes both naming styles used across modules (lat/latitude, neighbors/neighbouring_zones).
distance_to_corridor_km uses the forest-edge distance (proposal Sec. 8.1: corridor or forest boundary).
None = unknown; consumers must treat it cautiously.
"""
import json
from pathlib import Path

_ZONES_FILE = Path(__file__).resolve().parents[1] / "data" / "zones.json"


def _load():
    with _ZONES_FILE.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    zones = []
    for z in raw:
        neighbors = dict(z["neighbors"])
        forest = z.get("distance_to_forest_km")
        zones.append({
            "zone_id": z["zone_id"],
            "name": z["name"], "gn_division_name": z["name"],
            "lat": z["lat"], "latitude": z["lat"],
            "lng": z["lng"], "longitude": z["lng"],
            "neighbors": neighbors, "neighbouring_zones": neighbors,
            "distance_to_water_km": z.get("distance_to_water_km"),
            "distance_to_forest_km": forest,
            "distance_to_corridor_km": z.get("distance_to_corridor_km", forest),
            "flood_prone": bool(z.get("flood_prone", False)),
        })
    return zones


zone_data = _load()


def get_zone(zone_id):
    return next((z for z in zone_data if z["zone_id"] == zone_id), None)


def get_neighbours(zone_id):
    return (get_zone(zone_id) or {}).get("neighbors", {})


def get_flood_prone_zones():
    return [z for z in zone_data if z["flood_prone"]]
'''

FILES[f"{B}/tables/sightings_table.py"] = r'''"""Sightings table (simulated + officer-verified). Coordinates match the zone centres."""

sightings_data = [
    {"sighting_id": "S001", "date": "2026-08-10", "time": "19:30", "zone_id": "Z03",
     "latitude": 8.001, "longitude": 80.285, "number_of_elephants": 3,
     "distance_to_corridor_km": 1.4, "season_risk_period": "Dry Season",
     "source": "Village Coordinator", "data_origin": "Officer-verified",
     "notes": "Elephant group moving toward farmland"},
    {"sighting_id": "S002", "date": "2026-08-11", "time": "22:10", "zone_id": "Z07",
     "latitude": 7.915, "longitude": 80.22, "number_of_elephants": 1,
     "distance_to_corridor_km": 0.6, "season_risk_period": "Harvest Season",
     "source": "Simulation Engine", "data_origin": "Simulated",
     "notes": "Lone bull, correlated random walk position"},
    {"sighting_id": "S003", "date": "2026-08-12", "time": "05:45", "zone_id": "Z09",
     "latitude": 7.955, "longitude": 80.385, "number_of_elephants": 5,
     "distance_to_corridor_km": 2.1, "season_risk_period": "Dry Season",
     "source": "DWC Field Officer", "data_origin": "Officer-verified",
     "notes": "Herd sighted near tank, moving away from settlement"},
]


def get_sightings_by_zone(zone_id):
    return [s for s in sightings_data if s["zone_id"] == zone_id]


def get_verified_sightings():
    return [s for s in sightings_data if s["data_origin"] == "Officer-verified"]


def get_simulated_sightings():
    return [s for s in sightings_data if s["data_origin"] == "Simulated"]


def get_latest_sighting(zone_id):
    records = get_sightings_by_zone(zone_id)
    return max(records, key=lambda s: (s["date"], s["time"]), default=None)
'''

FILES[f"{B}/tables/weather_table.py"] = r'''"""Weather table (feeds the Seasonal Risk variable)."""

weather_data = [
    {"record_id": "W001", "date": "2026-08-10", "zone_id": "Z07", "rainfall_mm": 2.4, "temperature_c": 31, "drought_index": "Dry", "source": "Dept. of Meteorology"},
    {"record_id": "W002", "date": "2026-08-11", "zone_id": "Z07", "rainfall_mm": 0.0, "temperature_c": 33, "drought_index": "Dry", "source": "Dept. of Meteorology"},
    {"record_id": "W003", "date": "2026-08-12", "zone_id": "Z03", "rainfall_mm": 15.6, "temperature_c": 27, "drought_index": "Normal", "source": "Dept. of Meteorology"},
    {"record_id": "W004", "date": "2026-08-13", "zone_id": "Z09", "rainfall_mm": 0.5, "temperature_c": 34, "drought_index": "Dry", "source": "Dept. of Meteorology"},
]


def get_weather_by_zone(zone_id):
    return [r for r in weather_data if r["zone_id"] == zone_id]


def get_latest_weather(zone_id):
    return max(get_weather_by_zone(zone_id), key=lambda r: r["date"], default=None)


def get_drought_category(zone_id):
    latest = get_latest_weather(zone_id)
    return latest["drought_index"] if latest else "Unknown"
'''

FILES[f"{B}/tables/officer_reports_table.py"] = r'''"""Officer-verified reports. Verified reports take precedence over simulated data."""

officer_reports = [
    {"report_id": "OR001", "officer_id": "DWC-014", "zone_id": "Z07", "date": "2026-08-10", "time": "19:45",
     "report_type": "verified_sighting", "number_of_elephants": 4,
     "notes": "Small herd moving toward paddy field near village boundary", "verified": True},
    {"report_id": "OR002", "officer_id": "DWC-009", "zone_id": "Z03", "date": "2026-08-11", "time": "06:20",
     "report_type": "patrol_survey", "number_of_elephants": 0,
     "notes": "No elephant activity observed during morning patrol", "verified": True},
    {"report_id": "OR003", "officer_id": "DWC-014", "zone_id": "Z09", "date": "2026-08-12", "time": "21:10",
     "report_type": "verified_sighting", "number_of_elephants": 1,
     "notes": "Lone bull near electric fence, dispersed after noise deterrent", "verified": True},
]


def get_reports_by_zone(zone_id):
    return [r for r in officer_reports if r.get("zone_id") == zone_id]


def get_latest_report(zone_id):
    return max(get_reports_by_zone(zone_id),
               key=lambda r: (r.get("date", ""), r.get("time", "")), default=None)


def has_verified_override(zone_id, date):
    return any(r.get("zone_id") == zone_id and r.get("date") == date and r.get("verified")
               for r in officer_reports)
'''

SHIMS = {
    f"{B}/zones/zone_table.py": "zone_table",
    f"{B}/sightings/sightings_table.py": "sightings_table",
    f"{B}/weather/weather_table.py": "weather_table",
    f"{B}/officer_reports/officer_reports_table.py": "officer_reports_table",
}
for path, mod in SHIMS.items():
    FILES[path] = (f'"""Re-export: the single source of truth is backend/tables/{mod}.py"""\n'
                   f"from ..tables.{mod} import *  # noqa: F401,F403\n")

for path, text in FILES.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    print("wrote", path)

# unused sample-data duplicates (the real matrix is data/transition_matrix.json)
for stale in (f"{B}/markov/markov_transition_table.py",):
    if os.path.exists(stale):
        os.remove(stale)
        print("deleted", stale)
print("Done. Now do the 2 manual edits + 1 test edit from the chat.")