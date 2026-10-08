"""Fill distance_to_water_km / distance_to_forest_km in backend/data/zones.json from OpenStreetMap.
Run from project root (needs internet + osmnx):  python populate_distances.py

Forest distance = distance to the nearest LARGE forest block or protected area (>= MIN_FOREST_KM2),
used as the elephant-habitat / corridor proxy (proposal Sec. 8.1). Small woodland patches are ignored,
otherwise every zone in this farmland mosaic would sit "next to a wood" and look identical.
"""
import json

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import Point

WEST, SOUTH, EAST, NORTH = 80.15, 7.85, 80.45, 8.10   # slightly wider than the zones
PATH = "backend/data/zones.json"
UTM = 32644            # UTM 44N, metres (covers Sri Lanka's 80E)
MIN_FOREST_KM2 = 2.0   # raise to separate zones more, lower to separate less


def nearest_km(zone_pt, gdf):
    if gdf is None or gdf.empty:
        return None
    return round(float(gdf.to_crs(UTM).geometry.distance(zone_pt).min()) / 1000, 2)


def large_blocks(gdf):
    polys = gdf[gdf.geom_type.isin(["Polygon", "MultiPolygon"])]
    big = polys[polys.to_crs(UTM).area / 1e6 >= MIN_FOREST_KM2]
    if big.empty:
        print("WARNING: no block >= %.1f km2 found; using all polygons" % MIN_FOREST_KM2)
        return polys
    return big


bbox = (WEST, SOUTH, EAST, NORTH)
water = ox.features_from_bbox(bbox=bbox, tags={"natural": "water", "waterway": ["river", "stream"]})
woods = ox.features_from_bbox(bbox=bbox, tags={"natural": "wood", "landuse": "forest"})
reserves = ox.features_from_bbox(bbox=bbox, tags={"boundary": "protected_area", "leisure": "nature_reserve"})
forest = large_blocks(gpd.GeoDataFrame(pd.concat([woods, reserves]), crs=woods.crs))
print("water:", len(water), "| all woodland:", len(woods), "| large forest/reserve blocks:", len(forest))

with open(PATH, encoding="utf-8") as handle:
    zones = json.load(handle)
for z in zones:
    pt = gpd.GeoSeries([Point(z["lng"], z["lat"])], crs=4326).to_crs(UTM).iloc[0]
    z["distance_to_water_km"] = nearest_km(pt, water)
    z["distance_to_forest_km"] = nearest_km(pt, forest)
    print(z["zone_id"], z["name"], "water", z["distance_to_water_km"], "forest", z["distance_to_forest_km"])
with open(PATH, "w", encoding="utf-8") as handle:
    json.dump(zones, handle, indent=2)
print("zones.json updated")