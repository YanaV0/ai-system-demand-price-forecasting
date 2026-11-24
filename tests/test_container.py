import requests
 
BASE = "http://localhost:8000"
PAYLOAD = {"sku_id": "SKU_0001", "date": "2025-03-15", "price": 799.0,
           "promo": False, "stock_qty": 120, "lag_7": 40, "roll_mean_7": 38.5}
 
def test_container_health():
    res = requests.get(f"{BASE}/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["model_version"] == "v1.0.0"
 
def test_container_predict():
    res = requests.post(f"{BASE}/predict", json=PAYLOAD)
    assert res.status_code == 200
    data = res.json()
    assert data["forecast_demand"] >= 0
    assert data["model_version"] == "v1.0.0"
 
def test_container_validation_error():
    res = requests.post(f"{BASE}/predict", json={**PAYLOAD, "price": -5})
    assert res.status_code == 422