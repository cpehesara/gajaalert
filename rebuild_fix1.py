"""Fix 1: make the zone graph two-way, regenerate simulation + Markov matrix.
Run from project root:  python rebuild_fix1.py
"""
import json
from collections import deque

ZONES = "backend/data/zones.json"

# 1) symmetrize graph (keep the shorter distance if both directions exist)
with open(ZONES, encoding="utf-8") as f:
    zone_list = json.load(f)
zones = {z["zone_id"]: z for z in zone_list}
for zid, z in zones.items():
    for nid, d in list(z["neighbors"].items()):
        back = zones[nid]["neighbors"]
        back[zid] = min(d, back.get(zid, d))
        z["neighbors"][nid] = back[zid]
with open(ZONES, "w", encoding="utf-8") as f:
    json.dump(zone_list, f, indent=2)

# 2) connectivity proof
start = next(iter(zones))
seen, queue = {start}, deque([start])
while queue:
    for n in zones[queue.popleft()]["neighbors"]:
        if n not in seen:
            seen.add(n); queue.append(n)
assert seen == set(zones), f"still disconnected: {set(zones) - seen}"
print("Graph connected, all", len(zones), "zones reachable both ways")

# 3) regenerate simulation + Markov matrix
from backend.spatial.movement_sim import simulate_herds
from backend.spatial.markov_model import build_transition_matrix, validate_transition_matrix

history = simulate_herds(zones, n_herds=6, n_cycles=200, seed=42)
matrix = build_transition_matrix(history)
validate_transition_matrix(matrix)
missing = set(zones) - set(matrix)
print("Zones without a Markov row (will use fallback):", sorted(missing) or "none")
with open("backend/data/movement_history.json", "w") as f:
    json.dump(history, f)
with open("backend/data/transition_matrix.json", "w") as f:
    json.dump(matrix, f, indent=2)
print("Wrote movement_history.json (%d records) and transition_matrix.json" % len(history))
for z in sorted(matrix):
    print(z, "stay=%.2f" % matrix[z].get(z, 0))