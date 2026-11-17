import re

from app.models import Requirement


def _normalize(text: str) -> str:
    # collapse line breaks so "design\nlife" matches the keyword "design life"
    return " ".join(text.split())


def _score(text: str, keywords: list[str]) -> float:
    text = _normalize(text)
    score = 0.0
    for kw in keywords:
        # whole-word match, allowing a plural "s" ("load" matches "loads")
        pattern = rf"(?<!\w){re.escape(kw)}s?(?!\w)"
        hits = re.findall(pattern, text, flags=re.IGNORECASE)
        if hits:
            score += 1 + 0.1 * (len(hits) - 1)  # distinct keywords matter most
    return score


def retrieve(req: Requirement, pages: list[dict], top_k: int = 2) -> list[dict]:
    """Pick the pages the LLM should see for one requirement."""
    if req.scope == "all":
        return pages

    scored = [(_score(p["text"], req.keywords), p) for p in pages]
    scored = [s for s in scored if s[0] > 0]
    if not scored:
        return pages  # safe fallback: never send the model nothing

    scored.sort(key=lambda s: s[0], reverse=True)
    top = [p for _, p in scored[:top_k]]
    return sorted(top, key=lambda p: p["page"])