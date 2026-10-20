"""
Инференс модели.
"""
import numpy as np
from sklearn.linear_model import LinearRegression

class ModelUnavailable(Exception):
    pass

class ModelPredictor:
    def __init__(self):
        self.model_version = "linear-baseline-v1.0"
        self.model = None
        self._is_loaded = False
    def load(self):
        try:
            self.model = LinearRegression()
            X_train = np.array([[7.0,  100.0, 10.0, 0.0], [14.0, 200.0, 20.0, 0.0], [30.0, 300.0, 30.0, 1.0], [7.0,  100.0, 50.0, 1.0]])
            y_train = np.array([10.0, 20.0, 35.0, 55.0])
            self.model.fit(X_train, y_train)
            self._is_loaded = True
        except Exception as e:
            self._is_loaded = False
            raise ModelUnavailable(f"Failed to load model: {e}") from e
    def predict_demand(self, features: np.ndarray) -> float:
        if not self._is_loaded or self.model is None:
            raise ModelUnavailable("Model is not loaded")
        try:
            prediction = self.model.predict([features])
            return float(prediction[0])
        except Exception as e:
            raise ModelUnavailable(f"Prediction failed: {e}") from e