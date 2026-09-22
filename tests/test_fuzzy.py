from backend.fuzzy.fuzzy_engine import compute_risk_score, evaluate_zone_risk_from_tables


def test_fuzzy_returns_schema_and_native_values():
    result = compute_risk_score(8, 1, 22, 80, "Z07")
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in {"Low", "Medium", "High"}
    assert isinstance(result["risk_score"], int)


def test_fuzzy_clips_out_of_range_without_nan():
    result = compute_risk_score(-10, 99, -4, 1000)
    assert result["risk_score"] == result["risk_score"]


def test_table_evaluation_honors_verified_report():
    result = evaluate_zone_risk_from_tables("Z03")
    assert result["risk_level"] == "Low"
    assert "officer-verified clear patrol" in result["contributing_factors"]