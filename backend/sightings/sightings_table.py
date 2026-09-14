"""
sightings_table.py

Sightings / Positions table for GajaAlert.
Stores elephant sighting records and simulated positions, used as
input to the fuzzy risk assessment and movement-prediction modules.
"""

sightings_data = [
    {
        "sighting_id": "S001",
        "date": "2026-08-10",
        "time": "19:30",
        "zone_id": "Z03",
        "latitude": 7.7421,
        "longitude": 80.2891,
        "number_of_elephants": 3,
        "distance_to_corridor_km": 1.4,
        "season_risk_period": "Dry Season",
        "source": "Village Coordinator",
        "data_origin": "Officer-verified",
        "notes": "Elephant group moving toward farmland"
    },
    {
        "sighting_id": "S002",
        "date": "2026-08-11",
        "time": "22:10",
        "zone_id": "Z07",
        "latitude": 7.7583,
        "longitude": 80.3012,
        "number_of_elephants": 1,
        "distance_to_corridor_km": 0.6,
        "season_risk_period": "Harvest Season",
        "source": "Simulation Engine",
        "data_origin": "Simulated",
        "notes": "Lone bull, correlated random walk position"
    },
    {
        "sighting_id": "S003",
        "date": "2026-08-12",
        "time": "05:45",
        "zone_id": "Z09",
        "latitude": 7.7305,
        "longitude": 80.2765,
        "number_of_elephants": 5,
        "distance_to_corridor_km": 2.1,
        "season_risk_period": "Dry Season",
        "source": "DWC Field Officer",
        "data_origin": "Officer-verified",
        "notes": "Herd sighted near tank, moving away from settlement"
    },
]


def get_sightings_by_zone(zone_id):
    """Return all sighting records for a given zone."""
    return [s for s in sightings_data if s["zone_id"] == zone_id]


def get_verified_sightings():
    """Return only officer-verified sightings."""
    return [s for s in sightings_data if s["data_origin"] == "Officer-verified"]


def get_simulated_sightings():
    """Return only simulated (non-verified) positions."""
    return [s for s in sightings_data if s["data_origin"] == "Simulated"]


def get_latest_sighting(zone_id):
    """Return the most recent sighting for a given zone, or None."""
    records = get_sightings_by_zone(zone_id)
    if not records:
        return None
    return sorted(records, key=lambda s: (s["date"], s["time"]), reverse=True)[0]


if __name__ == "__main__":
    for record in sightings_data:
        print(record)

    print("\nVerified sightings:", [s["sighting_id"] for s in get_verified_sightings()])
    print("Simulated sightings:", [s["sighting_id"] for s in get_simulated_sightings()])
    print("Latest sighting for Z07:", get_latest_sighting("Z07"))
    