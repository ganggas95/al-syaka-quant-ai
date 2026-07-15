"""Base Model — Abstract interface for all ML models."""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import pandas as pd
import numpy as np
import json


class BaseModel(ABC):
    """Abstract base class for all prediction models."""

    def __init__(self, name: str = "base"):
        self.name = name
        self.model = None
        self.is_trained = False
        self.feature_importance_: Optional[pd.Series] = None
        self.metrics: dict = {}

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val=None, y_val=None):
        """Train the model."""
        ...

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict probabilities or classes."""
        ...

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predict class probabilities. Override if model supports it."""
        return self.predict(X)

    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
        """Evaluate model performance."""
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

        y_pred = self.predict(X_test)
        y_proba = self.predict_proba(X_test)

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, average="weighted", zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, average="weighted", zero_division=0)),
            "f1": float(f1_score(y_test, y_pred, average="weighted", zero_division=0)),
        }

        # ROC AUC only for binary
        if len(np.unique(y_test)) == 2 and y_proba.ndim >= 2 and y_proba.shape[1] >= 2:
            try:
                metrics["roc_auc"] = float(roc_auc_score(y_test, y_proba[:, 1]))
            except Exception:
                pass

        self.metrics = metrics
        return metrics

    def save(self, path: str):
        """Save model to disk. Override for framework-specific saving."""
        import joblib
        joblib.dump(self.model, path)

    def load(self, path: str):
        """Load model from disk."""
        import joblib
        self.model = joblib.load(path)
        self.is_trained = True
