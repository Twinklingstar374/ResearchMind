"""
ResearchMemory — Manages conversation history and research context
with a sliding window of the last 10 exchanges.
"""

from collections import deque
from datetime import datetime


class ResearchMemory:
    """
    Manages chat history and accumulated research context for a session.
    Uses a sliding window of the last 10 exchanges to keep context concise.
    """

    def __init__(self, max_exchanges: int = 10):
        self.max_exchanges = max_exchanges
        self._exchanges: deque = deque(maxlen=max_exchanges)
        self._research_store: list[dict] = []  # {query, report_dict, timestamp}

    # ── Chat History ────────────────────────────────────────────────────────

    def add_exchange(self, human: str, ai: str) -> None:
        """Add a human/AI exchange to the sliding window."""
        self._exchanges.append({
            "human": human,
            "ai": ai,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(self) -> list[dict]:
        """
        Return last 10 exchanges as a flat list of role-content dicts,
        suitable for passing to LLM as message history.
        """
        messages = []
        for exchange in self._exchanges:
            messages.append({"role": "user", "content": exchange["human"]})
            messages.append({"role": "assistant", "content": exchange["ai"]})
        return messages

    def get_history_as_exchanges(self) -> list[dict]:
        """Return raw exchange dicts with human/ai/timestamp keys."""
        return list(self._exchanges)

    # ── Research Store ──────────────────────────────────────────────────────

    def store_research(self, query: str, report_dict: dict) -> None:
        """
        Store a completed research result.

        Args:
            query: The original research query
            report_dict: The full result dict from ResearchAgent.run()
        """
        self._research_store.append({
            "query": query,
            "report_dict": report_dict,
            "timestamp": datetime.now().isoformat()
        })

    def get_research_context(self) -> str:
        """
        Returns a short summary of all past research topics in this session,
        useful for giving the LLM context about what has already been covered.
        """
        if not self._research_store:
            return "No prior research conducted in this session."

        lines = ["Past research topics in this session:"]
        for i, entry in enumerate(self._research_store, 1):
            lines.append(f"  {i}. {entry['query']} (at {entry['timestamp'][:16]})")
        return "\n".join(lines)

    def get_last_report(self) -> dict | None:
        """Return the most recent research report dict, or None."""
        if self._research_store:
            return self._research_store[-1]["report_dict"]
        return None

    def has_research(self) -> bool:
        """True if at least one research result has been stored."""
        return len(self._research_store) > 0

    def total_queries(self) -> int:
        """Total number of research queries made in this session."""
        return len(self._research_store)

    # ── Session Reset ───────────────────────────────────────────────────────

    def clear(self) -> None:
        """Full reset — clears both chat history and research store."""
        self._exchanges.clear()
        self._research_store.clear()
