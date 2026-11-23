import requests

def test_container_health():
    res = requests.get("http://localhost:8000/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert res.json()["model_version"] == "v1.4.0"

def test_container_predict():
    payload = {
        "device_id": "DEV_0042",
        "temperature": 75.0,
        "vibration": 3.2,
        "pressure": 15.0,
        "operating_mode": "NORMAL"
    }
    res = requests.post("http://localhost:8000/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert 0.0 <= data["failure_probability"] <= 1.0
    assert data["decision"] in ["normal", "high_risk"]