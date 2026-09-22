"""Membership functions for the HEC fuzzy risk model."""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

SIGHTING_UNIVERSE = np.arange(0, 15.01, 0.1)
DISTANCE_UNIVERSE = np.arange(0, 10.01, 0.1)
TIME_UNIVERSE = np.arange(0, 24.01, 0.1)
SEASON_UNIVERSE = np.arange(0, 100.1, 0.5)
RISK_UNIVERSE = np.arange(0, 100.1, 0.5)


def build_antecedents():
    """Create antecedents with overlapping curves and complete coverage."""
    sighting = ctrl.Antecedent(SIGHTING_UNIVERSE, "sighting_freq")
    distance = ctrl.Antecedent(DISTANCE_UNIVERSE, "distance_corridor")
    time = ctrl.Antecedent(TIME_UNIVERSE, "time_of_day")
    seasonal = ctrl.Antecedent(SEASON_UNIVERSE, "seasonal_risk")

    sighting["low"] = fuzz.trimf(sighting.universe, [0, 0, 4])
    sighting["medium"] = fuzz.trimf(sighting.universe, [2, 7, 10])
    sighting["high"] = fuzz.trimf(sighting.universe, [6, 15, 15])
    distance["near"] = fuzz.trimf(distance.universe, [0, 0, 2.5])
    distance["medium"] = fuzz.trimf(distance.universe, [1.5, 3, 5])
    distance["far"] = fuzz.trimf(distance.universe, [3.5, 10, 10])
    time["day"] = fuzz.trapmf(time.universe, [6, 6, 17, 18])
    time["dusk"] = fuzz.trimf(time.universe, [16, 18, 20])
    night = np.maximum(
        fuzz.trimf(time.universe, [19, 24, 24]),
        fuzz.trimf(time.universe, [0, 0, 7]),
    )
    time["night"] = night
    seasonal["low"] = fuzz.trimf(seasonal.universe, [0, 0, 45])
    seasonal["medium"] = fuzz.trimf(seasonal.universe, [30, 50, 70])
    seasonal["high"] = fuzz.trimf(seasonal.universe, [60, 100, 100])
    return sighting, distance, time, seasonal


def build_consequent():
    risk = ctrl.Consequent(RISK_UNIVERSE, "risk_score")
    risk["low"] = fuzz.trimf(risk.universe, [0, 0, 45])
    risk["medium"] = fuzz.trimf(risk.universe, [30, 50, 70])
    risk["high"] = fuzz.trimf(risk.universe, [55, 100, 100])
    return risk


def membership_label(variable, value):
    """Return the strongest membership label for a clipped input."""
    clipped = float(np.clip(value, variable.universe[0], variable.universe[-1]))
    memberships = {
        name: float(fuzz.interp_membership(variable.universe, term.mf, clipped))
        for name, term in variable.terms.items()
    }
    return max(memberships, key=memberships.get), memberships