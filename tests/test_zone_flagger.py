from datetime import datetime, timedelta
from unittest.mock import patch

from backend.rules import zone_flagger
from backend.rules.zone_flagger import (
    categorize_distance,
    categorize_season,
    categorize_sighting_frequency,
    categorize_time,
    get_all_zone_flags,
    get_zone_risk_flag,
)
from backend.zones.zone_table import zone_data


# ---------- categorize_time ----------
def test_time_night_dusk_day_boundaries():
    assert categorize_time(datetime(2026, 8, 10, 22, 0)) == "Night"
    assert categorize_time(datetime(2026, 8, 10, 2, 0)) == "Night"
    assert categorize_time(datetime(2026, 8, 10, 18, 0)) == "Dusk"
    assert categorize_time(datetime(2026, 8, 10, 19, 59)) == "Dusk"
    assert categorize_time(datetime(2026, 8, 10, 20, 0)) == "Night"
    assert categorize_time(datetime(2026, 8, 10, 5, 59)) == "Night"
    assert categorize_time(datetime(2026, 8, 10, 6, 0)) == "Day"
    assert categorize_time(datetime(2026, 8, 10, 12, 0)) == "Day"


# ---------- categorize_sighting_frequency ----------
NOW = datetime(2026, 8, 12, 12, 0)


def _s(days_ago):
    """Fake sighting record `days_ago` days before NOW (negative = future)."""
    when = NOW - timedelta(days=days_ago)
    return {"date": when.strftime("%Y-%m-%d"), "time": when.strftime("%H:%M")}


def test_sighting_frequency_levels():
    cases = [
        ([], "Low"),
        ([_s(1)], "Low"),
        ([_s(1), _s(2)], "Medium"),
        ([_s(1), _s(2), _s(3)], "High"),
    ]
    for records, expected in cases:
        with patch.object(zone_flagger, "get_sightings_by_zone", return_value=records):
            assert categorize_sighting_frequency("Z01", NOW) == expected


def test_old_sightings_are_ignored():
    # 4 sightings in total, but only 2 are inside the 7-day window
    records = [_s(1), _s(2), _s(10), _s(20)]
    with patch.object(zone_flagger, "get_sightings_by_zone", return_value=records):
        assert categorize_sighting_frequency("Z01", NOW) == "Medium"


def test_future_and_malformed_sightings_are_ignored():
    records = [_s(1), _s(2), _s(-1), {"date": "bad", "time": "??"}, {}]
    with patch.object(zone_flagger, "get_sightings_by_zone", return_value=records):
        assert categorize_sighting_frequency("Z01", NOW) == "Medium"


# ---------- categorize_distance ----------
def test_distance_levels():
    for km, expected in [(0.5, "Near"), (1.0, "Near"), (1.5, "Medium"),
                         (2.0, "Medium"), (2.5, "Far")]:
        with patch.object(zone_flagger, "get_zone",
                          return_value={"distance_to_forest_km": km}):
            assert categorize_distance("Z01") == expected


def test_distance_unknown_zone_defaults_to_far():
    assert categorize_distance("Z99") == "Far"


# ---------- categorize_season ----------
def test_season_mapping():
    cases = {"Severe Drought": "High", "Dry": "High", "Normal": "Medium",
             "Wet": "Low", "Unknown": "Medium", "???": "Medium"}
    for drought, expected in cases.items():
        with patch.object(zone_flagger, "get_drought_category", return_value=drought):
            assert categorize_season("Z01") == expected


def test_missing_weather_is_never_read_as_safe():
    # Z01 has no weather record in weather_table.py
    assert categorize_season("Z01") == "Medium"


# ---------- get_zone_risk_flag ----------
def test_flag_output_schema():
    flag = get_zone_risk_flag("Z07", datetime(2026, 8, 11, 22, 0))
    assert set(flag) == {"zone_id", "risk", "triggered_by", "conditions"}
    assert set(flag["conditions"]) == {"sighting", "distance", "time", "season"}
    assert flag["zone_id"] == "Z07"


def test_flag_reports_triggering_rule_for_covered_case():
    # Z07: Low sightings, Near, Dusk, Dry -> R18 -> Medium
    flag = get_zone_risk_flag("Z07", datetime(2026, 8, 11, 18, 30))
    assert flag["risk"] == "Medium"
    assert flag["triggered_by"] == "R18"


def test_flag_undetermined_has_no_trigger():
    # Z01: Low, Medium distance, Dusk, Medium season -> not in rule base
    flag = get_zone_risk_flag("Z01", datetime(2026, 8, 11, 18, 30))
    assert flag["risk"] == "Undetermined"
    assert flag["triggered_by"] is None


def test_unknown_zone_does_not_crash():
    flag = get_zone_risk_flag("Z99", datetime(2026, 8, 11, 12, 0))
    assert flag["zone_id"] == "Z99"
    assert flag["risk"] in {"Low", "Medium", "Medium/High", "High", "Undetermined"}


# ---------- get_all_zone_flags ----------
def test_all_zone_flags_covers_every_zone():
    flags = get_all_zone_flags(datetime(2026, 8, 11, 22, 0))
    assert [f["zone_id"] for f in flags] == [z["zone_id"] for z in zone_data]