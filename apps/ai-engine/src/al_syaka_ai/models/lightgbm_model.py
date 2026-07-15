"""LightGBM Model — Training, comparison with XGBoost, ensemble."""

import pandas as pd
import numpy as np
from typing import Optional
import lightgbm as lgb

from .base import BaseModel


class LightGBMModel(BaseModel):
    """LightGBM classifier for market direction prediction."""

    def __init__(
        self,
        name: str = "lightgbm",
        params: Optional[dict] = None,
    ):
        super().__init__(name)
        self.params = params or {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_samples": 20,
            "reg_alpha": 0.1,
            "reg_lambda": 0.1,
            "random_state": 42,
            "verbose": -1,
        }

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val=None, y_val=None):
        """Train LightGBM model."""
        self.model = lgb.LGBMClassifier(**self.params)
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            callbacks=[lgb.early_stopping(10)] if X_val is not None else None,
        )
        self.is_trained = True
        self._extract_importance(X_train)

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        return self.model.predict_proba(X)

    def _extract_importance(self, X_train: pd.DataFrame):
        if hasattr(self.model, "feature_importances_"):
            self.feature_importance_ = pd.Series(
                self.model.feature_importances_,
                index=X_train.columns,
            ).sort_values(ascending=False)
