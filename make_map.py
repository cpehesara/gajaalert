import osmnx as ox
from backend.spatial.gis_extract import extract_roads

print("Fetching roads...")
G = extract_roads()
print(f"Loaded {len(G.nodes)} nodes, {len(G.edges)} edges")

nodes, edges = ox.graph_to_gdfs(G)
m = edges.explore(color="gray", tiles="CartoDB positron")
m.save("galgamuwa_check.html")
print("Saved galgamuwa_check.html")
