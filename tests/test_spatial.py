import pytest
from backend.spatial.zone_graph import load_zones
from backend.spatial.astar import astar, plan_patrol_route

@pytest.fixture
def zones():
    return load_zones()

def test_direct_neighbor_route(zones):
    z1 = list(zones.keys())[0]
    z2 = list(zones[z1]["neighbors"].keys())[0]
    result = astar(zones, z1, z2)
    assert result is not None
    assert result["route"][0] == z1 and result["route"][-1] == z2

def test_unreachable_zone_returns_none(zones):
    fake_zones = {**zones, "Z_ISOLATED": {"zone_id": "Z_ISOLATED", "lat": 0, "lng": 0, "neighbors": {}}}
    result = astar(fake_zones, list(zones.keys())[0], "Z_ISOLATED")
    assert result is None

def test_empty_priority_list(zones):
    start = list(zones.keys())[0]
    result = plan_patrol_route(zones, start, [])
    assert result["route"] == [start]

def test_multi_zone_route(zones):
    start = list(zones.keys())[0]
    targets = list(zones.keys())[1:3]
    result = plan_patrol_route(zones, start, targets)
    assert result["route"][0] == start
    assert len(result["unreached_zones"]) == 0
