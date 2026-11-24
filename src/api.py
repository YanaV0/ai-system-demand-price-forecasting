import logging
from contextlib import asynccontextmanager
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from src.schemas import ForecastRequest, ForecastResponse
 
MODEL_VERSION = "v1.0.0"
logger = logging.getLogger("forecast_api")
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.preprocessor = joblib.load("artifacts/preprocessor.joblib")
    app.state.model = joblib.load("models/model.joblib")
    yield
 
app = FastAPI(title="Demand Forecast Service", version=MODEL_VERSION, lifespan=lifespan)
 
@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}
 
@app.post("/predict", response_model=ForecastResponse)
def predict(req: ForecastRequest):
    try:
        df = pd.DataFrame([{
            "sku_id": req.sku_id,
            "price": req.price,
            "promo": int(req.promo),
            "stock_qty": req.stock_qty,
            "lag_7": req.lag_7,
            "roll_mean_7": req.roll_mean_7,
            "day_of_week": req.date.weekday(),
            "month": req.date.month,
        }])
        X = app.state.preprocessor.transform(df)
        demand = max(0.0, float(app.state.model.predict(X)[0]))
        return ForecastResponse(sku_id=req.sku_id, forecast_demand=round(demand, 2),
                                model_version=MODEL_VERSION)
    except Exception as exc:
        logger.exception("Ошибка инференса")
        raise HTTPException(status_code=500, detail="Ошибка инференса") from exc