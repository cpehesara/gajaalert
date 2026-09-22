"""Helpers for converting shared zone records into adjacency graphs."""

from math import hypot

from ..tables.zone_table import zone_data


def load_zones(path="backend/data/zones.json"):
    import json
    with open(path, encoding="utf-8") as handle:
        return {zone["zone_id"]: zone for zone in json.load(handle)}


def build_graph(zones=None):
    records = zones or zone_data
    if isinstance(records, dict):
        return {key: dict(value.get("neighbors", {})) for key, value in records.items()}
    return {zone["zone_id"]: dict(zone.get("neighbors", {})) for zone in records}


def straight_line_distance(zone_a, zone_b, zones=None):
    records = zones or zone_data
    if isinstance(records, dict):
        records = records.values()
    records = {zone["zone_id"]: zone for zone in records}
    first, second = records[zone_a], records[zone_b]
    return hypot((first["lat"] - second["lat"]) * 111, (first["lng"] - second["lng"]) * 103)
