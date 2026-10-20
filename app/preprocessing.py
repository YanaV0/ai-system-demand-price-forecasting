"""
Подготовка признаков для модели.
"""
import numpy as np
from app.schemas import ForecastRequest

def prepare_features(request: ForecastRequest) -> np.ndarray:
    mean_history = sum(request.history) / len(request.history)
    promo_flag = 1.0 if request.promo else 0.0
    features = np.array([float(request.horizon_days), float(request.current_price), float(mean_history), promo_flag], dtype=np.float32)
    return features