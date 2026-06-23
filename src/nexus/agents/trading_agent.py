"""LLM-powered trading agent with market analysis capabilities."""

from __future__ import annotations

import json
from typing import Any

import structlog

from nexus.agents.base import BaseAgent
from nexus.data.models import Signal, SignalType, Token

logger = structlog.get_logger()

SYSTEM_PROMPT = """You are an expert crypto trading analyst. Analyze the given market data and produce a trading signal.

Output JSON: {"action": "buy"|"sell"|"hold", "confidence": 0.0-1.0, "reasoning": "...", "price_target": number|null}

Consider: technical indicators, volume, sentiment, whale activity, macro conditions.
Be conservative. Only high-conviction signals with confidence > 0.7.
"""


class TradingAgent(BaseAgent):
    """Trading agent powered by LLM analysis."""

    def __init__(self, model: str = "gpt-4", strategy: str = "momentum", **kwargs: Any):
        super().__init__(model=model, **kwargs)
        self.strategy = strategy

    async def analyze(self, context: dict[str, Any]) -> list[Signal]:
        """Analyze market data using LLM."""
        token_data = context.get("tokens", [])
        timeframe = context.get("timeframe", "4h")

        signals = []
        for token_info in token_data:
            prompt = self._build_analysis_prompt(token_info, timeframe)
            try:
                response = await self._call_llm(prompt)
                signal = self._parse_signal(response, token_info)
                if signal:
                    signals.append(signal)
                    self.memory.remember({
                        "type": "signal",
                        "token": token_info.get("symbol"),
                        "action": signal.signal_type.value,
                        "confidence": signal.confidence,
                    })
            except Exception as e:
                logger.error("trading_agent.analyze.error", token=token_info.get("symbol"), error=str(e))

        return signals

    async def plan(self, signals: list[Signal]) -> list[dict[str, Any]]:
        """Create execution plan from signals."""
        plan = []
        for signal in signals:
            if signal.signal_type == SignalType.HOLD:
                continue
            if signal.confidence < 0.7:
                continue
            plan.append({
                "action": signal.signal_type.value,
                "token": signal.token.symbol,
                "confidence": signal.confidence,
                "price_target": signal.price_target,
                "size_pct": min(signal.confidence * 20, 10),  # max 10% per trade
            })
        return plan

    def _build_analysis_prompt(self, token_info: dict[str, Any], timeframe: str) -> str:
        return f"""Analyze {token_info.get("symbol", "UNKNOWN")} on {timeframe} timeframe.

Current Data:
- Price: ${token_info.get("price", 0):,.2f}
- 24h Change: {token_info.get("change_24h", 0):.1f}%
- Volume 24h: ${token_info.get("volume", 0):,.0f}
- Market Cap: ${token_info.get("market_cap", 0):,.0f}
- RSI: {token_info.get("rsi", "N/A")}
- MACD: {token_info.get("macd", "N/A")}
- Whale Activity: {token_info.get("whale_signal", "neutral")}
- Sentiment: {token_info.get("sentiment", "neutral")}

Strategy: {self.strategy}
{SYSTEM_PROMPT}"""

    async def _call_llm(self, prompt: str) -> str:
        """Call LLM API. Supports OpenAI and Anthropic."""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=500,
            )
            return response.choices[0].message.content or "{}"
        except Exception:
            return json.dumps({"action": "hold", "confidence": 0.0, "reasoning": "LLM unavailable"})

    def _parse_signal(self, response: str, token_info: dict[str, Any]) -> Signal | None:
        """Parse LLM response into a Signal."""
        try:
            data = json.loads(response)
            action_map = {"buy": SignalType.BUY, "sell": SignalType.SELL, "hold": SignalType.HOLD}
            token = Token(
                address=token_info.get("address", "0x0"),
                symbol=token_info.get("symbol", "???"),
                name=token_info.get("name", ""),
                chain_id=token_info.get("chain_id", 1),
                price_usd=token_info.get("price", 0),
            )
            return Signal(
                source=self.agent_id,
                signal_type=action_map.get(data.get("action", "hold"), SignalType.HOLD),
                token=token,
                confidence=float(data.get("confidence", 0)),
                price_target=data.get("price_target"),
                reasoning=data.get("reasoning", ""),
            )
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("trading_agent.parse_error", error=str(e))
            return None
