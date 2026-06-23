"""Base strategy class for trading strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class TradeSignal:
    timestamp: pd.Timestamp
    side: str  # "long", "short", "close"
    size: float  # 0.0 to 1.0 (fraction of capital)
    confidence: float
    metadata: dict[str, Any] | None = None


class BaseStrategy(ABC):
    """Abstract base for all trading strategies."""

    def __init__(self, name: str, lookback: int = 100):
        self.name = name
        self.lookback = lookback

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> list[TradeSignal]:
        """Generate trading signals from OHLCV data."""
        ...

    def validate_data(self, data: pd.DataFrame) -> bool:
        required = {"open", "high", "low", "close", "volume"}
        return required.issubset(set(data.columns)) and len(data) >= self.lookback

    @staticmethod
    def calculate_returns(data: pd.DataFrame) -> pd.Series:
        return data["close"].pct_change()

    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 20) -> pd.Series:
        return returns.rolling(window).std() * np.sqrt(365)
