from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass
class DomainModel:
    name: str
    regressor: LinearRegression
    feature_names: list[str]

    def predict(self, features: dict[str, float]) -> tuple[float, dict[str, float]]:
        x = np.array([[features.get(n, 0.0) for n in self.feature_names]])
        y = float(self.regressor.predict(x)[0])
        importances = {
            self.feature_names[i]: float(abs(self.regressor.coef_[i]))
            for i in range(len(self.feature_names))
        }
        return y, importances

