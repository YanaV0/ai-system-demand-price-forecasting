from pathlib import Path
import json, joblib, mlflow
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from contracts import RawTelemetrySchema

RAW = Path("data/raw/telemetry.csv")
OUT = Path("data/processed")
ART = Path("artifacts")
OUT.mkdir(parents=True, exist_ok=True)
ART.mkdir(parents=True, exist_ok=True)

def main():
    raw = pd.read_csv(RAW, parse_dates=["timestamp"])
    validated = RawTelemetrySchema.validate(raw)
    clean = validated.drop_duplicates().copy()
    clean = clean.sort_values("timestamp")

    # Для временных данных: поздние наблюдения оставляем для test.
    split_at = int(len(clean) * 0.8)
    train_df, test_df = clean.iloc[:split_at].copy(), clean.iloc[split_at:].copy()

    num = ["temperature", "vibration", "pressure"]
    cat = ["operating_mode"]
    preprocessor = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ]), num),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat)
    ])

    # fit только на train: защита от Data Leakage.
    x_train = preprocessor.fit_transform(train_df[num + cat])
    x_test = preprocessor.transform(test_df[num + cat])
    names = preprocessor.get_feature_names_out()

    train_out = pd.DataFrame(x_train, columns=names)
    test_out = pd.DataFrame(x_test, columns=names)
    train_out["is_failure"] = train_df["is_failure"].to_numpy()
    test_out["is_failure"] = test_df["is_failure"].to_numpy()

    train_out.to_parquet(OUT / "train.parquet", index=False)
    test_out.to_parquet(OUT / "test.parquet", index=False)
    joblib.dump(preprocessor, ART / "preprocessor.joblib")

    report = {"raw_rows": len(raw), "clean_rows": len(clean),
              "train_rows": len(train_out), "test_rows": len(test_out),
              "dropped_rows": len(raw) - len(clean)}
    (OUT / "validation_report.json").write_text(json.dumps(report, indent=2))

    mlflow.set_experiment("lab4-data-pipeline")
    with mlflow.start_run():
        mlflow.log_params({"split_strategy": "time_ordered", "train_share": 0.8})
        mlflow.log_metrics(report)
        mlflow.log_artifact(str(OUT / "validation_report.json"))
        mlflow.log_artifact(str(ART / "preprocessor.joblib"))

if __name__ == "__main__":
    main()