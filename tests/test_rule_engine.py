from backend.rules.rule_engine import evaluate_rules


def test_evaluate_rules_returns_matching_risk_for_known_rule():
    assert evaluate_rules("High", "Near", "Night", "High") == "High"
    assert evaluate_rules("Low", "Far", "Day", "Low") == "Low"


def test_evaluate_rules_returns_undetermined_for_unknown_combination():
    # Every valid label combination now has a rule; an unrecognised label does not.
    assert evaluate_rules("Medium", "Medium", "Day", "Unknown") == "Undetermined"
