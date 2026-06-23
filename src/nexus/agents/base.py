"""Base agent class for the multi-agent framework."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

import structlog

from nexus.data.models import AgentState, Signal

logger = structlog.get_logger()


class AgentMemory:
    """Short-term and long-term memory for agents."""

    def __init__(self, max_short_term: int = 100):
        self.short_term: list[dict[str, Any]] = []
        self.long_term: list[dict[str, Any]] = []
        self.max_short_term = max_short_term

    def remember(self, event: dict[str, Any], important: bool = False) -> None:
        event["timestamp"] = datetime.utcnow().isoformat()
        if important:
            self.long_term.append(event)
            logger.info("agent.memory.long_term", event_type=event.get("type"))
        self.short_term.append(event)
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)

    def recall_recent(self, n: int = 10) -> list[dict[str, Any]]:
        return self.short_term[-n:]

    def recall_important(self, query: str | None = None) -> list[dict[str, Any]]:
        if query:
            return [e for e in self.long_term if query.lower() in str(e).lower()]
        return self.long_term


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, agent_id: str | None = None, model: str = "gpt-4"):
        self.agent_id = agent_id or f"{self.__class__.__name__}_{uuid.uuid4().hex[:8]}"
        self.model = model
        self.memory = AgentMemory()
        self.state = AgentState(agent_id=self.agent_id)
        self._running = False

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> Signal | list[Signal]:
        """Analyze context and produce signals."""
        ...

    @abstractmethod
    async def plan(self, signals: list[Signal]) -> list[dict[str, Any]]:
        """Create execution plan from signals."""
        ...

    async def execute(self, plan: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Execute a plan. Override for custom execution logic."""
        results = []
        for step in plan:
            try:
                result = await self._execute_step(step)
                results.append(result)
                self.memory.remember({"type": "execution", "step": step, "result": result})
            except Exception as e:
                logger.error("agent.execute.error", agent=self.agent_id, error=str(e))
                results.append({"error": str(e)})
        return results

    async def _execute_step(self, step: dict[str, Any]) -> dict[str, Any]:
        """Override for step-level execution."""
        return {"status": "completed", "step": step}

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Full agent cycle: analyze → plan → execute."""
        self.state.status = "analyzing"
        signals = await self.analyze(context)

        if isinstance(signals, Signal):
            signals = [signals]

        self.state.status = "planning"
        plan = await self.plan(signals)

        self.state.status = "executing"
        results = await self.execute(plan)

        self.state.status = "idle"
        self.state.total_signals += len(signals)
        self.state.last_active = datetime.utcnow()

        return {"signals": signals, "plan": plan, "results": results}
