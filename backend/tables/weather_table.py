"""Weather table (feeds the Seasonal Risk variable)."""

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
