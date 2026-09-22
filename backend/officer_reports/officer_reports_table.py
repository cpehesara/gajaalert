"""
officer_reports_table.py

Officer-verified reports / patrol survey table for GajaAlert.
Stores DWC field officer submissions — verified sightings and patrol
survey entries — which take precedence over simulated elephant
positions for the corresponding zone and time window.
"""

officer_reports = [
    {
        "report_id": "OR001",
        "officer_id": "DWC-014",
        "zone_id": "Z07",
        "date": "2026-08-10",
        "time": "19:45",
        "report_type": "verified_sighting",
        "number_of_elephants": 4,
        "notes": "Small herd moving toward paddy field near village boundary",
        "verified": True
    },
    {
        "report_id": "OR002",
        "officer_id": "DWC-009",
        "zone_id": "Z03",
        "date": "2026-08-11",
        "time": "06:20",
        "report_type": "patrol_survey",
        "number_of_elephants": 0,
        "notes": "No elephant activity observed during morning patrol",
        "verified": True
    },
    {
        "report_id": "OR003",
        "officer_id": "DWC-014",
        "zone_id": "Z09",
        "date": "2026-08-12",
        "time": "21:10",
        "report_type": "verified_sighting",
        "number_of_elephants": 1,
        "notes": "Lone bull elephant near electric fence, dispersed after noise deterrent",
        "verified": True
    },
]


def get_reports_by_zone(zone_id):
    """Return all officer reports for a given zone."""
    return [r for r in officer_reports if r["zone_id"] == zone_id]


def get_latest_report(zone_id):
    """Return the most recent officer report for a given zone, or None."""
    records = get_reports_by_zone(zone_id)
    if not records:
        return None
    return sorted(records, key=lambda r: (r["date"], r["time"]), reverse=True)[0]


def has_verified_override(zone_id, date):
    """
    Check whether a verified officer report exists for a zone on a given
    date — used to override simulated elephant positions for that
    zone/time window.
    """
    return any(
        r["zone_id"] == zone_id and r["date"] == date and r["verified"]
        for r in officer_reports
    )


if __name__ == "__main__":
    for report in officer_reports:
        print(report)

    print("\nLatest report for Z07:", get_latest_report("Z07"))
    print("Override exists for Z07 on 2026-08-10:", has_verified_override("Z07", "2026-08-10"))