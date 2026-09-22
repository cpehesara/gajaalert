from backend.app import app


def test_api_endpoints_integrate():
    client = app.test_client()
    response = client.post("/api/fuzzy-risk", json={"zone_id": "Z07"})
    assert response.status_code == 200
    assert response.get_json()["risk_level"] in {"Low", "Medium", "High"}
    assert client.get("/api/zones").status_code == 200


def test_dashboard_contract_integrates_frontend_data_sources():
    client = app.test_client()
    response = client.get("/api/dashboard")
    payload = response.get_json()
    assert response.status_code == 200
    assert {"meta", "situationSummary", "herds", "forecast", "patrolRecommendation",
            "zoneRiskRegister", "activityLog", "zones"} <= payload.keys()
    assert payload["herds"]
    assert payload["patrolRecommendation"]["route"]