import osmnx as ox

# NOTE: 'Galgamuwa, Sri Lanka' does not geocode to a polygon via Nominatim
# (confirmed: TypeError - Nominatim returns a non-polygon geometry type
# for this query). Using a manually-set bounding box instead.
#
# osmnx 2.1.1 expects bbox as a single tuple in (west, south, east, north) order.
# Confirmed working after fixing an earlier coordinate-order bug that caused
# a 15,800x oversized query and a connection timeout.

WEST, SOUTH, EAST, NORTH = 80.20, 7.90, 80.40, 8.05

def extract_roads():
    return ox.graph_from_bbox((WEST, SOUTH, EAST, NORTH), network_type='drive')
