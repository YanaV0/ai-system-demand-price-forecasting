# Model Card: Demand Forecast (v1.0.0)

## 1. Model Details
- Тип: RandomForestRegressor (scikit-learn), n_estimators=200, max_depth=10, random_state=42
- Версия: v1.0.0; препроцессор: ColumnTransformer (медиана + StandardScaler, OneHot для sku_id)

## 2. Intended Use
- Прогноз дневного спроса (шт.) по SKU для планирования закупок.
- Не предназначен для автоматического ценообразования и юридически значимых решений.
- Пользователи: отдел закупок, коммерческий отдел.

## 3. Factors & Data
- Данные: синтетические (src/make_dataset.py), 10 SKU, 365 дней, 3650 строк.
- Признаки: price, stock_qty, lag_7, roll_mean_7, promo, day_of_week, month, sku_id.
- Сплит: по времени, 80/20 (2864 train / 716 test), без утечки данных.

## 4. Metrics & Evaluation
| Метрика | Значение | Цель |
|---|---|---|
| WAPE | 0.146 | ≤ 0.12 |
| MAPE | 0.149 | ≤ 0.10 |
| RMSE | 10.05 | baseline |
Для регрессии спроса основной метрикой выбран WAPE (устойчив к малым значениям спроса).
Цели по MAPE и WAPE пока еще не достигнуты.

## 5. Caveats & Limitations
- Обучена на синтетических данных, на реальных результаты могут отличаться.
- Новые SKU не из обучающей выборки обрабатываются как неизвестная категория.
- lag_7 и roll_mean_7 клиент передаёт сам; ошибка в них даёт ошибочный прогноз.
- При сбое модели используется fallback: среднее за 7 дней (source="fallback_rule").