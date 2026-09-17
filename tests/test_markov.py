import json
import pytest
from backend.spatial.zone_graph import load_zones
from backend.spatial.markov_model import build_transition_matrix, validate_transition_matrix, predict_movement, prioritize_zones

@pytest.fixture
def zones():
    return load_zones()

@pytest.fixture
def matrix():
    with open("backend/data/transition_matrix.json") as f:
        return json.load(f)

def test_matrix_rows_sum_to_one(matrix):
    assert validate_transition_matrix(matrix)

def test_predict_movement_known_zone(zones, matrix):
    zone_id = list(matrix.keys())[0]
    result = predict_movement(matrix, zone_id, zones)
    assert result["zone_id"] == zone_id
    assert sum(result["predicted_transitions"].values()) > 0

def test_predict_movement_fallback_for_unknown_zone(zones, matrix):
    fake_matrix = {}
    zone_id = list(zones.keys())[0]
    result = predict_movement(fake_matrix, zone_id, zones)
    assert "note" in result

def test_prioritize_zones_flags_high_risk(zones, matrix):
    zone_ids = list(zones.keys())
    fuzzy_scores = {
        zone_ids[0]: {"zone_id": zone_ids[0], "risk_score": 85, "risk_level": "High"},
        zone_ids[1]: {"zone_id": zone_ids[1], "risk_score": 20, "risk_level": "Low"},
    }
    priority = prioritize_zones(fuzzy_scores, matrix, zones)
    assert zone_ids[0] in priority
