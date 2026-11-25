from pathlib import Path

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
dates = pd.date_range("2024-01-01", periods=365, freq="D")
rows = []
for i in range(1, 11):
    sku = f"SKU_{i:04d}"
    base = rng.uniform(20, 80)
    price0 = rng.uniform(300, 1500)
    for d in dates:
        promo = int(rng.random() < 0.1)
        price = round(price0 * (0.85 if promo else 1) * rng.uniform(0.97, 1.03), 2)
        season = 1 + 0.3 * np.sin(2 * np.pi * d.dayofyear / 365)
        weekend = 1.2 if d.dayofweek >= 5 else 1.0
        lam = base * season * weekend * (1.5 if promo else 1) * (price0 / price) ** 0.8
        stock = float(rng.integers(0, 500)) if rng.random() > 0.01 else np.nan
        rows.append((sku, d, price, promo, stock, int(rng.poisson(lam))))
 
df = pd.DataFrame(rows, columns=["sku_id", "date", "price", "promo", "stock_qty", "units_sold"])
Path("data/raw").mkdir(parents=True, exist_ok=True)
df.to_csv("data/raw/sales.csv", index=False)
print(len(df), "строк")