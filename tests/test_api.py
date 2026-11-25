import json
import logging
import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.logger import JSONFormatter

PAYLOAD = {"sku_id": "SKU_0001", "date": "2025-03-15", "price": 799.0,
           "promo": False, "stock_qty": 120, "lag_7": 40, "roll_mean_7": 38.5}

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_predict_success(client):
    res = client.post("/predict", json=PAYLOAD)
    assert res.status_code == 200
    data = res.json()
    for key in ("trace_id", "model_version", "source", "forecast_demand"):
        assert key in data
    assert data["source"] in ["model", "fallback_rule"]
    assert data["forecast_demand"] >= 0

def test_trace_id_is_unique(client):
    a = client.post("/predict", json=PAYLOAD).json()["trace_id"]
    b = client.post("/predict", json=PAYLOAD).json()["trace_id"]
    assert a != b

def test_validation_error(client):
    res = client.post("/predict", json={**PAYLOAD, "price": -5})
    assert res.status_code == 422

def test_json_formatter_outputs_valid_json():
    rec = logging.LogRecord("t", logging.INFO, "", 0, "msg", (), None)
    rec.extra_data = {"trace_id": "abc"}
    parsed = json.loads(JSONFormatter().format(rec))
    assert parsed["trace_id"] == "abc" and parsed["level"] == "INFO"