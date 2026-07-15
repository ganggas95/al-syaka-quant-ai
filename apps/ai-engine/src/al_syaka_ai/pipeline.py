"""ML Pipeline — Automated feature engineering, labeling, train/test split."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sklearn.model_selection import TimeSeriesSplit

from al_syaka_features import FeaturePipeline
from .labeling import LabelGenerator, LabelConfig


class MLPipeline:
    """End-to-end ML pipeline: features → labels → train/test split."""

    def __init__(self, label_config: Optional[LabelConfig] = None):
        self.feature_pipeline = FeaturePipeline()
        self.label_generator = LabelGenerator(label_config or LabelConfig())
        self.features: Optional[pd.DataFrame] = None
        self.labels: Optional[pd.Series] = None

    def prepare_data(
        self,
        open: pd.Series,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: Optional[pd.Series] = None,
        timestamps: Optional[pd.Series] = None,
        generate_labels: bool = True,
    ) -> Tuple[pd.DataFrame, Optional[pd.Series]]:
        """Prepare complete dataset: features + labels."""
        # Generate features
        self.features = self.feature_pipeline.compute(
            open=open,
            high=high,
            low=low,
            close=close,
            volume=volume,
            timestamps=timestamps,
        )

        # Remove NaN rows
        self.features = self.features.replace([np.inf, -np.inf], np.nan)
        self.features = self.features.dropna()

        if generate_labels:
            self.labels = self.label_generator.generate_labels(close, high, low)
            # Align labels with features
            self.labels = self.labels.loc[self.features.index]

        return self.features, self.labels

    def train_test_split(
        self,
        test_size: float = 0.2,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Time-series aware train/test split."""
        if self.features is None or self.labels is None:
            raise ValueError("Run prepare_data() first")

        split_idx = int(len(self.features) * (1 - test_size))
        X_train = self.features.iloc[:split_idx]
        X_test = self.features.iloc[split_idx:]
        y_train = self.labels.iloc[:split_idx]
        y_test = self.labels.iloc[split_idx:]

        return X_train, X_test, y_train, y_test

    def time_series_cv(self, n_splits: int = 5) -> list:
        """Generate time series cross-validation indices."""
        if self.features is None:
            raise ValueError("Run prepare_data() first")
        tscv = TimeSeriesSplit(n_splits=n_splits)
        return list(tscv.split(self.features))

    def get_feature_columns(self) -> list:
        """Get list of feature column names."""
        if self.features is None:
            return []
        return self.features.columns.tolist()
