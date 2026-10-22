"""
Контракты входных и выходных данных для компонента app.services.forecast.
ForecastRequest — что компонент принимает.
ForecastResult  — что компонент возвращает.
"""

from pydantic import BaseModel, Field, field_validator

class ForecastRequest(BaseModel):
    """Входной контракт: запрос на прогноз спроса и цены по одному SKU."""

    sku_id: str = Field(min_length=1, max_length=50, description="Идентификатор товара (SKU)")

    horizon_days: int = Field(ge=7, le=30, description="Горизонт прогноза в днях")

    current_price: float = Field(gt=0, le=1_000_000, description="Текущая цена товара, руб.")

    history: list[float] = Field(description="Продажи за последние дни, шт. (минимум 14 значений)")

    promo: bool = Field(description="Признак действия акции")

    @field_validator("history")
    @classmethod
    def check_history(cls, value: list[float]) -> list[float]:
        """Проверяет длину истории и неотрицательность значений."""
        if len(value) < 14:
            raise ValueError(f"история должна содержать как минимум 14 значений, получено {len(value)}")
        for i, v in enumerate(value):
            if v < 0:
                raise ValueError(f"history[{i}] must be >= 0, got {v}")
        return value


class ForecastResult(BaseModel):
    """Выходной контракт: результат прогноза."""

    forecast_demand: float | None = Field(description="Прогноз спроса, шт. None — если модель не вызывалась")

    recommended_price: float | None = Field(description="Рекомендованная цена, руб. None — если модель не вызывалась")

    model_version: str = Field(description="Версия использованной модели или алгоритма")

    stale: bool = Field(description="True — если использован fallback (наивный прогноз)")

    needs_human_review: bool = Field(description="True — если требуется проверка человеком")

    review_reason: str | None = Field(default=None, description="Причина, по которой требуется проверка человеком")