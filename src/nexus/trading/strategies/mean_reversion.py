"""Statistical mean reversion strategy."""

from __future__ import annotations

import numpy as np
import pandas as pd

from nexus.trading.strategies.base import BaseStrategy, TradeSignal


class MeanReversionStrategy(BaseStrategy):
    """Z-score based mean reversion strategy."""

    def __init__(self, lookback: int = 50, z_entry: float = 2.0, z_exit: float = 0.5):
        super().__init__(name="mean_reversion", lookback=lookback)
        self.z_entry = z_entry
        self.z_exit = z_exit

    def generate_signals(self, data: pd.DataFrame) -> list[TradeSignal]:
        if not self.validate_data(data):
            return []

        closes = data["close"]
        ma = closes.rolling(self.lookback).mean()
        std = closes.rolling(self.lookback).std()
        z_score = (closes - ma) / std

        signals = []
        for i in range(self.lookback, len(data)):
            z = z_score.iloc[i]
            if z > self.z_entry:  # Overbought → short
                signals.append(TradeSignal(
                    timestamp=data.index[i], side="short",
                    size=min(abs(z) * 0.2, 0.1), confidence=min(abs(z) / 3, 1.0),
                    metadata={"z_score": z},
                ))
            elif z < -self.z_entry:  # Oversold → long
                signals.append(TradeSignal(
                    timestamp=data.index[i], side="long",
                    size=min(abs(z) * 0.2, 0.1), confidence=min(abs(z) / 3, 1.0),
                    metadata={"z_score": z},
                ))

        return signals
