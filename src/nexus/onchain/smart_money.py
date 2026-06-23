"""Smart money detection."""
from dataclasses import dataclass
@dataclass
class SmartMoneySignal:
    wallet: str; action: str; token: str; amount_usd: float; win_rate: float; avg_return: float
class SmartMoneyTracker:
    def __init__(self, min_win_rate: float = 0.6, min_trades: int = 50):
        self.min_win_rate = min_win_rate; self.min_trades = min_trades
    def analyze_wallet(self, wallet: str, trades: list[dict]) -> dict:
        if len(trades) < self.min_trades: return {"eligible": False}
        wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
        wr = wins / len(trades)
        avg = sum(t.get("pnl_pct", 0) for t in trades) / len(trades)
        return {"eligible": wr >= self.min_win_rate, "win_rate": wr, "avg_return": avg}
