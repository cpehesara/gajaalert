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
    "risk": "Medium",           # Low / Medium / Medium/High / High / Undetermined
    "triggered_by": "R18",      # id of the rule that fired, or None
    "officer_override": False,  # True if a verified officer report overrode simulated sightings
    "conditions": {
        "sighting": "Low",
        "distance": "Near",
        "time": "Dusk",
        "season": "High"
    }
}
```

- `RISK_LEVELS` in `rule_engine.py` lists every label the module can return. Compare against it instead of hand-typed strings.
- `"Medium/High"` sits between Medium and High.
- `"Undetermined"` now only appears for unrecognised labels (for example a missing or misspelled input). Every valid Low/Medium/High, Near/Medium/Far and Day/Dusk/Night combination returns a result. Treat `"Undetermined"` as "needs manual officer review," not an error.
- A `triggered_by` starting with `R` is an expert-written rule. One starting with `D` is a derived rule (see below).

Pulls data automatically from `sightings_table.py`, `zone_table.py`, `weather_table.py` and `officer_reports_table.py` — just pass a `zone_id`.

## Files

- `rules_table.py` — 81 rule definitions (`RULES` list): R1–R27 are expert-written, D01–D54 are derived from a scoring formula to cover every remaining combination
- `rule_engine.py` — `evaluate_rules()`, `get_matching_rules()`, `RISK_LEVELS`
- `zone_flagger.py` — `get_zone_risk_flag()`, `get_all_zone_flags()` (main entry points)

## How the inputs are categorised

All cutoffs are constants at the top of `zone_flagger.py`.

| Input | Rule |
|---|---|
| Sightings | Counted over the last 7 days. 0–3 = Low, 4–8 = Medium, 9 or more = High. Older, future or unreadable records are ignored. |
| Distance | Up to 1.9 km = Near, up to 4.6 km = Medium, beyond = Far. Unknown distance = Medium. |
| Time of day | Day 06:00–18:00, Dusk 18:00–20:00, Night 20:00–06:00. |
| Season | Severe Drought / Dry = High, Normal = Medium, Wet = Low, missing = Medium. |

The sighting and distance cutoffs are taken from where neighbouring terms of the Fuzzy module's membership functions cross, and the time boundaries match the Fuzzy module, so both modules agree on what each label means.

## Officer override

If a verified officer report exists for a zone within the 7-day window, simulated sightings for that zone are ignored. Each officer `verified_sighting` report counts as a sighting, and a verified `patrol_survey` with no elephants adds nothing. Unverified reports are ignored. The result sets `officer_override` to `True`.

## Derived rules

The 54 `D` rules are generated from a score: `4 x sighting + 2 x distance + 2 x time + 1 x season`, where each factor is 0 (Low / Far / Day), 1 (Medium / Dusk) or 2 (High / Near / Night). A score below 7 is Low, 7–10 is Medium, 11–15 is Medium/High and 16 or more is High. Expert rules always take priority, and a test checks that raising any input never lowers the risk.

## Known limitations

- **Distance**: `categorize_distance()` uses `distance_to_forest_km` from `zone_table.py` as a stand-in for distance to an elephant corridor. The finalized `zones.json` has no such field yet, so it is `None` for every zone and treated as Medium. Ask the Spatial Search Lead for real values.
- **Cutoffs**: derived from the Fuzzy module's ranges, but not yet checked against the simulated movement dataset.
- **Derived rules**: formula-based, not reviewed by a domain expert.
- **Season**: uses `drought_index` from `weather_table.py` as a proxy for seasonal risk.

## Testing

```powershell
python -m pytest tests\test_rule_engine.py tests\test_rules.py tests\test_zone_flagger.py tests\test_risk_labels.py tests\test_rule_coverage.py
```