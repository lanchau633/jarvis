"""Agent runtime interface.

The voice loop (voice/core) depends only on this shape: something with a
`run(text) -> str | None` method. Swapping the dummy echo agent for a real
OpenJarvis-backed agent (Milestone 2) means implementing this interface,
not touching the voice loop.
"""

from typing import Optional, Protocol


class Agent(Protocol):
    def run(self, text: str) -> Optional[str]:
        """Take a transcribed user query, return the reply text (or None for no reply)."""
        ...
