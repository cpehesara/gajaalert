sightings_data = [
    {"sighting_id": "S001", "date": "2026-08-10", "time": "19:30", "zone_id": "Z03", "latitude": 7.7421, "longitude": 80.2891, "number_of_elephants": 3, "distance_to_corridor_km": 1.4, "source": "Village Coordinator", "data_origin": "Officer-verified"},
    {"sighting_id": "S002", "date": "2026-08-11", "time": "22:10", "zone_id": "Z07", "latitude": 7.7583, "longitude": 80.3012, "number_of_elephants": 1, "distance_to_corridor_km": 0.6, "source": "Simulation Engine", "data_origin": "Simulated"},
    {"sighting_id": "S003", "date": "2026-08-12", "time": "05:45", "zone_id": "Z09", "latitude": 7.7305, "longitude": 80.2765, "number_of_elephants": 5, "distance_to_corridor_km": 2.1, "source": "DWC Field Officer", "data_origin": "Officer-verified"},
]

def get_sightings_by_zone(zone_id):
    return [item for item in sightings_data if item["zone_id"] == zone_id]