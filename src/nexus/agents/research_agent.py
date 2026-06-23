"""Research agent — web scraping, paper analysis, alpha finding."""

from __future__ import annotations

from typing import Any

import structlog

from nexus.agents.base import BaseAgent
from nexus.data.models import Signal, SignalType, Token

logger = structlog.get_logger()


class ResearchAgent(BaseAgent):
    """Finds alpha through research and analysis."""

    async def analyze(self, context: dict[str, Any]) -> list[Signal]:
        """Research market conditions and find opportunities."""
        signals = []
        sources = context.get("sources", [])

        for source in sources:
            try:
                findings = await self._research_source(source)
                for finding in findings:
                    signal = self._finding_to_signal(finding)
                    if signal:
                        signals.append(signal)
            except Exception as e:
                logger.error("research.error", source=source.get("name"), error=str(e))

        return signals

    async def plan(self, signals: list[Signal]) -> list[dict[str, Any]]:
        """Research agent recommends further investigation."""
        return [
            {"action": "investigate", "token": s.token.symbol, "reasoning": s.reasoning}
            for s in signals if s.confidence > 0.5
        ]

    async def _research_source(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        """Research a single source. Override for specific source types."""
        source_type = source.get("type", "unknown")
        if source_type == "twitter":
            return await self._analyze_social(source)
        elif source_type == "onchain":
            return await self._analyze_onchain(source)
        return []

    async def _analyze_social(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze social media signals."""
        return [{"type": "social", "sentiment": "neutral", "volume": 0}]

    async def _analyze_onchain(self, source: dict[str, Any]) -> list[dict[str, Any]]:
        """Analyze on-chain data."""
        return [{"type": "onchain", "signal": "neutral"}]

    def _finding_to_signal(self, finding: dict[str, Any]) -> Signal | None:
        """Convert a research finding to a trading signal."""
        sentiment = finding.get("sentiment", "neutral")
        if sentiment == "neutral":
            return None
        token = Token(address="0x0", symbol=finding.get("symbol", "???"), name="", chain_id=1)
        return Signal(
            source=self.agent_id,
            signal_type=SignalType.BUY if sentiment == "bullish" else SignalType.SELL,
            token=token,
            confidence=finding.get("confidence", 0.5),
            reasoning=finding.get("reasoning", ""),
        )
