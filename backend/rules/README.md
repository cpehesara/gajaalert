# Rule-Based Reasoning Module

## Main function for other modules to use:
`get_zone_risk_flag(zone_id, current_time=None)` from `zone_flagger.py`

Returns:
```python
{
    "zone_id": "Z07",
    "risk": "Medium",          # Low / Medium / Medium-High / High / Undetermined
    "triggered_by": "R18",     # which rule fired, or None
    "conditions": {
        "sighting": "Low",
        "distance": "Near",
        "time": "Dusk",
        "season": "High"
    }
}
```

Pulls data from sightings_table.py, zone_table.py, and weather_table.py automatically — just pass a zone_id.

## Files
- `rules_table.py` — 27 rule definitions (RULES list)
- `rule_engine.py` — `evaluate_rules()`, `get_matching_rules()`
- `zone_flagger.py` — `get_zone_risk_flag()` (the main entry point)