from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    sku_id: str = Field(..., pattern=r"^SKU_\d{4}$", description="Идентификатор товара")
    date: Date = Field(..., description="Дата, на которую считается прогноз")
    price: float = Field(..., gt=0, le=1_000_000, description="Цена, руб.")
    promo: bool = Field(..., description="Участвует ли товар в акции")
    stock_qty: float = Field(..., ge=0, description="Остаток на складе, шт.")
    lag_7: float = Field(..., ge=0, description="Продажи 7 дней назад, шт.")
    roll_mean_7: float = Field(..., ge=0, description="Среднее продаж за последние 7 дней, шт.")
 
class ForecastResponse(BaseModel):
    trace_id: str = Field(description="Сквозной идентификатор запроса (UUID4)")
    sku_id: str = Field(description="Идентификатор товара")
    forecast_demand: float = Field(description="Прогноз спроса, шт.")
    model_version: str = Field(description="Версия модели")
    source: Literal["model", "fallback_rule"] = Field(
        description="Источник прогноза: модель или резервное правило")
    latency_ms: float = Field(description="Время обработки запроса, мс")