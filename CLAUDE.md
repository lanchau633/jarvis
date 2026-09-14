# Personal JARVIS Assistant

A local-first personal AI assistant combining the agent runtime of **OpenJarvis** with the voice interface of **isair/jarvis**, using **Obsidian** as a human-readable memory backend.

## Source Repos

- **OpenJarvis** (Stanford, agent runtime): https://github.com/open-jarvis/OpenJarvis
- **isair/jarvis** (voice assistant): https://github.com/isair/jarvis

Do not fork or merge these repos directly. Treat them as reference/source material — clone them into `reference/openjarvis` and `reference/jarvis-voice` (gitignored) so their code can be read and selectively vendored, but this project has its own git history.

## What We're Taking From Each

**From OpenJarvis:**
- The agent runtime (`orchestrator`, `native_react`, `operative`, etc.) — this is the "brain"
- Local model routing via Ollama
- The skills system, if useful later

**From isair/jarvis:**
- Wake-word detection + conversational rolling context loop
- Whisper STT pipeline
- Piper/Chatterbox TTS output
- NOT its own LLM call or its own knowledge-graph memory — we replace both

## Architecture

```
[mic] -> isair voice loop (wake word, STT) -> plain text
                                                  |
                                                  v
                                    OpenJarvis agent runtime
                                    (reads/writes memory via
                                     our Obsidian adapter)
                                                  |
                                                  v
                              plain text response -> Piper TTS -> [speaker]
```

The two integration seams:
1. **Text in**: wherever isair/jarvis currently hands transcribed text to its own LLM — redirect this to call an OpenJarvis agent instead.
2. **Text out**: whatever the OpenJarvis agent returns — hand this to isair's TTS output function instead of its own reply pipeline.

## Obsidian Memory Backend

Instead of a hidden SQLite/vector DB, memory writes become markdown notes in an Obsidian vault:
- One note per memory item, YAML frontmatter for tags/dates/entities
- `[[wikilinks]]` between related notes to form a knowledge graph, browsable in Obsidian's graph view
- Daily notes act as the "diary" layer (mirrors isair/jarvis's diary concept)
- Retrieval: keyword/grep search over the vault to start; embeddings later if needed
- Optional: Obsidian Local REST API plugin for live read/write while the vault is open in the app

This module needs to implement whatever memory read/write interface the OpenJarvis agent runtime expects, backed by vault files instead of a database.

## Milestones (build in this order — don't parallelize)

1. **Echo skeleton**: voice loop (wake word + STT + TTS) wired to a dummy agent that just echoes text back. Proves the seams work before any real intelligence is involved.
2. **Real agent swap**: replace the dummy agent with an actual OpenJarvis agent (start with `simple` or `orchestrator`).
3. **Obsidian memory layer**: build the vault-backed memory adapter, wire it into the agent's memory calls, verify notes are readable/linked correctly in Obsidian itself.
4. **Polish**: tune wake word sensitivity, tool selection, memory retrieval quality.

## Tech Stack

- Python (both source repos are Python — no cross-language bridging needed)
- Ollama for local model serving
- Whisper (STT) + Piper (TTS), vendored from isair/jarvis
- Obsidian vault (plain markdown + YAML frontmatter) as the memory store

## Conventions

- Keep the voice loop, the agent runtime, and the memory adapter as separate modules with clear interfaces — don't let them get tangled, since each may need to be swapped or upgraded independently as upstream repos evolve.
- Test each milestone in isolation before moving to the next.
