"""Movement prediction helpers for simulated history and shared tables."""

from collections import defaultdict

from ..tables.markov_transition_table import transition_matrix


def transition_probabilities():
    result = {}
    for row in transition_matrix:
        values = {
            row["current_zone"]: row["P_stay"],
            row["neighbour_A"]: row["P_neighbour_A"],
            row["neighbour_B"]: row["P_neighbour_B"],
        }
        total = sum(values.values()) or 1.0
        result[row["current_zone"]] = {key: value / total for key, value in values.items()}
    return result


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
