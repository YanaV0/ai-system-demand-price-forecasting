import time
import uuid
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI

from src.logger import get_json_logger
from src.schemas import ForecastRequest, ForecastResponse

MODEL_VERSION = "v1.0.0"
logger = get_json_logger("forecast_api")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.preprocessor = None
    app.state.model = None
    try:
        app.state.preprocessor = joblib.load("artifacts/preprocessor.joblib")
        app.state.model = joblib.load("models/model.joblib")
    except Exception as exc: # noqa: BLE001
        app.state.model = None
        logger.error("Ошибка загрузки артефактов",
                     extra={"extra_data": {"error": str(exc)}})
    yield

app = FastAPI(title="Demand Forecast Service", version=MODEL_VERSION, lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION,
            "model_loaded": getattr(app.state, "model", None) is not None}

@app.post("/predict", response_model=ForecastResponse)
def predict(req: ForecastRequest):
    start = time.perf_counter()
    trace_id = str(uuid.uuid4())
    source = "model"
    try:
        model = getattr(app.state, "model", None)
        prep = getattr(app.state, "preprocessor", None)
        if model is None or prep is None:
            raise RuntimeError("Модель не инициализирована")
        df = pd.DataFrame([{
            "sku_id": req.sku_id, "price": req.price, "promo": int(req.promo),
            "stock_qty": req.stock_qty, "lag_7": req.lag_7,
            "roll_mean_7": req.roll_mean_7,
            "day_of_week": req.date.weekday(), "month": req.date.month,
        }])
        demand = max(0.0, float(model.predict(prep.transform(df))[0]))
    except Exception as exc: # noqa: BLE001
        source = "fallback_rule"          # ПАТТЕРН FALLBACK
        demand = float(req.roll_mean_7)
        logger.warning("fallback", extra={"extra_data": {
            "trace_id": trace_id, "error": str(exc)}})

    latency = round((time.perf_counter() - start) * 1000, 2)
    logger.info("inference", extra={"extra_data": {
        "trace_id": trace_id, "sku_id": req.sku_id,
        "forecast_demand": round(demand, 2), "source": source,
        "model_version": MODEL_VERSION, "latency_ms": latency}})

    return ForecastResponse(trace_id=trace_id, sku_id=req.sku_id,
                            forecast_demand=round(demand, 2),
                            model_version=MODEL_VERSION, source=source,
                            latency_ms=latency)