"""Точка входа FastAPI-приложения (заглушка для ЛР-2)."""

from fastapi import FastAPI

app = FastAPI(title="Demand & Price Forecasting API", version="1.0.0")


@app.get("/health")
def health() -> dict:
    """Проверка состояния сервиса."""
    return {"status": "healthy", "model_loaded": False, "model_version": "0.0.0"}