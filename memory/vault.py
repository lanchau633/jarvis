"""Obsidian vault memory adapter.

Tier 1 (profile): a small, stable set of facts loaded into every request.
Cheaper and more reliable than retrieving them, per CLAUDE.md.
"""

from pathlib import Path

VAULT_DIR = Path(__file__).resolve().parent.parent / "vault"
PROFILE_PATH = VAULT_DIR / "profile.md"

BASE_PROMPT = (
    "You are JARVIS, a personal assistant running locally on the user's machine. "
    "Be direct and concise; skip pleasantries and filler. "
    "You have access to the facts below about the user. Use them without being asked, "
    "and never claim you don't know things about the user that appear here."
)


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.find("\n---", 3)
    return text[end + 4 :] if end != -1 else text


def load_profile() -> str:
    """Profile note body, or empty string if the vault has no profile yet."""
    if not PROFILE_PATH.exists():
        return ""
    return _strip_frontmatter(PROFILE_PATH.read_text(encoding="utf-8")).strip()


def build_system_prompt() -> str:
    profile = load_profile()
    if not profile:
        return BASE_PROMPT
    return f"{BASE_PROMPT}\n\n## What you know about the user\n\n{profile}"
