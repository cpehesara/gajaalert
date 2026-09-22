import os
import pickle
import osmnx as ox

# NOTE: 'Galgamuwa, Sri Lanka' does not geocode to a polygon via Nominatim
# (confirmed: TypeError - Nominatim returns a non-polygon geometry type
# for this query). Using a manually-set bounding box instead.
#
# osmnx 2.1.1 expects bbox as a single tuple in (west, south, east, north) order.

WEST, SOUTH, EAST, NORTH = 80.20, 7.90, 80.40, 8.05
CACHE_PATH = "backend/data/roads_cache.pkl"

def extract_roads(use_cache=True):
    if use_cache and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            return pickle.load(f)

    G = ox.graph_from_bbox((WEST, SOUTH, EAST, NORTH), network_type="drive")

    os.makedirs("backend/data", exist_ok=True)
    with open(CACHE_PATH, "wb") as f:
        pickle.dump(G, f)

    return G
