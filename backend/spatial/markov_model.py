from collections import defaultdict

def build_transition_matrix(history):
    herd_sequences = defaultdict(list)
    for record in sorted(history, key=lambda r: r["timestamp_cycle"]):
        herd_id = record["sighting_id"].split("-")[-1]
        herd_sequences[herd_id].append(record["zone_id"])

    transition_counts = defaultdict(lambda: defaultdict(int))
    for sequence in herd_sequences.values():
        for i in range(len(sequence) - 1):
            transition_counts[sequence[i]][sequence[i+1]] += 1

    transition_matrix = {}
    for zone_id, next_counts in transition_counts.items():
        total = sum(next_counts.values())
        transition_matrix[zone_id] = {
            next_zone: round(count / total, 3)
            for next_zone, count in next_counts.items()
        }
    return transition_matrix

def predict_movement(transition_matrix, current_zone, zones):
    if current_zone not in transition_matrix:
        neighbors = list(zones[current_zone]["neighbors"].keys())
        if not neighbors:
            return {"zone_id": current_zone, "predicted_transitions": {}, "note": "isolated zone, no data"}
        equal_prob = round(1 / len(neighbors), 3)
        return {"zone_id": current_zone,
                "predicted_transitions": {n: equal_prob for n in neighbors},
                "note": "fallback: no simulated history for this zone"}
    return {"zone_id": current_zone, "predicted_transitions": transition_matrix[current_zone]}

def validate_transition_matrix(matrix):
    for zone_id, transitions in matrix.items():
        total = sum(transitions.values())
        assert abs(total - 1.0) < 0.01, f"{zone_id} sums to {total}, not 1.0"
    return True

def prioritize_zones(fuzzy_scores, transition_matrix, zones, threshold=60):
    priority = []
    for zone_id, score_obj in fuzzy_scores.items():
        current_risk = score_obj["risk_score"]
        predicted = predict_movement(transition_matrix, zone_id, zones)
        max_transition_prob = max(predicted["predicted_transitions"].values(), default=0)
        if current_risk >= threshold or max_transition_prob > 0.5:
            priority.append(zone_id)
    return priority
