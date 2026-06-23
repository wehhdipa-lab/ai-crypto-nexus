"""Impermanent Loss calculator."""
import math
class ILCalculator:
    @staticmethod
    def calculate(price_ratio: float) -> float:
        if price_ratio <= 0: return 0.0
        return abs(2 * math.sqrt(price_ratio) / (1 + price_ratio) - 1)
    @staticmethod
    def breakeven(price_ratio: float, fee_apr: float = 0.0, days: int = 30) -> dict:
        il = ILCalculator.calculate(price_ratio)
        fees = fee_apr * days / 365
        hold = price_ratio - 1
        lp = (1 + hold) * (1 - il) + fees - 1
        return {"il_pct": il*100, "fees_pct": fees*100, "hold_pct": hold*100, "lp_pct": lp*100, "lp_better": lp > hold}
