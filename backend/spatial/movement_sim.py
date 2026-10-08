"""Correlated random walk over the zone graph (herds may stay, avoid instant back-tracking)."""

import numpy as np

STAY_FACTOR = 12.0      # elephants linger ~1 day per 10 km zone: staying dominates moving
BACKTRACK_FACTOR = 0.6  # directional persistence: stepping straight back is less likely


def attractiveness(zone, season="dry"):
    score = 1.0
    if zone.get("distance_to_water_km") is not None:
        score += max(0, 3 - zone["distance_to_water_km"])
    if season == "dry":
        score += 1.5
    if zone.get("flood_prone"):
        score += 0.5
    return score


def crw_step(current_zone, zones, season="dry", previous_zone=None, rng=None):
    """Next zone: a neighbour or the current zone (stay). Weighted, heading-correlated."""
    rng = rng or np.random
    neighbors = list(zones[current_zone]["neighbors"])
    if not neighbors:
        return current_zone
    candidates = neighbors + [current_zone]
    weights = []
    for zone_id in neighbors:
        w = attractiveness(zones[zone_id], season)
        if zone_id == previous_zone:
            w *= BACKTRACK_FACTOR
        weights.append(w)
    weights.append(attractiveness(zones[current_zone], season) * STAY_FACTOR)
    weights = np.array(weights, dtype=float)
    return str(rng.choice(candidates, p=weights / weights.sum()))


def simulate_herds(zones, n_herds=6, n_cycles=200, season="dry", seed=None):
    rng = np.random.RandomState(seed) if seed is not None else np.random
    ids = list(zones)
    positions = {f"herd{i}": str(rng.choice(ids)) for i in range(n_herds)}
    previous = {h: None for h in positions}
    sizes = {h: int(rng.randint(1, 12)) for h in positions}  # herd size stays stable
    history = []
    for cycle in range(n_cycles):
        for herd_id, current in positions.items():
            nxt = crw_step(current, zones, season, previous[herd_id], rng)
            previous[herd_id] = current if nxt != current else previous[herd_id]
            positions[herd_id] = nxt
            history.append({"sighting_id": f"SIM-{cycle}-{herd_id}", "zone_id": nxt,
                            "timestamp_cycle": cycle, "elephant_count": sizes[herd_id],
                            "source": "simulated", "verified": False})
    return history