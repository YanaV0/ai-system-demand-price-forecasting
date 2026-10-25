import pandera as pa
from pandera import Column, Check, DataFrameSchema

RawTelemetrySchema = DataFrameSchema({
    "device_id": Column(str, Check.str_matches(r"^DEV_\d{4}$"), nullable=False),
    "timestamp": Column(pa.DateTime, nullable=False),
    "temperature": Column(float, Check.in_range(-40.0, 180.0), nullable=True),
    "vibration": Column(float, Check.greater_than_or_equal_to(0.0), nullable=True),
    "pressure": Column(float, Check.in_range(0.5, 30.0), nullable=False),
    "operating_mode": Column(str, Check.isin(["ECO", "NORMAL", "TURBO"]), nullable=False),
    "is_failure": Column(int, Check.isin([0, 1]), nullable=False),
}, strict=True, coerce=True)