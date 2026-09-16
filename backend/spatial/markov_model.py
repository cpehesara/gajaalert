"""Markov movement prediction backed by the shared transition table."""

from ..tables.markov_transition_table import transition_matrix


def transition_probabilities():
    result = {}
    for row in transition_matrix:
        values = {row["current_zone"]: row["P_stay"], row["neighbour_A"]: row["P_neighbour_A"], row["neighbour_B"]: row["P_neighbour_B"]}
        total = sum(values.values()) or 1.0
        result[row["current_zone"]] = {key: value / total for key, value in values.items()}
    return result


def predict_movement(zone_id):
    probabilities = transition_probabilities().get(zone_id, {})
    return {"zone_id": zone_id, "current_probability": probabilities.get(zone_id, 0.0), "predicted_transitions": probabilities, "predicted_risk_window_hours": 6}