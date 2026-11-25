import pytest
from fastapi.testclient import TestClient

from src.api import app
from tests.test_api import PAYLOAD


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

def test_fallback_when_model_missing(client):
    original = app.state.model
    app.state.model = None
    try:
        res = client.post("/predict", json=PAYLOAD)
        assert res.status_code == 200
        assert res.json()["source"] == "fallback_rule"
        assert res.json()["forecast_demand"] == PAYLOAD["roll_mean_7"]
    finally:
        app.state.model = original

def test_fallback_when_model_raises(client):
    class Broken:
        def predict(self, X):
            raise RuntimeError("boom")

    original = app.state.model
    app.state.model = Broken()
    try:
        res = client.post("/predict", json=PAYLOAD)
        assert res.status_code == 200
        assert res.json()["source"] == "fallback_rule"
    finally:
        app.state.model = original