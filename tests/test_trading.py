"""Test trading strategies and backtester."""

import numpy as np
import pandas as pd
import pytest
from nexus.trading.strategies.momentum import MomentumStrategy
from nexus.trading.strategies.mean_reversion import MeanReversionStrategy
from nexus.trading.strategies.sentiment import SentimentStrategy


def _make_ohlcv(n: int = 200) -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=n, freq="4h")
    close = 100 + np.cumsum(np.random.randn(n) * 2)
    return pd.DataFrame({
        "open": close + np.random.randn(n) * 0.5,
        "high": close + abs(np.random.randn(n)),
        "low": close - abs(np.random.randn(n)),
        "close": close,
        "volume": np.random.randint(1000, 10000, n).astype(float),
    }, index=dates)


def test_momentum_strategy():
    data = _make_ohlcv()
    strat = MomentumStrategy(lookback=50, threshold=0.3)
    signals = strat.generate_signals(data)
    assert isinstance(signals, list)
    for s in signals:
        assert s.side in ("long", "short")
        assert 0 < s.size <= 0.1
        assert 0 < s.confidence <= 1.0


def test_mean_reversion_strategy():
    data = _make_ohlcv()
    strat = MeanReversionStrategy(lookback=30, z_entry=1.5)
    signals = strat.generate_signals(data)
    assert isinstance(signals, list)


def test_sentiment_analyzer():
    assert SentimentStrategy.analyze_text("ETH is mooning! Very bullish!") > 0
    assert SentimentStrategy.analyze_text("Market crash, bearish dump incoming") < 0
    assert SentimentStrategy.analyze_text("The weather is nice today") == 0


def test_sentiment_batch():
    texts = ["bullish pump moon", "bearish dump crash", "neutral day"]
    result = SentimentStrategy.batch_analyze(texts)
    assert result["count"] == 3
    assert -1 <= result["mean"] <= 1
