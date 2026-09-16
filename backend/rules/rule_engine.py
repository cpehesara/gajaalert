"""
rule_engine.py - Rule-based AI reasoning module for GajaAlert.

Evaluates discrete contextual indicators against the defined rule base
(RULES from rules_table.py) and returns an explainable risk categorization.
"""

from .rules_table import RULES


def evaluate_rules(sighting_freq, distance, time_of_day, season):
    """
    Evaluate sighting and contextual indicators against defined expert rules.

    Args:
        sighting_freq (str): Sighting frequency ("Low", "Medium", "High")
        distance (str): Distance to corridor/refuge ("Near", "Medium", "Far")
        time_of_day (str): Time category ("Day", "Dusk", "Night")
        season (str): Seasonal risk category ("Low", "Medium", "High")

    Returns:
        str: Risk classification ("High", "Medium/High", "Medium", "Low", or "Undetermined")
    """
    if not all([sighting_freq, distance, time_of_day, season]):
        return "Undetermined"

    sighting_norm = str(sighting_freq).strip().title()
    distance_norm = str(distance).strip().title()
    time_norm = str(time_of_day).strip().title()
    season_norm = str(season).strip().title()

    for rule in RULES:
        if (
            rule["sighting"].title() == sighting_norm
            and rule["distance"].title() == distance_norm
            and rule["time"].title() == time_norm
            and rule["season"].title() == season_norm
        ):
            return rule["risk"]

    return "Undetermined"


def explain_rule_evaluation(sighting_freq, distance, time_of_day, season):
    """
    Evaluate rules and return detailed explanation including matched rule ID.

    Returns:
        dict: Evaluation result with matched_rule, risk, and factors.
    """
    sighting_norm = str(sighting_freq).strip().title() if sighting_freq else "Unknown"
    distance_norm = str(distance).strip().title() if distance else "Unknown"
    time_norm = str(time_of_day).strip().title() if time_of_day else "Unknown"
    season_norm = str(season).strip().title() if season else "Unknown"

    for rule in RULES:
        if (
            rule["sighting"].title() == sighting_norm
            and rule["distance"].title() == distance_norm
            and rule["time"].title() == time_norm
            and rule["season"].title() == season_norm
        ):
            return {
                "matched_rule_id": rule.get("id"),
                "risk": rule["risk"],
                "explanation": f"Matched Rule {rule.get('id')}: Sighting={sighting_norm}, Distance={distance_norm}, Time={time_norm}, Season={season_norm}",
                "success": True
            }

    return {
        "matched_rule_id": None,
        "risk": "Undetermined",
        "explanation": "No matching discrete rule found in knowledge base. Deferred to fuzzy inference.",
        "success": False
    }


if __name__ == "__main__":
    test_cases = [
        ("High", "Near", "Night", "High"),
        ("Low", "Far", "Day", "Low"),
        ("Medium", "Far", "Dusk", "Medium"),
        ("High", "Far", "Day", "Low"),  # Not in table
    ]
    for s, d, t, se in test_cases:
        print(f"Eval({s}, {d}, {t}, {se}) -> {evaluate_rules(s, d, t, se)}")
