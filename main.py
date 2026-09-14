"""JARVIS entry point — Milestone 1 echo skeleton.

Wires isair/jarvis's voice loop (vendored in voice/core) to our own agent
runtime (agent/) instead of isair's own reply engine. Swap the agent
constructed below to move to Milestone 2 (real OpenJarvis agent) without
touching the voice loop.
"""

import sys

from agent.dummy import EchoAgent
from voice.core.daemon import main as run_daemon


if __name__ == "__main__":
    smoke_test = "--smoke-test" in set(sys.argv[1:])
    run_daemon(smoke_test=smoke_test, agent=EchoAgent())
