"""
weather_table.py

Weather data table for GajaAlert.
Stores rainfall and drought-condition records used as an input to the
fuzzy risk assessment module (feeds into the Seasonal Risk variable).

Each record represents a weather reading tied to a date and zone (or
region), sourced either from the Department of Meteorology or an
open weather API.
"""

weather_data = [
    {
        "record_id": "W001",
        "date": "2026-08-10",
        "zone_id": "Z07",
        "rainfall_mm": 2.4,
        "temperature_c": 31,
        "drought_index": "Dry",
        "source": "Dept. of Meteorology"
    },
    {
        "record_id": "W002",
        "date": "2026-08-11",
        "zone_id": "Z07",
        "rainfall_mm": 0.0,
        "temperature_c": 33,
        "drought_index": "Dry",
        "source": "Dept. of Meteorology"
    },
    {
        "record_id": "W003",
        "date": "2026-08-12",
        "zone_id": "Z03",
        "rainfall_mm": 15.6,
        "temperature_c": 27,
        "drought_index": "Normal",
        "source": "Dept. of Meteorology"
    },
    {
        "record_id": "W004",
        "date": "2026-08-13",
        "zone_id": "Z09",
        "rainfall_mm": 0.5,
        "temperature_c": 34,
        "drought_index": "Dry",
        "source": "Dept. of Meteorology"
    },
]


def get_weather_by_zone(zone_id):
    """Return all weather records for a given zone."""
    return [record for record in weather_data if record["zone_id"] == zone_id]


def get_latest_weather(zone_id):
    """Return the most recent weather record for a given zone, or None."""
    records = get_weather_by_zone(zone_id)
    if not records:
        return None
    return sorted(records, key=lambda r: r["date"], reverse=True)[0]


def get_drought_category(zone_id):
    """Return the drought_index of the most recent record for a zone."""
    latest = get_latest_weather(zone_id)
    return latest["drought_index"] if latest else "Unknown"


if __name__ == "__main__":
    # Quick manual test when running this file directly
    for record in weather_data:
        print(record)

    print("\nLatest weather for Z07:", get_latest_weather("Z07"))
    print("Drought category for Z07:", get_drought_category("Z07"))