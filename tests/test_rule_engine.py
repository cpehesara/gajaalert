from backend.rules.rule_engine import evaluate_rules


def test_evaluate_rules_returns_matching_risk_for_known_rule():
    assert evaluate_rules("High", "Near", "Night", "High") == "High"
    assert evaluate_rules("Low", "Far", "Day", "Low") == "Low"


def test_evaluate_rules_returns_undetermined_for_unknown_combination():
    assert evaluate_rules("High", "Far", "Day", "High") == "Undetermined"
