import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path

# Создаем папки, если их нет
Path("artifacts").mkdir(exist_ok=True)
Path("models").mkdir(exist_ok=True)

print("Загружаем данные...")
try:
    df = pd.read_csv("data/raw/telemetry.csv")
except FileNotFoundError:
    print("ОШИБКА: Файл data/raw/telemetry.csv не найден! Скопируйте его туда.")
    exit()

# Простая очистка (удаляем дубликаты)
df = df.drop_duplicates()

num = ["temperature", "vibration", "pressure"]
cat = ["operating_mode"]
X = df[num + cat]
y = df["is_failure"]

print("Обучаем препроцессор...")
preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ]), num),
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat)
])

# Обучаем препроцессор на всех данных
X_processed = preprocessor.fit_transform(X)

print("Обучаем модель...")
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_processed, y)

print("Сохраняем артефакты...")
joblib.dump(preprocessor, "artifacts/preprocessor.joblib")
joblib.dump(model, "models/model.joblib")

print("УСПЕХ! Файлы preprocessor.joblib и model.joblib созданы.")