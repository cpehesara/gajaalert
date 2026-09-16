officer_reports = [
    {"report_id": "OR001", "officer_id": "DWC-014", "zone_id": "Z07", "date": "2026-08-10", "time": "19:45", "report_type": "verified_sighting", "number_of_elephants": 4, "verified": True},
    {"report_id": "OR002", "officer_id": "DWC-009", "zone_id": "Z03", "date": "2026-08-11", "time": "06:20", "report_type": "patrol_survey", "number_of_elephants": 0, "verified": True},
    {"report_id": "OR003", "officer_id": "DWC-014", "zone_id": "Z09", "date": "2026-08-12", "time": "21:10", "report_type": "verified_sighting", "number_of_elephants": 1, "verified": True},
]

def get_reports_by_zone(zone_id):
    return [item for item in officer_reports if item["zone_id"] == zone_id]

def get_latest_report(zone_id):
    return max(get_reports_by_zone(zone_id), key=lambda item: (item["date"], item["time"]), default=None)