"""A* routing for either zone records or plain adjacency graphs."""

import heapq
import math


def euclidean(coord1, coord2):
    return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)


def _zone_records(graph):
    return bool(graph) and all(isinstance(value, dict) and "neighbors" in value for value in graph.values())


def astar(graph, start, goal, coordinates=None):
    if _zone_records(graph):
        coordinates = {key: (value["lat"], value["lng"]) for key, value in graph.items()}
        adjacency = {key: value["neighbors"] for key, value in graph.items()}
        result = _astar_graph(adjacency, start, goal, coordinates)
        if result is None or result[0] is None:
            return None
        path, distance = result
        return {"route": path, "total_distance_km": distance}
    return _astar_graph(graph, start, goal, coordinates)


def _astar_graph(graph, start, goal, coordinates=None):
    if start not in graph or goal not in graph:
        return None, float("inf")
    coordinates = coordinates or {}
    queue = [(0.0, start, [start])]
    costs = {start: 0.0}
    while queue:
        _, current, path = heapq.heappop(queue)
        if current == goal:
            return path, costs[current]
        for neighbor, weight in graph[current].items():
            candidate = costs[current] + float(weight)
            if candidate < costs.get(neighbor, float("inf")):
                costs[neighbor] = candidate
                heuristic = 0.0
                if neighbor in coordinates and goal in coordinates:
                    heuristic = euclidean(coordinates[neighbor], coordinates[goal])
                heapq.heappush(queue, (candidate + heuristic, neighbor, path + [neighbor]))
    return None, float("inf")


def plan_patrol_route(zones, start_zone, priority_zones):
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
                best, best_target = result, target
        if best is None:
            break
        route.extend(best["route"][1:])
        total_distance += best["total_distance_km"]
        current = best_target
        remaining.remove(best_target)
    return {"route": route, "total_distance_km": round(total_distance, 2), "unreached_zones": remaining}


def get_patrol_route(start_zone, priority_zones, graph=None):
    from .zone_graph import build_graph

    graph = graph or build_graph()
    route = [start_zone]
    total = 0.0
    current = start_zone
    for target in priority_zones:
        path, distance = astar(graph, current, target)
        if path:
            route.extend(path[1:])
            total += distance
            current = target
    return {"route": route, "total_distance_km": total, "estimated_time_minutes": int(round(total * 7.5))}
