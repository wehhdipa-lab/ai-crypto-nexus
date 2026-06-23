# Architecture

## System Overview

AI-Crypto Nexus is a modular platform combining AI agents with on-chain intelligence.

```
┌─────────────────────────────────────────────────┐
│                   CLI / API Layer                │
├───────────┬───────────┬──────────┬──────────────┤
│  Agents   │  Trading  │   DeFi   │  On-Chain    │
│  Engine   │  Engine   │ Analytics│ Intelligence │
├───────────┴───────────┴──────────┴──────────────┤
│           Unified Data Pipeline                  │
│        (Event Streaming + Feature Store)         │
├─────────────────────────────────────────────────┤
│    Ethereum │ Arbitrum │ Base │ Polygon │ BSC    │
└─────────────────────────────────────────────────┘
```

## Agent Framework

The multi-agent system uses a consensus-based approach:

1. **BaseAgent** — abstract class with memory, planning, execution
2. **AgentOrchestrator** — runs agents in parallel, computes weighted consensus
3. **Specialized Agents** — TradingAgent (LLM), RiskAgent (quantitative), ResearchAgent (data)

### Consensus Mechanism

Each agent produces signals with confidence scores. The orchestrator aggregates:
- Signals below individual threshold (0.7) are discarded
- Remaining signals are weighted by confidence
- Consensus requires >70% agreement (configurable)
- RiskAgent has veto power on risk-limit breaches

## Data Pipeline

```
WebSocket Feeds → Stream Processor → Feature Store → Signal Bus → Agents
                     ↓
              Event Log (Redis Streams)
```

## Security Model

- Private keys: Fernet-encrypted keystore, never in memory unencrypted longer than needed
- Transactions: always simulated via `eth_call` before broadcast
- Rate limiting on all external API calls
- Circuit breakers halt trading on anomalous conditions
