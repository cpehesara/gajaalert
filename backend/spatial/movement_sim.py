"""Small normalized correlated random-walk step for offline simulation."""

import random


def correlated_random_walk_step(current_zone, previous_zone, graph, attractiveness=None, rng=None):
    neighbors = list(graph.get(current_zone, {}))
    if not neighbors:
        return current_zone
    attractiveness = attractiveness or (lambda zone: 1.0)
    weights = [max(0.0, float(attractiveness(zone))) * (1.25 if zone == previous_zone else 1.0) for zone in neighbors]
    total = sum(weights) or 1.0
    chooser = rng or random
    return chooser.choices(neighbors, weights=[weight / total for weight in weights], k=1)[0]