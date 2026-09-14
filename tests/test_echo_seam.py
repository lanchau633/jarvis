"""Milestone 1 check: drive VoiceListener._dispatch_query directly (no mic,
no wake word, no real TTS engine) to prove the two integration seams work —
text-in reaches our agent, and the agent's reply reaches TTS output.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.dummy import EchoAgent
from voice.core.listening.listener import VoiceListener


class FakeTTS:
    def __init__(self):
        self.enabled = True
        self.spoken = None

    def speak(self, text, completion_callback=None, duration_callback=None):
        self.spoken = text


class FakeListenerSelf:
    """Minimal stand-in for VoiceListener with only what _dispatch_query touches."""

    def __init__(self, agent, tts):
        self.agent = agent
        self.tts = tts
        self.echo_detector = None
        self._last_detected_language = None
        self.db = None
        self.cfg = None
        self.dialogue_memory = None

    def _clear_audio_buffers(self):
        pass

    def _stop_thinking_tune(self):
        pass

    def activate_hot_window(self):
        pass

    def track_tts_start(self, reply):
        pass


def main() -> None:
    tts = FakeTTS()
    fake_self = FakeListenerSelf(agent=EchoAgent(), tts=tts)

    VoiceListener._dispatch_query(fake_self, "what time is it")

    assert tts.spoken == "You said: what time is it", f"unexpected reply: {tts.spoken!r}"
    print("OK: text-in -> agent -> TTS seam works:", tts.spoken)


if __name__ == "__main__":
    main()
