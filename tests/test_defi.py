"""Test DeFi analytics modules."""

import math
import pytest
from nexus.defi.il_calculator import ILCalculator
from nexus.defi.yield_optimizer import YieldOptimizer


def test_il_no_change():
    il = ILCalculator.calculate(1.0)
    assert il == pytest.approx(0.0)


def test_il_2x_price():
    il = ILCalculator.calculate(2.0)
    assert il == pytest.approx(0.0572, abs=0.001)  # ~5.72%


def test_il_5x_price():
    il = ILCalculator.calculate(5.0)
    assert il == pytest.approx(0.2546, abs=0.001)  # ~25.5%


def test_il_zero_price():
    il = ILCalculator.calculate(0)
    assert il == 0.0


def test_breakeven():
    result = ILCalculator.breakeven(2.0, fee_apr=0.5, days=365)
    assert "il_pct" in result
    assert "fees_pct" in result
    assert result["fees_pct"] == pytest.approx(50.0)


def test_apy_calculation():
    # 10% APR compounded daily
    apy = YieldOptimizer.calculate_apy(0.10, 365)
    assert apy > 0.10  # APY > APR due to compounding
    assert apy == pytest.approx(0.10516, abs=0.001)


def test_yield_ranking():
    from nexus.defi.yield_optimizer import YieldOpportunity
    opps = [
        YieldOpportunity("aave", "pool1", 5.0, 1e9, 0.1, "eth", "USDC"),
        YieldOpportunity("curve", "pool2", 10.0, 500e6, 0.3, "eth", "ETH/USDC"),
    ]
    opt = YieldOptimizer()
    ranked = opt.rank_opportunities(opps)
    # aave: 5/0.1=50, curve: 10/0.3=33.3 → aave first
    assert ranked[0].protocol == "aave"
