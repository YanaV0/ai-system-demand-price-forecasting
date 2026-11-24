from datetime import date as Date
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
    sku_id: str
    forecast_demand: float
    model_version: str