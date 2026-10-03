"""
zone_table.py

Zone table for GajaAlert.
Stores per-zone geographic and connectivity attributes, used by both
the rule-based/fuzzy modules (risk assessment) and the A* search
module (patrol routing). Each zone represents a Grama Niladhari
division or group of adjacent divisions in the Galgamuwa DS Division.

The 10 zones, coordinates, road-network neighbour distances (km) and
flood-prone flags are copied from the Spatial Search Lead's finalized
backend/data/zones.json (synced 2026-10-03). If that file changes,
update this table to match.

distance_to_water_km and distance_to_forest_km are None because the
real data does not provide them yet (water distance is still null in
zones.json; there is no forest/corridor distance field). None means
"unknown": the rule module treats unknown distance cautiously instead
of guessing a value.
"""

zone_data = [
    {
        "zone_id": "Z01",
        "gn_division_name": "Galgamuwa Town",
        "latitude": 7.9821,
        "longitude": 80.2988,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": False,
        "neighbouring_zones": {"Z03": 3.86, "Z02": 4.89, "Z10": 8.96}
    },
    {
        "zone_id": "Z02",
        "gn_division_name": "Walagambapura",
        "latitude": 7.965,
        "longitude": 80.312,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": True,
        "neighbouring_zones": {"Z01": 4.89, "Z10": 5.89, "Z05": 8.39}
    },
    {
        "zone_id": "Z03",
        "gn_division_name": "Bandaragama",
        "latitude": 8.001,
        "longitude": 80.285,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": True,
        "neighbouring_zones": {"Z01": 3.86, "Z10": 7.75, "Z02": 8.74}
    },
    {
        "zone_id": "Z04",
        "gn_division_name": "Meegaswewa",
        "latitude": 7.945,
        "longitude": 80.26,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": True,
        "neighbouring_zones": {"Z05": 9.45, "Z07": 10.53, "Z01": 11.99}
    },
    {
        "zone_id": "Z05",
        "gn_division_name": "Mahragalgamuwa",
        "latitude": 7.928,
        "longitude": 80.335,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": True,
        "neighbouring_zones": {"Z02": 8.39, "Z04": 9.45, "Z10": 10.2}
    },
    {
        "zone_id": "Z06",
        "gn_division_name": "Patukadawala",
        "latitude": 8.025,
        "longitude": 80.36,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": True,
        "neighbouring_zones": {"Z03": 10.59, "Z09": 11.59, "Z10": 14.37}
    },
    {
        "zone_id": "Z07",
        "gn_division_name": "Wadugama",
        "latitude": 7.915,
        "longitude": 80.22,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": True,
        "neighbouring_zones": {"Z04": 10.53, "Z05": 13.99, "Z01": 14.03}
    },
    {
        "zone_id": "Z08",
        "gn_division_name": "Diyakobala",
        "latitude": 8.04,
        "longitude": 80.24,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": False,
        "neighbouring_zones": {"Z03": 9.33, "Z01": 10.97, "Z02": 15.86}
    },
    {
        "zone_id": "Z09",
        "gn_division_name": "Kalankuttiya",
        "latitude": 7.955,
        "longitude": 80.385,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": False,
        "neighbouring_zones": {"Z10": 10.03, "Z06": 11.59, "Z05": 14.2}
    },
    {
        "zone_id": "Z10",
        "gn_division_name": "Rambewa Road Junction",
        "latitude": 7.99,
        "longitude": 80.34,
        "distance_to_water_km": None,
        "distance_to_forest_km": None,
        "flood_prone": False,
        "neighbouring_zones": {"Z02": 5.89, "Z03": 7.75, "Z01": 8.96}
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
