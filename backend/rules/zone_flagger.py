"""
zone_flagger.py

Zone-level flag generation for GajaAlert.
Pulls real data for a given zone from sightings_table.py, zone_table.py,
weather_table.py and officer_reports_table.py, converts raw values into
the categorical labels the rule engine expects (Low/Medium/High,
Near/Medium/Far, etc.), and runs them through evaluate_rules() to produce
the initial risk flag that feeds into the fuzzy logic module
(Section 6.1, 8.2 of proposal).
"""

from datetime import datetime, timedelta

from .rule_engine import evaluate_rules, get_matching_rules
from ..sightings.sightings_table import get_sightings_by_zone
from ..zones.zone_table import get_zone, zone_data
from ..weather.weather_table import get_drought_category
from ..officer_reports.officer_reports_table import get_reports_by_zone

# Time-of-day boundaries (24h clock). Keep in sync with the Fuzzy module's
# membership functions (Day starts 06:00, Dusk peaks 18:00, Night after 20:00).
DAY_START_HOUR = 6
DUSK_START_HOUR = 18
NIGHT_START_HOUR = 20

# Only sightings within this many days before "now" count as recent.
# The Fuzzy module measures sighting frequency per week, so this matches it.
RECENT_WINDOW_DAYS = 7


def _record_datetime(record):
    """Parse a record's date + time into a datetime, or None if invalid."""
    try:
        return datetime.strptime(
            f"{record['date']} {record['time']}", "%Y-%m-%d %H:%M"
        )
    except (KeyError, ValueError, TypeError):
        return None


def _in_window(record, current_time):
    """True if the record falls within the recent window ending at current_time."""
    when = _record_datetime(record)
    if when is None:
        return False
    window_start = current_time - timedelta(days=RECENT_WINDOW_DAYS)
    return window_start <= when <= current_time


def _verified_reports_in_window(zone_id, current_time):
    """Officer-verified reports for a zone inside the recent window."""
    return [
        r for r in get_reports_by_zone(zone_id)
        if r.get("verified") and _in_window(r, current_time)
    ]


def has_officer_override(zone_id, current_time=None):
    """
    True if a verified officer report exists for this zone in the recent
    window. When True, officer data takes precedence over simulated
    sightings for the zone.
    """
    if current_time is None:
        current_time = datetime.now()
    return len(_verified_reports_in_window(zone_id, current_time)) > 0


def categorize_sighting_frequency(zone_id, current_time=None):
    """
    Count sightings for a zone in the last RECENT_WINDOW_DAYS days and
    convert to Low/Medium/High.

    - Sightings older than the window, in the future, or with an
      unreadable date/time are ignored.
    - If a verified officer report exists in the window, simulated
      sightings are ignored (officer ground truth takes precedence), and
      each officer 'verified_sighting' report counts as a sighting.

    Thresholds are placeholders — adjust once real sighting volume
    is known from actual field data.
    """
    if current_time is None:
        current_time = datetime.now()

    reports = _verified_reports_in_window(zone_id, current_time)

    count = 0
    for sighting in get_sightings_by_zone(zone_id):
        if not _in_window(sighting, current_time):
            continue
        if reports and sighting.get("data_origin") == "Simulated":
            continue  # officer ground truth overrides simulated positions
        count += 1

    count += sum(1 for r in reports if r.get("report_type") == "verified_sighting")

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

    If the zone is unknown or its distance is not available (None), return
    the cautious middle value "Medium" instead of guessing "Far", so missing
    data is never silently read as safe.
    """
    zone = get_zone(zone_id)
    if zone is None:
        return "Medium"

    distance_km = zone.get("distance_to_forest_km")
    if distance_km is None:
        return "Medium"

    if distance_km <= 1.0:
        return "Near"
    elif distance_km <= 2.0:
        return "Medium"
    else:
        return "Far"


def categorize_time(current_time=None):
    """
    Convert a datetime (or the current time, if none given) into
    Day / Dusk / Night. Boundaries are defined by the constants above
    so they stay aligned with the Fuzzy module.
    """
    if current_time is None:
        current_time = datetime.now()

    hour = current_time.hour

    if DUSK_START_HOUR <= hour < NIGHT_START_HOUR:
        return "Dusk"
    elif hour >= NIGHT_START_HOUR or hour < DAY_START_HOUR:
        return "Night"
    else:
        return "Day"


def categorize_season(zone_id):
    """
    Use the zone's drought category from weather_table.py as a proxy
    for seasonal risk, and convert to Low/Medium/High.
    """
    drought = get_drought_category(zone_id)

    if drought in ("Severe Drought", "Dry"):
        return "High"
    elif drought == "Normal":
        return "Medium"
    elif drought == "Wet":
        return "Low"
    else:
        # "Unknown" or any unrecognised value: never silently read as safe
        return "Medium"


def get_zone_risk_flag(zone_id, current_time=None):
    """
    Full pipeline: pull real data for a zone, categorize it, and run
    it through the rule engine to produce the initial risk flag.
    Returns a dict with the risk level, the input conditions used, and
    whether officer reports overrode simulated data, for explainability.
    """
    if current_time is None:
        current_time = datetime.now()

    sighting = categorize_sighting_frequency(zone_id, current_time)
    distance = categorize_distance(zone_id)
    time_of_day = categorize_time(current_time)
    season = categorize_season(zone_id)

    risk = evaluate_rules(sighting, distance, time_of_day, season)
    matched = get_matching_rules(sighting, distance, time_of_day, season)

    return {
        "zone_id": zone_id,
        "risk": risk,
        "triggered_by": matched[0]["id"] if matched else None,
        "officer_override": has_officer_override(zone_id, current_time),
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