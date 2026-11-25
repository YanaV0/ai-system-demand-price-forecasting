import json
from pathlib import Path

import joblib
import mlflow
import pandas as pd
import yaml
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from contracts import RawSalesSchema

RAW = Path("data/raw/sales.csv")
OUT = Path("data/processed")
ART = Path("artifacts")
OUT.mkdir(parents=True, exist_ok=True)
ART.mkdir(parents=True, exist_ok=True)
 
NUM = ["price", "stock_qty", "lag_7", "roll_mean_7"]
PASS = ["promo", "day_of_week", "month"]
CAT = ["sku_id"]
 
def main():
    with open("params.yaml", "r") as f:
        params = yaml.safe_load(f)["prepare"]
    raw = pd.read_csv(RAW, parse_dates=["date"])
    clean = RawSalesSchema.validate(raw).drop_duplicates().copy()
    clean = clean.sort_values(["sku_id", "date"])
 
    # Признаки только из прошлого (без утечки будущего)
    g = clean.groupby("sku_id")["units_sold"]
    clean["lag_7"] = g.shift(7)
    clean["roll_mean_7"] = g.transform(lambda s: s.shift(1).rolling(7).mean())
    clean["day_of_week"] = clean["date"].dt.dayofweek
    clean["month"] = clean["date"].dt.month
    clean = clean.dropna(subset=["lag_7", "roll_mean_7"]).sort_values("date")
 
    split_at = int(len(clean) * params["train_share"])
    train_df, test_df = clean.iloc[:split_at], clean.iloc[split_at:]
 
    preprocessor = ColumnTransformer([
        ("num", Pipeline([("imputer", SimpleImputer(strategy="median")),
                          ("scaler", StandardScaler())]), NUM),
        ("pass", "passthrough", PASS),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CAT),
    ])
    cols = NUM + PASS + CAT
    x_train = preprocessor.fit_transform(train_df[cols])   # fit только на train
    x_test = preprocessor.transform(test_df[cols])
    names = preprocessor.get_feature_names_out()
 
    train_out = pd.DataFrame(x_train, columns=names)
    test_out = pd.DataFrame(x_test, columns=names)
    train_out["units_sold"] = train_df["units_sold"].to_numpy()
    test_out["units_sold"] = test_df["units_sold"].to_numpy()
    train_out.to_parquet(OUT / "train.parquet", index=False)
    test_out.to_parquet(OUT / "test.parquet", index=False)
    joblib.dump(preprocessor, ART / "preprocessor.joblib")
 
    report = {"raw_rows": len(raw), "clean_rows": len(clean),
              "train_rows": len(train_out), "test_rows": len(test_out),
              "dropped_rows": len(raw) - len(clean)}
    (OUT / "validation_report.json").write_text(json.dumps(report, indent=2))
 
    mlflow.set_experiment("lab4-data-pipeline")
    with mlflow.start_run():
        mlflow.log_params({"split_strategy": "time_ordered", **params})
        mlflow.log_metrics(report)
        mlflow.log_artifact(str(OUT / "validation_report.json"))
        mlflow.log_artifact(str(ART / "preprocessor.joblib"))
 
if __name__ == "__main__":
    main()