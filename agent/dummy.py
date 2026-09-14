"""Milestone 1 dummy agent: echoes the query back, proving the voice-loop seams."""

from typing import Optional


class EchoAgent:
    def run(self, text: str) -> Optional[str]:
        return f"You said: {text}"
