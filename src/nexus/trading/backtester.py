"""Full backtesting engine with realistic simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from nexus.trading.strategies.base import BaseStrategy, TradeSignal


@dataclass
class BacktestConfig:
    initial_capital: float = 100_000.0
    slippage_bps: int = 30  # 0.3%
    gas_per_trade: float = 5.0  # USD
    maker_fee_bps: int = 10  # 0.1%
    taker_fee_bps: int = 30  # 0.3%
    max_position_pct: float = 0.20


@dataclass
class BacktestResult:
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    avg_trade_return: float
    profit_factor: float
    equity_curve: pd.Series
    trades: list[dict[str, Any]]


class Backtester:
    """Event-driven backtesting engine with realistic cost modeling."""

    def __init__(self, config: BacktestConfig | None = None):
        self.config = config or BacktestConfig()

    def run(self, strategy: BaseStrategy, data: pd.DataFrame) -> BacktestResult:
        """Run backtest on historical data."""
        signals = strategy.generate_signals(data)

        capital = self.config.initial_capital
        position = 0.0
        entry_price = 0.0
        trades: list[dict] = []
        equity = [capital]

        for signal in signals:
            idx = data.index.get_loc(signal.timestamp) if signal.timestamp in data.index else -1
            if idx < 0:
                continue
            price = data["close"].iloc[idx]

            if signal.side == "long" and position == 0:
                # Open long
                size_usd = capital * min(signal.size, self.config.max_position_pct)
                cost = size_usd * (self.config.slippage_bps + self.config.taker_fee_bps) / 10000
                cost += self.config.gas_per_trade
                position = (size_usd - cost) / price
                entry_price = price
                capital -= size_usd

            elif signal.side == "short" and position > 0:
                # Close long
                exit_price = price * (1 - self.config.slippage_bps / 10000)
                pnl = position * (exit_price - entry_price)
                fee = position * exit_price * self.config.taker_fee_bps / 10000
                net_pnl = pnl - fee - self.config.gas_per_trade
                capital += position * exit_price - fee - self.config.gas_per_trade
                trades.append({
                    "entry": entry_price, "exit": exit_price,
                    "pnl": net_pnl, "pnl_pct": net_pnl / (position * entry_price) * 100,
                })
                position = 0.0
                entry_price = 0.0

            equity.append(capital + position * price)

        equity_series = pd.Series(equity)
        returns = equity_series.pct_change().dropna()

        wins = [t for t in trades if t["pnl"] > 0]
        gross_profit = sum(t["pnl"] for t in wins)
        gross_loss = abs(sum(t["pnl"] for t in trades if t["pnl"] <= 0))

        return BacktestResult(
            total_return=(equity[-1] / self.config.initial_capital - 1) * 100,
            sharpe_ratio=float(returns.mean() / returns.std() * np.sqrt(365)) if returns.std() > 0 else 0,
            max_drawdown=float((equity_series / equity_series.cummax() - 1).min()) * 100,
            win_rate=len(wins) / len(trades) * 100 if trades else 0,
            total_trades=len(trades),
            avg_trade_return=float(np.mean([t["pnl_pct"] for t in trades])) if trades else 0,
            profit_factor=gross_profit / gross_loss if gross_loss > 0 else float("inf"),
            equity_curve=equity_series,
            trades=trades,
        )
