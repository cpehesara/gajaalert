"""Offline movement simulation and a deterministic correlated walk helper."""

import random
import numpy as np


def attractiveness(zone, season="dry"):
    score = 1.0
    if zone.get("distance_to_water_km") is not None:
        score += max(0, 3 - zone["distance_to_water_km"])
    if season == "dry":
        score += 1.5
    if zone.get("flood_prone"):
        score += 0.5
    return score


def crw_step(current_zone, zones, season="dry"):
    neighbors = list(zones[current_zone]["neighbors"])
    if not neighbors:
        return current_zone
    scores = np.array([attractiveness(zones[neighbor], season) for neighbor in neighbors], dtype=float)
    return str(np.random.choice(neighbors, p=scores / scores.sum()))


def correlated_random_walk_step(current_zone, previous_zone, graph, attractiveness_fn=None, rng=None):
    neighbors = list(graph.get(current_zone, {}))
    if not neighbors:
        return current_zone
    attractiveness_fn = attractiveness_fn or (lambda zone: 1.0)
    weights = [max(0.0, float(attractiveness_fn(zone))) * (1.25 if zone == previous_zone else 1.0)
               for zone in neighbors]
    chooser = rng or random
    return chooser.choices(neighbors, weights=weights, k=1)[0]


def simulate_herds(zones, n_herds=6, n_cycles=200, season="dry"):
    positions = {f"herd{index}": np.random.choice(list(zones)) for index in range(n_herds)}
    history = []
    for cycle in range(n_cycles):
        for herd_id, current_zone in positions.items():
            next_zone = crw_step(current_zone, zones, season)
            history.append({"sighting_id": f"SIM-{cycle}-{herd_id}", "zone_id": next_zone,
                            "timestamp_cycle": cycle, "elephant_count": int(np.random.randint(1, 6)),
                            "source": "simulated", "verified": False})
            positions[herd_id] = next_zone
    return history
