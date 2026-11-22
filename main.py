"""JARVIS entry point.

Launches the desktop shell. `--voice` runs the legacy headless voice daemon
instead, which the mic pod will fold into the shell in Milestone 2.
"""

import sys

from agent.gemini_agent import GeminiAgent


def build_agent():
    # Consumers depend only on the agent/base.py interface, so swapping this
    # for OpenJarvisAgent (local Ollama) or EchoAgent isolates UI problems
    # from model ones.
    return GeminiAgent()


if __name__ == "__main__":
    args = set(sys.argv[1:])
    agent = build_agent()

    if "--voice" in args:
        from voice.core.daemon import main as run_daemon
        run_daemon(smoke_test="--smoke-test" in args, agent=agent)
    else:
        from app.shell import run
        sys.exit(run(agent))
