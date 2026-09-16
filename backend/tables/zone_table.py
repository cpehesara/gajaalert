zone_data = [
    {"zone_id": "Z01", "name": "Village A", "lat": 7.7421, "lng": 80.2891, "distance_to_corridor_km": 4.0, "distance_to_water_km": 0.8, "distance_to_forest_km": 1.2, "flood_prone": False, "neighbors": {"Z02": 2.4, "Z05": 3.1}},
    {"zone_id": "Z02", "name": "Walagambapura", "lat": 7.7502, "lng": 80.2955, "distance_to_corridor_km": 2.5, "distance_to_water_km": 0.3, "distance_to_forest_km": 2.0, "flood_prone": True, "neighbors": {"Z01": 2.4, "Z03": 1.8}},
    {"zone_id": "Z03", "name": "Bandaragama", "lat": 7.7305, "lng": 80.2765, "distance_to_corridor_km": 3.5, "distance_to_water_km": 0.6, "distance_to_forest_km": 0.9, "flood_prone": True, "neighbors": {"Z02": 1.8, "Z04": 2.9}},
    {"zone_id": "Z07", "name": "Village A (Z07)", "lat": 7.7583, "lng": 80.3012, "distance_to_corridor_km": 1.4, "distance_to_water_km": 0.6, "distance_to_forest_km": 0.9, "flood_prone": False, "neighbors": {"Z06": 2.4, "Z08": 3.1, "Z09": 2.0}},
    {"zone_id": "Z09", "name": "Z09", "lat": 7.7305, "lng": 80.2765, "distance_to_corridor_km": 2.1, "distance_to_water_km": 0.6, "distance_to_forest_km": 0.9, "flood_prone": False, "neighbors": {"Z07": 2.0}},
]

def get_zone(zone_id):
    return next((zone for zone in zone_data if zone["zone_id"] == zone_id), None)

def get_neighbours(zone_id):
    return (get_zone(zone_id) or {}).get("neighbors", {})