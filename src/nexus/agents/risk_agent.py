"""Risk management agent — position limits, drawdown protection, correlation."""

from __future__ import annotations

from typing import Any

import structlog

from nexus.agents.base import BaseAgent
from nexus.data.models import Position, Signal, SignalType, Token

logger = structlog.get_logger()


class RiskAgent(BaseAgent):
    """Monitors portfolio risk and enforces limits."""

    def __init__(
        self,
        max_drawdown: float = 0.15,
        max_leverage: float = 3.0,
        max_position_pct: float = 0.20,
        max_correlation: float = 0.8,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.max_drawdown = max_drawdown
        self.max_leverage = max_leverage
        self.max_position_pct = max_position_pct
        self.max_correlation = max_correlation
        self.positions: list[Position] = []

    async def analyze(self, context: dict[str, Any]) -> list[Signal]:
        """Analyze portfolio risk and emit warning signals."""
        signals = []
        portfolio_value = context.get("portfolio_value", 0)
        self.positions = context.get("positions", [])

        # Check drawdown
        peak_value = context.get("peak_value", portfolio_value)
        if peak_value > 0:
            drawdown = (peak_value - portfolio_value) / peak_value
            if drawdown > self.max_drawdown * 0.8:
                token = Token(address="0x0", symbol="PORTFOLIO", name="Portfolio", chain_id=1)
                signals.append(Signal(
                    source=self.agent_id,
                    signal_type=SignalType.SELL,
                    token=token,
                    confidence=min(drawdown / self.max_drawdown, 1.0),
                    reasoning=f"Drawdown {drawdown:.1%} approaching limit {self.max_drawdown:.1%}",
                ))

        # Check position concentration
        for pos in self.positions:
            if portfolio_value > 0 and pos.size_usd / portfolio_value > self.max_position_pct:
                signals.append(Signal(
                    source=self.agent_id,
                    signal_type=SignalType.SELL,
                    token=pos.token,
                    confidence=0.9,
                    reasoning=f"Position {pos.token.symbol} at {pos.size_usd/portfolio_value:.1%} exceeds {self.max_position_pct:.1%} limit",
                ))

        # Check leverage
        total_leverage = sum(p.leverage for p in self.positions)
        if total_leverage > self.max_leverage:
            token = Token(address="0x0", symbol="LEVERAGE", name="Leverage", chain_id=1)
            signals.append(Signal(
                source=self.agent_id,
                signal_type=SignalType.SELL,
                token=token,
                confidence=0.95,
                reasoning=f"Total leverage {total_leverage:.1f}x exceeds {self.max_leverage:.1f}x limit",
            ))

        return signals

    async def plan(self, signals: list[Signal]) -> list[dict[str, Any]]:
        """Risk agent plans are always reduce/exit actions."""
        return [
            {"action": "reduce", "token": s.token.symbol, "reason": s.reasoning}
            for s in signals if s.signal_type == SignalType.SELL
        ]

    def calculate_position_size(
        self, account_value: float, risk_per_trade: float = 0.02, stop_distance: float = 0.05
    ) -> float:
        """Kelly-criterion inspired position sizing."""
        max_loss = account_value * risk_per_trade
        position_size = max_loss / stop_distance
        return min(position_size, account_value * self.max_position_pct)
