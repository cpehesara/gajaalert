"""Movement prediction helpers for simulated history and shared tables."""

import json
from collections import defaultdict
from pathlib import Path

from ..tables.zone_table import get_neighbours

_MATRIX_FILE = Path(__file__).resolve().parents[1] / "data" / "transition_matrix.json"


def transition_probabilities():
    """Load the simulated Markov transition matrix (single source of truth)."""
    with _MATRIX_FILE.open(encoding="utf-8") as handle:
        return json.load(handle)


def build_transition_matrix(history):
    sequences = defaultdict(list)
    for record in sorted(history, key=lambda item: item["timestamp_cycle"]):
        sequences[record["sighting_id"].split("-")[-1]].append(record["zone_id"])
    counts = defaultdict(lambda: defaultdict(int))
    for sequence in sequences.values():
        for current, following in zip(sequence, sequence[1:]):
            counts[current][following] += 1
    return {
        zone: {target: round(count / sum(values.values()), 3) for target, count in values.items()}
        for zone, values in counts.items()
    }


def validate_transition_matrix(matrix):
    for zone, probabilities in matrix.items():
        total = sum(probabilities.values())
        if abs(total - 1.0) >= 0.01:
            raise AssertionError(f"{zone} sums to {total}, not 1.0")
    return True


def predict_movement(*args):
    if len(args) == 1:
        zone_id = args[0]
        probabilities = transition_probabilities().get(zone_id, {})
        if not probabilities:
            neighbours = list(get_neighbours(zone_id))
            probabilities = {n: round(1 / len(neighbours), 3) for n in neighbours}
        return {"zone_id": zone_id, "current_probability": probabilities.get(zone_id, 0.0),
                "predicted_transitions": probabilities, "predicted_risk_window_hours": 6}
    transition_matrix_value, current_zone, zones = args
    probabilities = transition_matrix_value.get(current_zone)
    if probabilities is not None:
        return {"zone_id": current_zone, "predicted_transitions": probabilities}
    neighbors = list(zones[current_zone]["neighbors"])
    fallback = {neighbor: round(1 / len(neighbors), 3) for neighbor in neighbors} if neighbors else {}
    return {"zone_id": current_zone, "predicted_transitions": fallback,
            "note": "fallback: no simulated history for this zone"}


def prioritize_zones(fuzzy_scores, transition_matrix_value, zones, threshold=60):
    priority = []
    for zone_id, score in fuzzy_scores.items():
        prediction = predict_movement(transition_matrix_value, zone_id, zones)
        maximum = max(prediction["predicted_transitions"].values(), default=0)
        if score["risk_score"] >= threshold or maximum > 0.5:
            priority.append(zone_id)
    return priority