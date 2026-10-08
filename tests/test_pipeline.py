import backend.app as app_module
from backend.app import app


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "REPORTS_FILE", tmp_path / "officer_reports.json")
    return app.test_client()


def test_register_rows_carry_rule_flags_and_forecast_pressure(tmp_path, monkeypatch):
    rows = _client(tmp_path, monkeypatch).get("/api/dashboard").get_json()["zoneRiskRegister"]
    assert len(rows) == 10
    assert all(row["triggeredRules"] != "—" for row in rows)
    assert any(row["forecastPressure"] > 0 for row in rows)


def test_cycle_advance_moves_herds(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    first = client.get("/api/dashboard").get_json()
    for _ in range(8):
        client.post("/api/cycle/advance")
    later = client.get("/api/dashboard").get_json()
    assert later["meta"]["cycle"] == first["meta"]["cycle"] + 8
    assert [h["zoneId"] for h in first["herds"]] != [h["zoneId"] for h in later["herds"]]


def test_officer_update_overrides_simulated_position(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    herd = client.get("/api/dashboard").get_json()["herds"][0]
    target = "Z08" if herd["zoneId"] != "Z08" else "Z06"
    response = client.post("/api/officer-update",
                           json={"herdId": herd["id"], "zoneId": target, "observedSize": "7"})
    assert response.status_code == 201
    updated = next(h for h in client.get("/api/dashboard").get_json()["herds"] if h["id"] == herd["id"])
    assert updated["zoneId"] == target and updated["size"] == 7
    assert updated["source"] == "officer-verified"
    assert (tmp_path / "officer_reports.json").exists()


def test_officer_update_rejects_bad_input(tmp_path, monkeypatch):
    client = _client(tmp_path, monkeypatch)
    assert client.post("/api/officer-update", json={"zoneId": "Z99", "observedSize": 2}).status_code == 400
    assert client.post("/api/officer-update", json={"zoneId": "Z01", "observedSize": "x"}).status_code == 400
    assert client.post("/api/officer-update", json={"herdId": "H99", "zoneId": "Z01", "observedSize": 2}).status_code == 400


def test_patrol_route_reaches_every_zone():
    client = app.test_client()
    plan = client.post("/api/patrol-route",
                       json={"start_zone": "Z01", "priority_zones": ["Z06", "Z08", "Z09"]}).get_json()
    assert plan["unreached_zones"] == []