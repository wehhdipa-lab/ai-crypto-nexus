"""NLP-based sentiment trading strategy."""

from __future__ import annotations

import re
from collections import Counter

import pandas as pd

from nexus.trading.strategies.base import BaseStrategy, TradeSignal


# Crypto-specific sentiment lexicon
BULLISH_WORDS = {
    "moon", "bullish", "pump", "breakout", "rally", "surge", "accumulate",
    "undervalued", "hodl", "buy", "long", "uptrend", "support", "bounce",
    "golden cross", "halving", "adoption", "institutional", "partnership",
}

BEARISH_WORDS = {
    "dump", "crash", "bearish", "sell", "short", "overvalued", "resistance",
    "breakdown", "capitulation", "fear", "panic", "rug", "scam", "hack",
    "exploit", "regulation", "ban", "death cross", "liquidation",
}


class SentimentStrategy(BaseStrategy):
    """Trading strategy based on NLP sentiment analysis."""

    def __init__(self, lookback: int = 24, threshold: float = 0.3):
        super().__init__(name="sentiment_nlp", lookback=lookback)
        self.threshold = threshold

    def generate_signals(self, data: pd.DataFrame) -> list[TradeSignal]:
        """Generate signals from sentiment data (expects 'sentiment' column)."""
        if "sentiment" not in data.columns:
            return []

        signals = []
        sent = data["sentiment"].rolling(self.lookback).mean()

        for i in range(self.lookback, len(data)):
            score = sent.iloc[i]
            if abs(score) > self.threshold:
                side = "long" if score > 0 else "short"
                signals.append(TradeSignal(
                    timestamp=data.index[i],
                    side=side,
                    size=min(abs(score) * 0.3, 0.08),
                    confidence=min(abs(score), 1.0),
                    metadata={"sentiment_score": score},
                ))

        return signals

    @staticmethod
    def analyze_text(text: str) -> float:
        """Score text sentiment from -1 (bearish) to +1 (bullish)."""
        words = set(re.findall(r"\w+", text.lower()))
        bull = len(words & BULLISH_WORDS)
        bear = len(words & BEARISH_WORDS)
        total = bull + bear
        if total == 0:
            return 0.0
        return (bull - bear) / total

    @staticmethod
    def batch_analyze(texts: list[str]) -> dict[str, float]:
        """Analyze multiple texts and return aggregate sentiment."""
        scores = [SentimentStrategy.analyze_text(t) for t in texts]
        return {
            "mean": sum(scores) / len(scores) if scores else 0.0,
            "positive_pct": sum(1 for s in scores if s > 0) / len(scores) if scores else 0.0,
            "negative_pct": sum(1 for s in scores if s < 0) / len(scores) if scores else 0.0,
            "count": len(scores),
        }
