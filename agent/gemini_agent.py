"""Gemini-backed agent, adapted to the agent/base.py interface.

Uses Gemini's OpenAI-compatible endpoint through the already-installed
`openai` package rather than adding Google's SDK for one call.
"""

import os
from typing import Optional

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# The newest Flash models (3.7, 3.8, flash-latest) return 503/timeout under
# load; 3.6 is the most capable one answering reliably. Re-check with
# list_models() if this starts failing.
DEFAULT_MODEL = "gemini-3.6-flash"


class GeminiAgent:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        api_key: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        from dotenv import load_dotenv

        load_dotenv()
        self._key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self._key:
            raise RuntimeError("GEMINI_API_KEY is not set (add it to .env)")

        self.model = model
        self._system_prompt = system_prompt
        self._client_obj = None

    @property
    def _client(self):
        # Importing openai costs seconds; deferring keeps window startup instant.
        if self._client_obj is None:
            from openai import OpenAI

            self._client_obj = OpenAI(api_key=self._key, base_url=BASE_URL)
        return self._client_obj

    def list_models(self) -> list[str]:
        return sorted(m.id for m in self._client.models.list())

    def run(self, text: str) -> Optional[str]:
        messages = []
        if self._system_prompt:
            messages.append({"role": "system", "content": self._system_prompt})
        messages.append({"role": "user", "content": text})

        response = self._client.chat.completions.create(
            model=self.model, messages=messages
        )
        return response.choices[0].message.content
