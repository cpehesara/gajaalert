# gajaalert
This project aims to design and prototype a decision support system for DWC field officers and village co-ordinators to anticipate the risk of HEC (present and future) in the monitored areas of the Galgamuwa Divisional Secretariat Division 

## Run locally

Install dependencies with `python -m pip install -r requirements.txt`, then run the API from the repository root:

```bash
python -m backend.app
```

The API is available at `http://127.0.0.1:5000`. Open `frontend/src/index.html` for the offline dashboard, or serve that directory with any static file server.

Run the test suite with:

```bash
pytest tests/ -v
```

The fuzzy API accepts either raw inputs (`sighting_freq`, `distance_km`, `time_of_day`, `seasonal_risk`) or a `zone_id` to evaluate the shared tables. Scores are clipped to the documented ranges and return `risk_score`, `risk_level`, and `contributing_factors`.
