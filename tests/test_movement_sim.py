import numpy as np
import pytest
from backend.spatial.zone_graph import load_zones
from backend.spatial.movement_sim import simulate_herds, crw_step

@pytest.fixture
def zones():
    return load_zones()

def test_simulation_stays_on_graph(zones):
    history = simulate_herds(zones, n_herds=2, n_cycles=20)
    valid_ids = set(zones.keys())
    assert all(record["zone_id"] in valid_ids for record in history)

def test_crw_step_returns_valid_neighbor(zones):
    start = list(zones.keys())[0]
    next_zone = crw_step(start, zones)
    assert next_zone in zones[start]["neighbors"] or next_zone == start

def test_record_count_matches_herds_and_cycles(zones):
    history = simulate_herds(zones, n_herds=3, n_cycles=10)
    assert len(history) == 30
