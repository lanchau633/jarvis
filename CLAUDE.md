# Personal JARVIS Assistant

A local-first personal AI desktop app. A pod-based UI sits on top of the **OpenJarvis** agent runtime, with an **Obsidian** vault as a human-readable memory backend. Speech and TTS are vendored from **isair/jarvis**.

## Source Repos

- **OpenJarvis** (Stanford, agent runtime): https://github.com/open-jarvis/OpenJarvis
- **isair/jarvis** (voice assistant): https://github.com/isair/jarvis

Do not fork or merge these repos directly. They are reference material, cloned into `reference/openjarvis` and `reference/jarvis-voice` (gitignored) so their code can be read and selectively vendored. This project has its own git history.

## What We Take From Each

**From OpenJarvis:** the agent runtime (the "brain"), local model routing via Ollama, and the skills/tools system.

**From isair/jarvis:** the Whisper STT pipeline and Piper TTS output, vendored into `voice/core`.

Explicitly **not** used from isair/jarvis, even though the code is vendored and present:
- Wake-word detection and the hot-window/follow-up loop — input is push-to-talk, not always-listening
- The intent judge — it exists to decide whether ambient speech is directed at the assistant, which is meaningless when the user is holding a button
- Its reply engine (`voice/core/reply/`) — OpenJarvis generates replies
- Its knowledge-graph memory (`voice/core/memory/`) — the Obsidian vault replaces it

## Architecture

```
        ┌──────────────── PyQt6 window ────────────────┐
        │  Web UI (HTML/CSS/JS) — pods                 │
        └───────────────────┬──────────────────────────┘
                            │  QWebChannel bridge
                            │  (in-process, no HTTP, no open port)
        ┌───────────────────▼──────────────────────────┐
        │  Python backend                              │
        │    OpenJarvis agent runtime (Ollama)         │
        │    Obsidian memory adapter                   │
        │    Whisper STT / Piper TTS (voice/core)      │
        │    Google integrations (Calendar, Gmail)     │
        └──────────────────────────────────────────────┘
```

### Why this stack

The UI is web tech because the target aesthetic (angular `clip-path` panels, conic gradients, custom type) is trivial in CSS and painful in native Qt widgets.

It is hosted in **PyQt6 + QtWebEngine with a QWebChannel bridge, not a local web server**. JavaScript calls Python methods directly; there is no HTTP layer and no listening port. This matters because the app holds Gmail and Calendar credentials — a Flask server on localhost is reachable by every other process on the machine, and a misconfigured bind exposes it to the network.

For UI development, attach Chrome DevTools via `QTWEBENGINE_REMOTE_DEBUGGING=9222` rather than reintroducing a server.

## Pods

The UI is a grid of pods. Each pod is a self-contained panel with its own backend module.

1. **Messaging** — chat with the agent. The reference implementation for the UI↔backend bridge.
2. **Mic** — push-to-talk. Hold to record, release to transcribe (Whisper), reply spoken via Piper. No wake word.
3. **Calendar / To-Do** — Google Calendar events beside a task list; tasks can be dragged onto the calendar.
4. **Email** — read and draft mail; sort into relevance bins (important / semi / spam).
5. **Daily digest** — date, time, weather, calendar events for today, email summary.

## Obsidian Memory Backend

Memory is markdown in a vault: one note per item, YAML frontmatter, `[[wikilinks]]` between related notes, daily notes as the diary layer.

**Memory is tiered — not everything is retrieval.** Treating it as one undifferentiated RAG store is the main failure mode to avoid:

1. **Profile (always loaded).** A small, stable set of facts and preferences — location, what the user considers important, how they like things done. These go into the system prompt every time. Retrieving them is strictly worse than always including them, because a lookup can fail to return something that costs ~50 tokens to just always send.
2. **Structured (queried).** Tasks, events, anything with fields. These are read with real queries — filter by status, date, tag — not similarity search. "The 3 most semantically similar tasks" is never the right answer to "what's due this week".
3. **Episodic (retrieved).** Past requests and conversations. Unbounded and open-ended, so this is the only tier that is genuinely retrieval-shaped.

**Start with keyword/grep search over frontmatter, not embeddings.** The local chat model is small and CPU-bound, so context is expensive and prefill dominates latency; small models also degrade when handed several semi-relevant chunks. That inverts the usual tradeoff — favour **precision over recall**. Consistent frontmatter (`type`, `tags`, `date`, `entities`) is what makes cheap retrieval accurate, and is more load-bearing than the choice of search algorithm.

`nomic-embed-text` and `faiss-cpu` are already available, so adding vector search later is a config change, not a rewrite. Add it only when grep demonstrably fails.

## Credentials

Google OAuth refresh tokens grant ongoing access to the user's mail and calendar. Treat storage as a design decision, not an afterthought:

- Store tokens via Windows DPAPI / Credential Manager, never a plaintext `token.json` beside the code
- Add token/credential paths to `.gitignore` *before* writing the first one
- Google's installed-app OAuth flow needs a transient `localhost` listener to catch the consent redirect; that is unavoidable, but it must close immediately after sign-in and never persist

## Milestones (build in this order — don't parallelize)

Credential-free work comes first deliberately: the UI↔backend bridge must be proven before anyone is also fighting an OAuth consent screen.

1. **Shell + messaging pod.** PyQt6 window rendering the web UI, QWebChannel bridge, messaging pod wired end-to-end to a real OpenJarvis agent. Proves the architecture.
2. **Mic pod.** Push-to-talk → Whisper → same agent path → Piper. Reuses the vendored STT/TTS.
3. **Obsidian memory.** The tiered model above, wired into the agent's memory calls. Verify notes are readable and linked correctly in Obsidian itself.
4. **Calendar / To-Do pod.** First Google integration — OAuth and token storage get solved here, on the simpler of the two APIs.
5. **Email pod.** Reading, drafting, relevance binning.
6. **Daily digest pod.** Composes the pieces built above.
7. **Polish.** Tool selection, retrieval quality, latency.

## Tech Stack

- Python — both source repos are Python, no cross-language bridging
- PyQt6 + QtWebEngine (UI shell), QWebChannel (bridge)
- Ollama for local model serving; small models only (CPU-bound machine, no dedicated GPU)
- Whisper (STT) + Piper (TTS), vendored from isair/jarvis
- Obsidian vault (markdown + YAML frontmatter) as the memory store

## Conventions

- Keep the UI, the agent runtime, the memory adapter, and each pod's backend as separate modules with clear interfaces. They are swapped and upgraded independently as upstream repos evolve.
- The agent is injected into consumers, never imported directly by them — see `agent/base.py` for the interface and how `voice/core` receives it.
- Test each milestone in isolation before moving to the next.
- Latency is a feature. The local model runs on CPU; anything added to the request path is paid for on every interaction.

## Environment

- Run from `C:\Users\lando\projects\JARVIS` — **not** a OneDrive-synced folder. A conda env is tens of thousands of files and will exhaust cloud storage quota.
- Python 3.11 conda env at `.conda-env` (gitignored). Python 3.14 cannot build this dependency set.
- Runtime config lives outside the repo at `~/.config/jarvis/config.json`.
