movement_history = [
    {"herd_id": "H01", "timestamp": "2026-08-10 06:00", "from_zone": "Z01", "to_zone": "Z01"},
    {"herd_id": "H01", "timestamp": "2026-08-10 12:00", "from_zone": "Z01", "to_zone": "Z02"},
    {"herd_id": "H01", "timestamp": "2026-08-10 18:00", "from_zone": "Z02", "to_zone": "Z02"},
    {"herd_id": "H02", "timestamp": "2026-08-10 06:00", "from_zone": "Z03", "to_zone": "Z04"},
]
transition_matrix = [
    {"current_zone": "Z01", "P_stay": 0.55, "P_neighbour_A": 0.30, "neighbour_A": "Z02", "P_neighbour_B": 0.15, "neighbour_B": "Z05"},
    {"current_zone": "Z02", "P_stay": 0.20, "P_neighbour_A": 0.60, "neighbour_A": "Z01", "P_neighbour_B": 0.20, "neighbour_B": "Z03"},
    {"current_zone": "Z03", "P_stay": 0.10, "P_neighbour_A": 0.35, "neighbour_A": "Z04", "P_neighbour_B": 0.55, "neighbour_B": "Z02"},
]