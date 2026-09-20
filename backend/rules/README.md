# Rule-Based Reasoning Module

## Main functions for other modules to use

`get_all_zone_flags()` from `zone_flagger.py` — returns risk flags for every zone in the system:

```python
from backend.rules.zone_flagger import get_all_zone_flags

flags = get_all_zone_flags()
```

For a single zone: `get_zone_risk_flag(zone_id, current_time=None)`

## Output format

```python
{
    "zone_id": "Z07",
    "risk": "Medium",          # Low / Medium / Medium-High / High / Undetermined
    "triggered_by": "R18",     # which rule fired, or None if uncovered
    "conditions": {
        "sighting": "Low",
        "distance": "Near",
        "time": "Dusk",
        "season": "High"
    }
}
```

`"Undetermined"` means no rule in the base covers this exact combination — treat this as "needs manual officer review," not an error.

Pulls data automatically from `sightings_table.py`, `zone_table.py`, and `weather_table.py` — just pass a `zone_id`.

## Files

- `rules_table.py` — 27 rule definitions (`RULES` list)
- `rule_engine.py` — `evaluate_rules()`, `get_matching_rules()`
- `zone_flagger.py` — `get_zone_risk_flag()`, `get_all_zone_flags()` (main entry points)

## Known limitations

- **Distance**: `categorize_distance()` currently uses `distance_to_forest_km` from `zone_table.py` as a stand-in for "distance to elephant corridor," since the zone table has no dedicated corridor-distance field yet. Flag to Spatial Search Lead if a real field is added.
- **Thresholds**: The Low/Medium/High and Near/Medium/Far cutoffs (e.g. `count >= 3 = High` sightings) are placeholder values, not derived from real data. Recalibrate once real/simulated sighting volume is available.
- **Season**: Uses `drought_index` from `weather_table.py` as a proxy for seasonal/harvest risk. Falls back to `"Medium"` if no weather record exists for a zone.

## Testing

```powershell
python -m pytest tests\test_rule_engine.py
```