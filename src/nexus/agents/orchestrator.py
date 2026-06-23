"""Multi-agent orchestrator with consensus mechanism."""

from __future__ import annotations

import asyncio
from typing import Any

import structlog

from nexus.agents.base import BaseAgent
from nexus.data.models import Signal, SignalType

logger = structlog.get_logger()


class AgentOrchestrator:
    """Orchestrates multiple specialized agents with consensus-based decision making."""

    def __init__(
        self,
        agents: list[BaseAgent],
        consensus_threshold: float = 0.7,
        max_concurrent: int = 5,
    ):
        self.agents = {a.agent_id: a for a in agents}
        self.consensus_threshold = consensus_threshold
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run all agents in parallel and aggregate signals."""
        tasks = []
        for agent in self.agents.values():
            tasks.append(self._run_agent_analyze(agent, context))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_signals: list[Signal] = []
        agent_results: dict[str, Any] = {}

        for agent_id, result in zip(self.agents.keys(), results):
            if isinstance(result, Exception):
                logger.error("orchestrator.agent.error", agent=agent_id, error=str(result))
                agent_results[agent_id] = {"error": str(result)}
            else:
                if isinstance(result, Signal):
                    all_signals.append(result)
                elif isinstance(result, list):
                    all_signals.extend(result)
                agent_results[agent_id] = result

        consensus = self._compute_consensus(all_signals)

        return {
            "signals": all_signals,
            "agent_results": agent_results,
            "consensus": consensus,
            "confidence": consensus["confidence"],
        }

    async def _run_agent_analyze(self, agent: BaseAgent, context: dict[str, Any]) -> Any:
        async with self.semaphore:
            return await agent.analyze(context)

    def _compute_consensus(self, signals: list[Signal]) -> dict[str, Any]:
        """Weighted consensus across agent signals."""
        if not signals:
            return {"action": "hold", "confidence": 0.0, "votes": {}}

        votes: dict[str, float] = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        for signal in signals:
            votes[signal.signal_type.value] += signal.confidence

        total = sum(votes.values())
        if total == 0:
            return {"action": "hold", "confidence": 0.0, "votes": votes}

        normalized = {k: v / total for k, v in votes.items()}
        best_action = max(normalized, key=normalized.get)  # type: ignore
        confidence = normalized[best_action]

        return {
            "action": best_action if confidence >= self.consensus_threshold else "hold",
            "confidence": confidence,
            "votes": normalized,
            "num_signals": len(signals),
        }

    async def execute_consensus(self, context: dict[str, Any]) -> dict[str, Any]:
        """Full cycle: analyze → consensus → execute if threshold met."""
        analysis = await self.analyze(context)

        if analysis["confidence"] < self.consensus_threshold:
            logger.info("orchestrator.no_consensus", confidence=analysis["confidence"])
            return {**analysis, "executed": False, "reason": "below_threshold"}

        # Execute with all agents that agree
        consensus_action = analysis["consensus"]["action"]
        execution_plan = [{"action": consensus_action, "signals": analysis["signals"]}]

        results = []
        for agent in self.agents.values():
            plan = await agent.plan(analysis["signals"])
            result = await agent.execute(plan)
            results.append(result)

        return {**analysis, "executed": True, "execution_results": results}
