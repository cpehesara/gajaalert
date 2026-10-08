"""Sightings table (simulated + officer-verified). Coordinates match the zone centres."""

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
