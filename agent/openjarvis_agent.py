"""OpenJarvis-backed agent, adapted to the agent/base.py interface.

Constructs the runtime directly rather than going through OpenJarvis's own
config system: passing both temperature and max_tokens short-circuits its
load_config() call, so nothing reads or creates ~/.openjarvis, and no
analytics or security scaffolding is pulled in.
"""

from typing import Optional

DEFAULT_HOST = "http://localhost:11434"
DEFAULT_MODEL = "qwen3.5:0.8b"


class OpenJarvisAgent:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        host: str = DEFAULT_HOST,
        temperature: float = 0.7,
        max_tokens: int = 512,
        system_prompt: Optional[str] = None,
    ):
        self.model = model
        self._host = host
        self._kwargs = {"temperature": temperature, "max_tokens": max_tokens}
        if system_prompt is not None:
            self._kwargs["prompt_builder"] = lambda *_a, **_k: system_prompt
        self._agent = None

    def _ensure_agent(self):
        # Importing OpenJarvis costs ~10s; deferring it keeps window startup
        # instant and pays the cost on the first message, where the UI is
        # already showing a busy state.
        if self._agent is None:
            from openjarvis.agents.simple import SimpleAgent
            from openjarvis.engine.ollama import OllamaEngine

            self._agent = SimpleAgent(OllamaEngine(self._host), self.model, **self._kwargs)
        return self._agent

    def run(self, text: str) -> Optional[str]:
        return self._ensure_agent().run(text).content
