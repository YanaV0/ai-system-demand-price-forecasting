import joblib
import os
from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

# Создаем папки, если их нет
os.makedirs("models", exist_ok=True)
os.makedirs("artifacts", exist_ok=True)

# 1. Создаем фейковый препроцессор (StandardScaler)
preprocessor = StandardScaler()
dummy_X = pd.DataFrame({
    "temperature": [75.0, 90.0], 
    "vibration": [3.0, 7.0], 
    "pressure": [15.0, 20.0]
})
preprocessor.fit(dummy_X)
joblib.dump(preprocessor, "artifacts/preprocessor.joblib")

# 2. Создаем фейковую модель (DummyClassifier)
dummy_y = [0, 1]
model = DummyClassifier(strategy="stratified", random_state=42)
model.fit(dummy_X, dummy_y)
joblib.dump(model, "models/model.joblib")

print("✅ Фейковые модели успешно созданы и сохранены в models/ и artifacts/")