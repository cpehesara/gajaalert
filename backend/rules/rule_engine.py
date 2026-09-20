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