"""
zone_flagger.py

Zone-level flag generation for GajaAlert.
Pulls real data for a given zone from sightings_table.py, zone_table.py,
and weather_table.py, converts raw values into the categorical labels
the rule engine expects (Low/Medium/High, Near/Medium/Far, etc.), and
runs them through evaluate_rules() to produce the initial risk flag
that feeds into the fuzzy logic module (Section 6.1, 8.2 of proposal).
"""

from datetime import datetime

from .rule_engine import evaluate_rules, get_matching_rules
from ..sightings.sightings_table import get_sightings_by_zone
from ..zones.zone_table import get_zone, zone_data
from ..weather.weather_table import get_drought_category


def categorize_sighting_frequency(zone_id):
    """
    Count recent sightings for a zone and convert to Low/Medium/High.
    Thresholds are placeholders — adjust once real sighting volume
    is known from actual field data.
    """
    sightings = get_sightings_by_zone(zone_id)
    count = len(sightings)

    if count >= 3:
        return "High"
    elif count == 2:
        return "Medium"
    else:
        return "Low"


def categorize_distance(zone_id):
    """
    Use the zone's distance_to_forest_km as a proxy for distance to
    corridor, and convert to Near/Medium/Far.
    """
    zone = get_zone(zone_id)
    if zone is None:
        return "Far"  # default fallback if zone data is missing

    distance_km = zone["distance_to_forest_km"]

    if distance_km <= 1.0:
        return "Near"
    elif distance_km <= 2.0:
        return "Medium"
    else:
        return "Far"


def categorize_time(current_time=None):
    """
    Convert a datetime (or the current time, if none given) into
    Day / Dusk / Night.
    """
    if current_time is None:
        current_time = datetime.now()

    hour = current_time.hour

    if 18 <= hour < 20:
        return "Dusk"
    elif hour >= 20 or hour < 5:
        return "Night"
    else:
        return "Day"


def categorize_season(zone_id):
    """
    Use the zone's drought category from weather_table.py as a proxy
    for seasonal risk, and convert to Low/Medium/High.
    """
    drought = get_drought_category(zone_id)

    if drought == "Dry":
        return "High"
    elif drought == "Normal":
        return "Medium"
    elif drought == "Unknown":
        return "Medium"  # no weather data available — default to a cautious middle value
    else:
        return "Low"


def get_zone_risk_flag(zone_id, current_time=None):
    """
    Full pipeline: pull real data for a zone, categorize it, and run
    it through the rule engine to produce the initial risk flag.
    Returns a dict with the risk level and the input conditions used,
    for explainability.
    """
    sighting = categorize_sighting_frequency(zone_id)
    distance = categorize_distance(zone_id)
    time_of_day = categorize_time(current_time)
    season = categorize_season(zone_id)

    risk = evaluate_rules(sighting, distance, time_of_day, season)
    matched = get_matching_rules(sighting, distance, time_of_day, season)

    return {
        "zone_id": zone_id,
        "risk": risk,
        "triggered_by": matched[0]["id"] if matched else None,
        "conditions": {
            "sighting": sighting,
            "distance": distance,
            "time": time_of_day,
            "season": season
        }
    }


def get_all_zone_flags(current_time=None):
    """
    Loop through every zone in zone_table.py and return a risk flag
    for each. This is the main function other modules (e.g. the
    dashboard, Systems & Integration Lead) should call to get a
    full system-wide risk picture.
    """
    all_flags = []
    for zone in zone_data:
        flag = get_zone_risk_flag(zone["zone_id"], current_time)
        all_flags.append(flag)
    return all_flags


if __name__ == "__main__":
    print(get_zone_risk_flag("Z07"))
    print(get_zone_risk_flag("Z03"))
    print("\n--- All zones ---")
    for flag in get_all_zone_flags():
        print(flag)

    print("\n--- Missing weather data test (Z01) ---")
    print("Season category for Z01:", categorize_season("Z01"))