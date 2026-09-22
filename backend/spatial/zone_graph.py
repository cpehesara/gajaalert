import json

def load_zones(path="backend/data/zones.json"):
    with open(path) as f:
        zones_list = json.load(f)
    return {z["zone_id"]: z for z in zones_list}
