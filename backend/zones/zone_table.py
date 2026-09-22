"""
zone_table.py

Zone table for GajaAlert.
Stores per-zone geographic and connectivity attributes, used by both
the rule-based/fuzzy modules (risk assessment) and the A* search
module (patrol routing). Each zone represents a Grama Niladhari
division or group of adjacent divisions in the Galgamuwa DS Division.
"""

zone_data = [
    {
        "zone_id": "Z01",
        "gn_division_name": "Village A",
        "latitude": 7.7421,
        "longitude": 80.2891,
        "distance_to_water_km": 0.8,
        "distance_to_forest_km": 1.2,
        "flood_prone": False,
        "neighbouring_zones": {"Z02": 2.4, "Z05": 3.1}
    },
    {
        "zone_id": "Z02",
        "gn_division_name": "Walagambapura",
        "latitude": 7.7502,
        "longitude": 80.2955,
        "distance_to_water_km": 0.3,
        "distance_to_forest_km": 2.0,
        "flood_prone": True,
        "neighbouring_zones": {"Z01": 2.4, "Z03": 1.8}
    },
    {
        "zone_id": "Z03",
        "gn_division_name": "Bandaragama",
        "latitude": 7.7305,
        "longitude": 80.2765,
        "distance_to_water_km": 0.6,
        "distance_to_forest_km": 0.9,
        "flood_prone": True,
        "neighbouring_zones": {"Z02": 1.8, "Z04": 2.9}
    },
    {
        "zone_id": "Z07",
        "gn_division_name": "Village A (Z07)",
        "latitude": 7.7583,
        "longitude": 80.3012,
        "distance_to_water_km": 0.6,
        "distance_to_forest_km": 0.9,
        "flood_prone": False,
        "neighbouring_zones": {"Z06": 2.4, "Z08": 3.1, "Z09": 2.0}
    },
]


def get_zone(zone_id):
    """Return the zone record for a given zone ID, or None."""
    for zone in zone_data:
        if zone["zone_id"] == zone_id:
            return zone
    return None


def get_neighbours(zone_id):
    """Return the adjacency dict {neighbour_zone: travel_weight} for a zone."""
    zone = get_zone(zone_id)
    return zone["neighbouring_zones"] if zone else {}


def get_flood_prone_zones():
    """Return all zones flagged as flood-prone."""
    return [z for z in zone_data if z["flood_prone"]]


if __name__ == "__main__":
    for zone in zone_data:
        print(zone)

    print("\nNeighbours of Z07:", get_neighbours("Z07"))
    print("Flood-prone zones:", [z["zone_id"] for z in get_flood_prone_zones()])