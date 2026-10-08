"""Officer-verified reports. Verified reports take precedence over simulated data."""

officer_reports = [
    {"report_id": "OR001", "officer_id": "DWC-014", "zone_id": "Z07", "date": "2026-08-10", "time": "19:45",
     "report_type": "verified_sighting", "number_of_elephants": 4,
     "notes": "Small herd moving toward paddy field near village boundary", "verified": True},
    {"report_id": "OR002", "officer_id": "DWC-009", "zone_id": "Z03", "date": "2026-08-11", "time": "06:20",
     "report_type": "patrol_survey", "number_of_elephants": 0,
     "notes": "No elephant activity observed during morning patrol", "verified": True},
    {"report_id": "OR003", "officer_id": "DWC-014", "zone_id": "Z09", "date": "2026-08-12", "time": "21:10",
     "report_type": "verified_sighting", "number_of_elephants": 1,
     "notes": "Lone bull near electric fence, dispersed after noise deterrent", "verified": True},
]


def get_reports_by_zone(zone_id):
    return [r for r in officer_reports if r.get("zone_id") == zone_id]


def get_latest_report(zone_id):
    return max(get_reports_by_zone(zone_id),
               key=lambda r: (r.get("date", ""), r.get("time", "")), default=None)


def has_verified_override(zone_id, date):
    return any(r.get("zone_id") == zone_id and r.get("date") == date and r.get("verified")
               for r in officer_reports)
