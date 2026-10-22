from app.schemas import ForecastRequest, ForecastResult
from app.preprocessing import prepare_features
from app.inference import ModelPredictor, ModelUnavailable

def process_request(request: ForecastRequest) -> ForecastResult:
    predictor = ModelPredictor()
    
    # 1. Пытаемся загрузить модель
    try:
        predictor.load()
    except ModelUnavailable as e:
        # ПРАВИЛО: Если модель недоступна, делаем fallback (среднее за 7 дней)
        fallback_demand = sum(request.history[-7:]) / 7
        return ForecastResult(
            forecast_demand=max(0.0, round(fallback_demand, 2)),
            recommended_price=request.current_price,
            model_version=predictor.model_version,
            stale=True, # Пометка, что это запасной вариант
            needs_human_review=True,
            review_reason=f"Модель недоступна: {e}"
        )

    # 2. Если модель загрузилась, готовим признаки
    try:
        features = prepare_features(request)
    except Exception as e:
        return ForecastResult(
            forecast_demand=None,
            recommended_price=None,
            model_version=predictor.model_version,
            stale=False,
            needs_human_review=True,
            review_reason=f"Ошибка подготовки данных: {e}"
        )

    # 3. Делаем прогноз
    try:
        prediction = predictor.predict_demand(features)
    except ModelUnavailable as e:
        # ПРАВИЛО: Сбой при инференсе
        fallback_demand = sum(request.history[-7:]) / 7
        return ForecastResult(
            forecast_demand=max(0.0, round(fallback_demand, 2)),
            recommended_price=request.current_price,
            model_version=predictor.model_version,
            stale=True,
            needs_human_review=True,
            review_reason=f"Ошибка инференса: {e}"
        )

    # 4. ПРИКЛАДНЫЕ ПРАВИЛА (после получения прогноза)
    # Правило: Спрос не может быть отрицательным
    final_demand = max(0.0, round(prediction, 2))
    
    # Правило: Рекомендованная цена (допустим, мы просто оставляем текущую)
    final_price = request.current_price
    
    # Правило: Если прогноз слишком большой, отправляем на проверку
    needs_review = False
    reason = None
    if final_demand > 1000: # Пример бизнес-правила
        needs_review = True
        reason = "Аномально высокий прогноз спроса"

    return ForecastResult(
        forecast_demand=final_demand,
        recommended_price=final_price,
        model_version=predictor.model_version,
        stale=False,
        needs_human_review=needs_review,
        review_reason=reason
    )