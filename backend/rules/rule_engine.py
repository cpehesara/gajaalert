"""Explainable rule-based risk evaluation."""

from .rules_table import RULES


def _normalise(value):
    return str(value).strip().title() if value else None


def get_matching_rules(sighting, distance, time, season):
    values = [_normalise(item) for item in (sighting, distance, time, season)]
    if not all(values):
        return []
    sighting, distance, time, season = values
    return [
        rule for rule in RULES
        if (
            rule["sighting"].title() == sighting
            and rule["distance"].title() == distance
            and rule["time"].title() == time
            and rule["season"].title() == season
        )
    ]


def evaluate_rules(sighting_freq, distance, time_of_day, season):
    matches = get_matching_rules(sighting_freq, distance, time_of_day, season)
    return matches[0]["risk"] if matches else "Undetermined"


def explain_rule_evaluation(sighting_freq, distance, time_of_day, season):
    matches = get_matching_rules(sighting_freq, distance, time_of_day, season)
    if matches:
        rule = matches[0]
        return {
            "matched_rule_id": rule.get("id"),
            "risk": rule["risk"],
            "explanation": f"Matched Rule {rule.get('id')}",
            "success": True,
        }
    return {
        "matched_rule_id": None,
        "risk": "Undetermined",
        "explanation": "No matching discrete rule found in knowledge base.",
        "success": False,
    }
