from backend.rules.rule_engine import evaluate_rules


def test_known_rule_matches():
    assert evaluate_rules("High", "Near", "Night", "High") == "High"


def test_unknown_or_missing_rule_is_safe():
    assert evaluate_rules("High", "Far", "Day", None) == "Undetermined"
    assert evaluate_rules("unknown", "Far", "Day", "Low") == "Undetermined"