from contextlib import asynccontextmanager
import joblib, pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_VERSION = "v1.4.0"

class TelemetryRequest(BaseModel):
    device_id: str = Field(..., pattern=r"^DEV_\d{4}$")
    temperature: float = Field(..., ge=-40.0, le=180.0)
    vibration: float = Field(..., ge=0.0)
    pressure: float = Field(..., ge=0.5, le=30.0)
    operating_mode: str = Field(..., pattern="^(ECO|NORMAL|TURBO)$")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Загрузка моделей при старте
    app.state.preprocessor = joblib.load("artifacts/preprocessor.joblib")
    app.state.model = joblib.load("models/model.joblib")
    yield

app = FastAPI(title="Pump Inference Service", version=MODEL_VERSION, lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "model_version": MODEL_VERSION}

@app.post("/predict")
def predict(req: TelemetryRequest):
    try:
        df = pd.DataFrame([req.model_dump()])
        X = app.state.preprocessor.transform(df)
        prob = float(app.state.model.predict_proba(X)[0, 1])
        return {
            "device_id": req.device_id,
            "failure_probability": round(prob, 4),
            "decision": "high_risk" if prob >= 0.70 else "normal",
            "model_version": MODEL_VERSION
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка инференса: {str(exc)}") from exc