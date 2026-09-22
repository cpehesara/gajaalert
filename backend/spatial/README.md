# Spatial Search Module - GajaAlert

## Public Functions (for Integration Lead)

### load_zones(path="backend/data/zones.json") -> dict
Returns zone_id -> zone object mapping. Call this first.

### plan_patrol_route(zones, start_zone, priority_zones) -> dict
Returns {"route": [...], "total_distance_km": float, "unreached_zones": [...]}.
Empty priority_zones returns a single-zone hold-position route, not an error.

### predict_movement(transition_matrix, zone_id, zones) -> dict
Returns {"zone_id": ..., "predicted_transitions": {...}}.
Falls back to equal-probability across neighbors if no simulated history exists for that zone.

### prioritize_zones(fuzzy_scores, transition_matrix, zones, threshold=60) -> list
Takes the Fuzzy Lead's risk score dict (schema: {zone_id: risk score object}),
returns list of zone_ids to prioritize for patrol.

## Data Files
- backend/data/zones.json - the zone graph (10 zones, GIS-derived, validated connected)
- backend/data/roads_cache.pkl - cached OSM road network (avoids live API calls)
- backend/data/movement_history.json - simulated elephant movement (6 herds, 200 cycles)
- backend/data/transition_matrix.json - precomputed Markov transition probabilities

## Known Failure Modes (handled explicitly, not silent)
- Unreachable zone in A* -> returns None
- Empty priority list -> returns hold-position route
- Zone with no movement history -> Markov falls back to equal-probability estimate
- Isolated zone (no neighbors at all) -> returns empty predicted_transitions with a note

## Running Tests
pytest tests/ -v
Requires pytest.ini at project root (already committed) for import path resolution.
