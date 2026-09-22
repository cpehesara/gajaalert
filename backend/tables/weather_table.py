weather_data = [
    {"record_id": "W001", "date": "2026-08-10", "zone_id": "Z07", "rainfall_mm": 2.4, "temperature_c": 31, "drought_index": "Dry", "source": "Dept. of Meteorology"},
    {"record_id": "W002", "date": "2026-08-11", "zone_id": "Z07", "rainfall_mm": 0.0, "temperature_c": 33, "drought_index": "Dry", "source": "Dept. of Meteorology"},
    {"record_id": "W003", "date": "2026-08-12", "zone_id": "Z03", "rainfall_mm": 15.6, "temperature_c": 27, "drought_index": "Normal", "source": "Dept. of Meteorology"},
    {"record_id": "W004", "date": "2026-08-13", "zone_id": "Z09", "rainfall_mm": 0.5, "temperature_c": 34, "drought_index": "Dry", "source": "Dept. of Meteorology"},
]

def get_weather_by_zone(zone_id):
    return [item for item in weather_data if item["zone_id"] == zone_id]

def get_latest_weather(zone_id):
    records = get_weather_by_zone(zone_id)
    return max(records, key=lambda item: item["date"], default=None)