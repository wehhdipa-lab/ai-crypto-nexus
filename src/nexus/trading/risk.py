"""Risk management — Kelly criterion, VaR, position sizing."""

from __future__ import annotations

import numpy as np


class RiskManager:
    """Quantitative risk management toolkit."""

    @staticmethod
    def kelly_fraction(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Kelly criterion for optimal bet sizing."""
        if avg_loss == 0:
            return 0.0
        b = avg_win / abs(avg_loss)
        f = (win_rate * b - (1 - win_rate)) / b
        return max(0, min(f, 0.25))  # Cap at 25%

    @staticmethod
    def value_at_risk(returns: np.ndarray, confidence: float = 0.95, horizon: int = 1) -> float:
        """Historical VaR at given confidence level."""
        sorted_returns = np.sort(returns)
        index = int((1 - confidence) * len(sorted_returns))
        var = sorted_returns[index]
        return float(var * np.sqrt(horizon))

    @staticmethod
    def position_size(
        account_value: float,
        risk_per_trade: float,
        entry_price: float,
        stop_price: float,
    ) -> float:
        """Calculate position size based on risk budget."""
        risk_amount = account_value * risk_per_trade
        stop_distance = abs(entry_price - stop_price) / entry_price
        if stop_distance == 0:
            return 0.0
        return risk_amount / stop_distance

    @staticmethod
    def max_drawdown(equity_curve: np.ndarray) -> float:
        """Calculate maximum drawdown from equity curve."""
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - peak) / peak
        return float(np.min(drawdown))

    @staticmethod
    def correlation_matrix(returns: dict[str, np.ndarray]) -> dict[str, dict[str, float]]:
        """Calculate correlation matrix between asset returns."""
        names = list(returns.keys())
        n = len(names)
        matrix = {}
        for i in range(n):
            matrix[names[i]] = {}
            for j in range(n):
                if len(returns[names[i]]) == len(returns[names[j]]):
                    corr = np.corrcoef(returns[names[i]], returns[names[j]])[0, 1]
                    matrix[names[i]][names[j]] = round(float(corr), 4)
                else:
                    matrix[names[i]][names[j]] = 0.0
        return matrix
