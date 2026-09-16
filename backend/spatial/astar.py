"""A* patrol routing with graceful handling for disconnected zones."""

import heapq

from .zone_graph import build_graph, straight_line_distance


def astar(graph, start, goal, coordinates=None):
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
                if coordinates and neighbor in coordinates and goal in coordinates:
                    a, b = coordinates[neighbor], coordinates[goal]
                    heuristic = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
                heapq.heappush(queue, (candidate + heuristic, neighbor, path + [neighbor]))
    return None, float("inf")


def get_patrol_route(start_zone, priority_zones, graph=None):
    graph = graph or build_graph()
    route = [start_zone]
    total = 0.0
    current = start_zone
    for target in priority_zones:
        path, distance = astar(graph, current, target)
        if not path:
            continue
        route.extend(path[1:])
        total += distance
        current = target
    return {"route": route, "total_distance_km": float(total), "estimated_time_minutes": int(round(total * 7.5))}