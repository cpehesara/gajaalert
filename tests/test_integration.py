from backend.app import app


def test_api_endpoints_integrate():
    client = app.test_client()
    response = client.post("/api/fuzzy-risk", json={"zone_id": "Z07"})
    assert response.status_code == 200
    assert response.get_json()["risk_level"] in {"Low", "Medium", "High"}
    assert client.get("/api/zones").status_code == 200