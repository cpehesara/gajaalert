from backend.rules.rule_engine import RISK_LEVELS
from backend.rules.rules_table import RULES


def test_every_rule_uses_a_known_risk_label():
    for rule in RULES:
        assert rule["risk"] in RISK_LEVELS, f"{rule['id']} has unknown label {rule['risk']}"