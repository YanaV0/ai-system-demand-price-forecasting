import pytest
from unittest.mock import patch
from pydantic import ValidationError

from app.schemas import ForecastRequest
from app.service import process_request
from app.inference import ModelUnavailable # <-- Добавили импорт для правильной ошибки

# 1. Корректный запрос
def test_valid_request_returns_result():
    request = ForecastRequest(
        sku_id="SKU-123", horizon_days=14, current_price=1500.0,
        history=[100, 105, 98, 110, 120, 115, 130, 125, 140, 135, 150, 145, 160, 155], 
        promo=False
    )
    result = process_request(request)
    
    assert result.needs_human_review is False
    assert result.stale is False
    assert result.forecast_demand is not None
    assert result.model_version == "linear-baseline-v1.0"

# 2. Второй вход (Проверка ошибки при короткой истории)
def test_short_history_raises_validation_error():
    with pytest.raises(ValidationError):
        ForecastRequest(
            sku_id="SKU-456", horizon_days=7, current_price=500.0,
            history=[10, 12, 11], # Меньше 14 дней
            promo=False
        )

# 3. Неверный ввод (Отрицательная цена)
def test_invalid_price_raises_error():
    with pytest.raises(ValidationError):
        ForecastRequest(
            sku_id="SKU-789", horizon_days=10, current_price=-100.0, 
            history=[1,2,3,4,5,6,7,8,9,10,11,12,13,14], 
            promo=False
        )

# 4. Сбой модели -> Fallback
def test_model_failure_triggers_fallback():
    request = ForecastRequest(
        sku_id="SKU-999", horizon_days=30, current_price=1000.0,
        history=[50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115], 
        promo=False
    )
    
    # Имитируем ситуацию, когда модель НЕ МОЖЕТ загрузиться (используем ModelUnavailable)
    with patch('app.service.ModelPredictor.load', side_effect=ModelUnavailable("Model crash")):
        result = process_request(request)
        
        # Проверяем, что сработал fallback
        assert result.stale is True
        assert result.needs_human_review is True
        assert result.forecast_demand is not None
        assert "Модель недоступна" in result.review_reason