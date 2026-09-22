"""
zone_risk_table.py

Zone risk / output table for GajaAlert.
Stores the final HEC risk output per zone, produced by combining the
fuzzy risk score with the Markov movement prediction. This is the
data consumed by the early-warning component and passed to the A*
patrol-route module.
"""

zone_risk_data = [
    {
        "zone_id": "Z07",
        "date": "2026-08-10",
        "time_window": "18:00-00:00",
        "hec_risk_score": 84,
        "risk_category": "High",
        "contributing_factors": [
            "High recent sighting frequency",
            "Close proximity to elephant corridor",
            "Dusk/night conditions"
        ],
        "predicted_next_6h_distribution": {
            "Z07": 0.62,
            "Z09": 0.24,
            "Z08": 0.14
        },
        "priority_status": "High",
        "early_warning_triggered": True
    },
    {
        "zone_id": "Z03",
        "date": "2026-08-11",
        "time_window": "06:00-12:00",
        "hec_risk_score": 22,
        "risk_category": "Low",
        "contributing_factors": [
            "No recent sightings",
            "Far from known corridor"
        ],
        "predicted_next_6h_distribution": {
            "Z03": 0.80,
            "Z04": 0.20
        },
        "priority_status": "Low",
        "early_warning_triggered": False
    },
    {
        "zone_id": "Z09",
        "date": "2026-08-12",
        "time_window": "18:00-00:00",
        "hec_risk_score": 58,
        "risk_category": "Medium",
        "contributing_factors": [
            "Medium sighting frequency",
            "Moderate distance to corridor",
            "Dry season"
        ],
        "predicted_next_6h_distribution": {
            "Z09": 0.50,
            "Z07": 0.30,
            "Z10": 0.20
        },
        "priority_status": "Medium",
        "early_warning_triggered": False
    },
]


def get_risk_by_zone(zone_id):
    """Return all risk records for a given zone."""
    return [r for r in zone_risk_data if r["zone_id"] == zone_id]


def get_latest_risk(zone_id):
    """Return the most recent risk record for a given zone, or None."""
    records = get_risk_by_zone(zone_id)
    if not records:
        return None
    return sorted(records, key=lambda r: r["date"], reverse=True)[0]


def get_high_priority_zones():
    """Return all zone records currently flagged as High priority."""
    return [r for r in zone_risk_data if r["priority_status"] == "High"]


def get_early_warning_zones():
    """Return all zone records where an early warning has been triggered."""
    return [r for r in zone_risk_data if r["early_warning_triggered"]]


if __name__ == "__main__":
    for record in zone_risk_data:
        print(record)

    print("\nLatest risk for Z07:", get_latest_risk("Z07"))
    print("High priority zones:", [r["zone_id"] for r in get_high_priority_zones()])
    print("Early warning zones:", [r["zone_id"] for r in get_early_warning_zones()])