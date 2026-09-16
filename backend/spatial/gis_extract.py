"""Optional OSMnx extraction; imports lazily so offline tests stay lightweight."""


def extract_galgamuwa_graph():
    try:
        import osmnx as ox
    except ImportError as exc:
        raise RuntimeError("Install osmnx to fetch live Galgamuwa GIS data") from exc
    return ox.graph_from_place("Galgamuwa, Kurunegala District, Sri Lanka", network_type="drive")