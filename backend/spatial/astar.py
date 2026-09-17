import heapq
import math

def euclidean(coord1, coord2):
    return math.sqrt((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)

def astar(zones, start, goal):
    coords = {zid: (z["lat"], z["lng"]) for zid, z in zones.items()}
    open_set = [(0, start, [start])]
    g_score = {start: 0}

    while open_set:
        f, current, path = heapq.heappop(open_set)
        if current == goal:
            return {"route": path, "total_distance_km": g_score[current]}
        for neighbor, weight in zones[current]["neighbors"].items():
            tentative_g = g_score[current] + weight
            if tentative_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = tentative_g
                h = euclidean(coords[neighbor], coords[goal]) * 111
                heapq.heappush(open_set, (tentative_g + h, neighbor, path + [neighbor]))
    return None

def plan_patrol_route(zones, start_zone, priority_zones):
    if not priority_zones:
        return {"route": [start_zone], "total_distance_km": 0, "unreached_zones": []}

    route = [start_zone]
    total_distance = 0
    current = start_zone
    remaining = list(priority_zones)

    while remaining:
        best = None
        best_target = None
        for target in remaining:
            result = astar(zones, current, target)
            if result and (best is None or result["total_distance_km"] < best["total_distance_km"]):
                best = result
                best_target = target
        if best is None:
            break
        route.extend(best["route"][1:])
        total_distance += best["total_distance_km"]
        current = best_target
        remaining.remove(best_target)

    return {"route": route, "total_distance_km": round(total_distance, 2), "unreached_zones": remaining}
