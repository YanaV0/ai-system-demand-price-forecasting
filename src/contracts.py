import pandera as pa
from pandera import Column, Check, DataFrameSchema
 
RawSalesSchema = DataFrameSchema({
    "sku_id": Column(str, Check.str_matches(r"^SKU_\d{4}$"), nullable=False),
    "date": Column(pa.DateTime, nullable=False),
    "price": Column(float, Check.gt(0), nullable=False),
    "promo": Column(int, Check.isin([0, 1]), nullable=False),
    "stock_qty": Column(float, Check.ge(0), nullable=True),
    "units_sold": Column(int, Check.ge(0), nullable=False),
}, strict=True, coerce=True)