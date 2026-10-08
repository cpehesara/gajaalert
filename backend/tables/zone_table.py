"""Zone table, built from backend/data/zones.json (single source of truth).
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
