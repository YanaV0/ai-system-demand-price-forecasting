import json, joblib, yaml
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
 
params = yaml.safe_load(open("params.yaml"))["train"]
train = pd.read_parquet("data/processed/train.parquet")
test = pd.read_parquet("data/processed/test.parquet")
X_tr, y_tr = train.drop(columns="units_sold"), train["units_sold"]
X_te, y_te = test.drop(columns="units_sold"), test["units_sold"]
 
model = RandomForestRegressor(**params, n_jobs=-1).fit(X_tr, y_tr)
pred = model.predict(X_te)
 
wape = float(np.abs(y_te - pred).sum() / y_te.sum())
rmse = float(np.sqrt(np.mean((y_te - pred) ** 2)))
mask = y_te > 0
mape = float(np.mean(np.abs((y_te[mask] - pred[mask]) / y_te[mask])))
 
Path("models").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)
joblib.dump(model, "models/model.joblib")
Path("reports/metrics.json").write_text(json.dumps({"wape": wape, "mape": mape, "rmse": rmse}, indent=2))
print("WAPE:", round(wape, 3), "MAPE:", round(mape, 3), "RMSE:", round(rmse, 3))