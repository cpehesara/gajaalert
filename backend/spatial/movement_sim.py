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
    neighbors = list(zones[current_zone]["neighbors"].keys())
    if not neighbors:
        return current_zone

    scores = np.array([attractiveness(zones[n], season) for n in neighbors], dtype=float)
    scores = np.clip(scores, 1e-6, None)
    probs = scores / scores.sum()

    return str(np.random.choice(neighbors, p=probs))

def simulate_herds(zones, n_herds=6, n_cycles=200, season="dry"):
    history = []
    zone_ids = list(zones.keys())
    positions = {f"herd{i}": np.random.choice(zone_ids) for i in range(n_herds)}

    for cycle in range(n_cycles):
        for herd_id, current_zone in positions.items():
            next_zone = crw_step(current_zone, zones, season)
            history.append({
                "sighting_id": f"SIM-{cycle}-{herd_id}",
                "zone_id": next_zone,
                "timestamp_cycle": cycle,
                "elephant_count": int(np.random.randint(1, 6)),
                "source": "simulated",
                "verified": False
            })
            positions[herd_id] = next_zone

    return history
