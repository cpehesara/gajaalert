import itertools

from backend.rules.rule_engine import RISK_LEVELS, evaluate_rules
from backend.rules.rules_table import RULES

SIGHTING = ["Low", "Medium", "High"]
DISTANCE = ["Far", "Medium", "Near"]
TIME = ["Day", "Dusk", "Night"]
SEASON = ["Low", "Medium", "High"]
RANK = {"Low": 0, "Medium": 1, "Medium/High": 2, "High": 3}


def test_every_combination_has_exactly_one_rule():
    keys = [(r["sighting"], r["distance"], r["time"], r["season"]) for r in RULES]
    assert len(keys) == len(set(keys)), "duplicate rule combination"
    assert set(keys) == set(itertools.product(SIGHTING, DISTANCE, TIME, SEASON))
    assert len(RULES) == 81


def test_expert_and_derived_rule_counts():
    expert = [r for r in RULES if r["id"].startswith("R")]
    derived = [r for r in RULES if r["id"].startswith("D")]
    assert len(expert) == 27
    assert len(derived) == 54


def test_all_valid_combinations_are_determined():
    for combo in itertools.product(SIGHTING, DISTANCE, TIME, SEASON):
        assert evaluate_rules(*combo) in RISK_LEVELS[:-1]


def test_invalid_labels_are_still_undetermined():
    assert evaluate_rules("Medium", "Medium", "Day", "Unknown") == "Undetermined"
    assert evaluate_rules("???", "Near", "Night", "High") == "Undetermined"


def test_more_risk_factors_never_lower_the_risk():
    """Raising any one input (with the others fixed) must not reduce the risk."""
    scales = [SIGHTING, DISTANCE, TIME, SEASON]  # each ordered low -> high risk
    for combo in itertools.product(*scales):
        for i, scale in enumerate(scales):
            pos = scale.index(combo[i])
            if pos + 1 < len(scale):
                higher = list(combo)
                higher[i] = scale[pos + 1]
                assert RANK[evaluate_rules(*higher)] >= RANK[evaluate_rules(*combo)], (combo, higher)
