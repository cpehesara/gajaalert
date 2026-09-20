from .rules_table import RULES


def evaluate_rules(sighting_freq, distance, time_of_day, season):
    for rule in RULES:
        if (
            rule["sighting"] == sighting_freq
            and rule["distance"] == distance
            and rule["time"] == time_of_day
            and rule["season"] == season
        ):
            return rule["risk"]

    return "Undetermined"


def get_matching_rules(sighting, distance, time, season):
    """
    Return ALL rules that match the given conditions (not just the
    first one). Useful when multiple rules could apply, or when you
    want to see the full set of triggered rules for explainability.
    """
    matched_rules = []
    for rule in RULES:
        if (rule["sighting"] == sighting and
            rule["distance"] == distance and
            rule["time"] == time and
            rule["season"] == season):
            matched_rules.append(rule)
    return matched_rules


if __name__ == "__main__":
    print(get_matching_rules("High", "Near", "Night", "High"))