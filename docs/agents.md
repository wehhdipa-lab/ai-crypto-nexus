# Agent Framework Guide

## Creating a Custom Agent

```python
from nexus.agents.base import BaseAgent
from nexus.data.models import Signal, SignalType, Token

class MyAgent(BaseAgent):
    async def analyze(self, context):
        # Your analysis logic
        token = Token(address="0x...", symbol="ETH", name="Ethereum", chain_id=1)
        return Signal(
            source=self.agent_id,
            signal_type=SignalType.BUY,
            token=token,
            confidence=0.85,
            reasoning="Custom analysis result",
        )

    async def plan(self, signals):
        return [{"action": s.signal_type.value, "token": s.token.symbol} for s in signals]
```

## Using the Orchestrator

```python
from nexus.agents import AgentOrchestrator, TradingAgent, RiskAgent

orchestrator = AgentOrchestrator(
    agents=[TradingAgent(), RiskAgent()],
    consensus_threshold=0.7,
)

result = await orchestrator.execute_consensus({
    "tokens": [{"symbol": "ETH", "price": 3500, "change_24h": 2.5}],
    "portfolio_value": 100000,
    "peak_value": 105000,
    "positions": [],
})
```

## Agent Memory

All agents have built-in memory:
- **Short-term**: last 100 events (rolling window)
- **Long-term**: manually flagged important events

```python
agent.memory.remember({"type": "trade", "pnl": 500}, important=True)
recent = agent.memory.recall_recent(10)
important = agent.memory.recall_important("trade")
```
