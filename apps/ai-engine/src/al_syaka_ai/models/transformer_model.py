"""Transformer Model — Time series transformer for market prediction."""

import pandas as pd
import numpy as np
from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from .base import BaseModel


class TimeSeriesTransformer(nn.Module):
    """Simple Transformer for time series classification."""

    def __init__(
        self,
        input_dim: int,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 3,
        dim_feedforward: int = 128,
        dropout: float = 0.1,
        num_classes: int = 2,
        seq_len: int = 20,
    ):
        super().__init__()
        self.seq_len = seq_len
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoder = nn.Parameter(torch.randn(1, seq_len, d_model) * 0.1)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.fc = nn.Linear(d_model, num_classes)

    def forward(self, x):
        # x: (batch, seq_len, features)
        x = self.input_projection(x) + self.pos_encoder[:, :x.size(1), :]
        x = self.transformer(x)
        x = x.mean(dim=1)  # Global average pooling
        return self.fc(x)


class TransformerModel(BaseModel):
    """Transformer-based model for time series market prediction."""

    def __init__(
        self,
        name: str = "transformer",
        seq_len: int = 20,
        d_model: int = 64,
        nhead: int = 4,
        num_layers: int = 3,
        learning_rate: float = 0.001,
        epochs: int = 50,
        batch_size: int = 32,
        device: str = "cpu",
    ):
        super().__init__(name)
        self.seq_len = seq_len
        self.d_model = d_model
        self.nhead = nhead
        self.num_layers = num_layers
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = torch.device(device if torch.cuda.is_available() else "cpu")
        self.input_dim = None

    def train(self, X_train: pd.DataFrame, y_train: pd.Series, X_val=None, y_val=None):
        """Train Transformer model."""
        self.input_dim = X_train.shape[1]
        num_classes = len(np.unique(y_train))

        self.model = TimeSeriesTransformer(
            input_dim=self.input_dim,
            d_model=self.d_model,
            nhead=min(self.nhead, self.d_model // 8),
            num_layers=self.num_layers,
            num_classes=num_classes,
            seq_len=self.seq_len,
        ).to(self.device)

        # Prepare sequences
        X_seq, y_seq = self._create_sequences(X_train.values, y_train.values)

        dataset = TensorDataset(
            torch.FloatTensor(X_seq).to(self.device),
            torch.LongTensor(y_seq).to(self.device),
        )
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)

        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)

        # Training loop
        self.model.train()
        for epoch in range(self.epochs):
            total_loss = 0
            for batch_X, batch_y in loader:
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{self.epochs}, Loss: {total_loss/len(loader):.4f}")

        self.is_trained = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        self.model.eval()
        X_seq, _ = self._create_sequences(X.values, np.zeros(len(X)))
        with torch.no_grad():
            tensor_X = torch.FloatTensor(X_seq).to(self.device)
            outputs = self.model(tensor_X)
            predictions = torch.argmax(outputs, dim=1).cpu().numpy()
        return predictions

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        self.model.eval()
        X_seq, _ = self._create_sequences(X.values, np.zeros(len(X)))
        with torch.no_grad():
            tensor_X = torch.FloatTensor(X_seq).to(self.device)
            outputs = torch.softmax(self.model(tensor_X), dim=1)
        return outputs.cpu().numpy()

    def _create_sequences(self, X: np.ndarray, y: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sliding window sequences."""
        X_seq, y_seq = [], []
        for i in range(len(X) - self.seq_len):
            X_seq.append(X[i:i + self.seq_len])
            y_seq.append(y[i + self.seq_len])
        return np.array(X_seq), np.array(y_seq)
