"""Optional GIS extraction with a local cache and lazy dependency loading."""

import os
import pickle

WEST, SOUTH, EAST, NORTH = 80.20, 7.90, 80.40, 8.05
CACHE_PATH = "backend/data/roads_cache.pkl"


def extract_roads(use_cache=True):
    if use_cache and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as handle:
            return pickle.load(handle)
    try:
        import osmnx as ox
    except ImportError as exc:
        raise RuntimeError("Install osmnx to fetch live Galgamuwa GIS data") from exc
    graph = ox.graph_from_bbox((WEST, SOUTH, EAST, NORTH), network_type="drive")
    os.makedirs("backend/data", exist_ok=True)
    with open(CACHE_PATH, "wb") as handle:
        pickle.dump(graph, handle)
    return graph


def extract_galgamuwa_graph():
    try:
        import osmnx as ox
    except ImportError as exc:
        raise RuntimeError("Install osmnx to fetch live Galgamuwa GIS data") from exc
    return ox.graph_from_place("Galgamuwa, Kurunegala District, Sri Lanka", network_type="drive")
