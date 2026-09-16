"""Zone graph helpers using the roadmap's zone contract."""

from math import hypot

from ..tables.zone_table import zone_data


def build_graph(zones=None):
    return {zone["zone_id"]: dict(zone.get("neighbors", {})) for zone in (zones or zone_data)}


def straight_line_distance(zone_a, zone_b, zones=None):
    records = {zone["zone_id"]: zone for zone in (zones or zone_data)}
    first, second = records[zone_a], records[zone_b]
    return hypot((first["lat"] - second["lat"]) * 111, (first["lng"] - second["lng"]) * 103)