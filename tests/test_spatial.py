from backend.spatial.astar import astar
from backend.spatial.markov_model import transition_probabilities


def test_astar_handles_path_and_unreachable_graphs():
    assert astar({"A": {"B": 2}, "B": {}}, "A", "B")[0] == ["A", "B"]
    assert astar({"A": {}, "B": {}}, "A", "B")[0] is None


def test_markov_rows_are_normalized():
    assert all(abs(sum(row.values()) - 1) < 1e-9 for row in transition_probabilities().values())