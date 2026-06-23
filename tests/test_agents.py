"""Test agent orchestrator and trading agent."""

import asyncio
import pytest
from nexus.agents.base import BaseAgent
from nexus.agents.orchestrator import AgentOrchestrator
from nexus.agents.trading_agent import TradingAgent
from nexus.agents.risk_agent import RiskAgent
from nexus.data.models import Signal, SignalType, Token


class MockAgent(BaseAgent):
    def __init__(self, signal_type: SignalType = SignalType.BUY, confidence: float = 0.8):
        super().__init__()
        self._signal_type = signal_type
        self._confidence = confidence

    async def analyze(self, context):
        token = Token(address="0x0", symbol="ETH", name="Ethereum", chain_id=1)
        return Signal(source=self.agent_id, signal_type=self._signal_type, token=token, confidence=self._confidence)

    async def plan(self, signals):
        return [{"action": "test"}]


def test_orchestrator_consensus():
    agents = [
        MockAgent(SignalType.BUY, 0.9),
        MockAgent(SignalType.BUY, 0.7),
        MockAgent(SignalType.SELL, 0.6),
    ]
    orch = AgentOrchestrator(agents, consensus_threshold=0.6)
    result = asyncio.run(orch.analyze({"tokens": []}))
    assert result["consensus"]["action"] == "buy"
    assert result["confidence"] > 0.6


def test_orchestrator_no_consensus():
    agents = [
        MockAgent(SignalType.BUY, 0.5),
        MockAgent(SignalType.SELL, 0.5),
    ]
    orch = AgentOrchestrator(agents, consensus_threshold=0.8)
    result = asyncio.run(orch.analyze({"tokens": []}))
    assert result["consensus"]["action"] == "hold"


def test_risk_agent_drawdown():
    agent = RiskAgent(max_drawdown=0.15)
    signals = asyncio.run(agent.analyze({
        "portfolio_value": 80000,
        "peak_value": 100000,
        "positions": [],
    }))
    assert len(signals) > 0  # Should warn about drawdown


def test_risk_agent_position_sizing():
    agent = RiskAgent(max_position_pct=0.2)
    size = agent.calculate_position_size(100000, risk_per_trade=0.02, stop_distance=0.05)
    assert size <= 20000  # Max 20% of account


def test_agent_memory():
    agent = MockAgent()
    agent.memory.remember({"type": "test", "value": 42}, important=True)
    recent = agent.memory.recall_recent(1)
    assert len(recent) == 1
    important = agent.memory.recall_important()
    assert len(important) == 1
