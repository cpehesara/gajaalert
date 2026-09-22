import pickle
from backend.spatial.gis_extract import extract_roads

print("Fetching and caching roads (one-time)...")
G = extract_roads()
with open("backend/data/roads_cache.pkl", "wb") as f:
    pickle.dump(G, f)
print(f"Cached {len(G.nodes)} nodes, {len(G.edges)} edges to backend/data/roads_cache.pkl")
