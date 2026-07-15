"""XGBoost Model — Training, hyperparameter tuning, inference."""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
import xgboost as xgb
from sklearn.model_selection import ParameterGrid

from .base import BaseModel


class XGBoostModel(BaseModel):
    """XGBoost classifier for market direction prediction."""

    def __init__(
        self,
        name: str = "xgboost",
        params: Optional[dict] = None,
    ):
        super().__init__(name)
        self.params = params or {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 3,
            "gamma": 0.1,
            "reg_alpha": 0.1,
            "reg_lambda": 1,
            "random_state": 42,
            "eval_metric": "logloss",
            "use_label_encoder": False,
        }
        self.best_params = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val=None, y_val=None):
        """Train XGBoost model."""
        eval_set = [(X_train, y_train)]
        if X_val is not None and y_val is not None:
            eval_set.append((X_val, y_val))

        self.model = xgb.XGBClassifier(**self.params)
        self.model.fit(
            X_train, y_train,
            eval_set=eval_set,
            verbose=False,
        )
        self.is_trained = True
        self._extract_importance(X_train)

    def tune(self, X_train: pd.DataFrame, y_train: pd.Series, X_val, y_val):
        """Hyperparameter tuning with grid search."""
        param_grid = {
            "max_depth": [4, 6, 8],
            "learning_rate": [0.01, 0.05, 0.1],
            "n_estimators": [100, 200],
            "subsample": [0.7, 0.8, 1.0],
        }

        best_score = 0
        for params in ParameterGrid(param_grid):
            p = self.params.copy()
            p.update(params)
            model = xgb.XGBClassifier(**p, eval_metric="logloss", use_label_encoder=False)
            model.fit(X_train, y_train, verbose=False)
            score = model.score(X_val, y_val)
            if score > best_score:
                best_score = score
                self.best_params = params
                self.params.update(params)

        # Retrain with best params
        self.train(X_train, y_train, X_val, y_val)

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
