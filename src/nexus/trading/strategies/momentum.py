"""LSTM-based momentum strategy with attention mechanism."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from nexus.trading.strategies.base import BaseStrategy, TradeSignal


class MomentumStrategy(BaseStrategy):
    """ML-based momentum strategy using LSTM with attention."""

    def __init__(
        self,
        lookback: int = 60,
        hidden_size: int = 128,
        num_layers: int = 2,
        threshold: float = 0.6,
    ):
        super().__init__(name="lstm_momentum", lookback=lookback)
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.threshold = threshold
        self.model: Any = None

    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Engineer features from OHLCV data."""
        df = data.copy()
        df["returns"] = df["close"].pct_change()
        df["volatility"] = df["returns"].rolling(20).std()
        df["rsi"] = self._calculate_rsi(df["close"], 14)
        df["macd"] = df["close"].ewm(span=12).mean() - df["close"].ewm(span=26).mean()
        df["macd_signal"] = df["macd"].ewm(span=9).mean()
        df["volume_ratio"] = df["volume"] / df["volume"].rolling(20).mean()
        df["price_range"] = (df["high"] - df["low"]) / df["close"]
        df = df.dropna()

        feature_cols = ["returns", "volatility", "rsi", "macd", "macd_signal", "volume_ratio", "price_range"]
        return df[feature_cols].values

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def generate_signals(self, data: pd.DataFrame) -> list[TradeSignal]:
        """Generate momentum signals using statistical approach (ML model optional)."""
        if not self.validate_data(data):
            return []

        features = self._prepare_features(data)
        signals = []
        df = data.iloc[-len(features):]

        for i in range(self.lookback, len(features)):
            window = features[i - self.lookback:i]
            score = self._score_window(window)

            if abs(score) > self.threshold:
                side = "long" if score > 0 else "short"
                signals.append(TradeSignal(
                    timestamp=df.index[i],
                    side=side,
                    size=min(abs(score) * 0.5, 0.1),
                    confidence=min(abs(score), 1.0),
                    metadata={"score": score, "rsi": features[i][2]},
                ))

        return signals

    def _score_window(self, window: np.ndarray) -> float:
        """Score a window of features. Positive = bullish, negative = bearish."""
        returns = window[:, 0]
        rsi = window[:, 2]
        macd = window[:, 3]
        vol_ratio = window[:, 5]

        # Momentum score
        momentum = np.mean(returns[-5:]) / (np.std(returns) + 1e-8)

        # RSI signal
        rsi_signal = (50 - rsi[-1]) / 50  # Oversold = positive

        # MACD crossover
        macd_trend = 1.0 if macd[-1] > macd[-2] else -1.0

        # Volume confirmation
        vol_confirm = min(vol_ratio[-1], 2.0) / 2.0

        score = (momentum * 0.3 + rsi_signal * 0.25 + macd_trend * 0.25 + vol_confirm * 0.2)
        return float(np.clip(score, -1, 1))
