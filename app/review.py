from datetime import datetime, timezone

from pydantic import BaseModel

VERDICTS = {"m": "met", "n": "not_met", "x": "missing", "c": "conflict"}


class Item(BaseModel):
    id: str
    rule: str
    verdict: str                 # the current (final, once reviewed) verdict
    model_verdict: str           # what the model originally said
    evidence_quote: str = ""
    page: int | None = None
    reasoning: str = ""
    status: str                  # auto | pending | approved | overridden
    flags: list[str] = []
    reviewer: str | None = None
    reviewed_at: str | None = None


def to_item(req, v) -> Item:
    r = v.result
    return Item(
        id=req.id, rule=req.rule, verdict=r.verdict, model_verdict=r.verdict,
        evidence_quote=r.evidence_quote, page=r.page, reasoning=r.reasoning,
        status="auto" if v.status == "auto" else "pending", flags=v.reasons,
    )


def review(items: list[Item], reviewer: str) -> None:
    for it in items:
        if it.status != "pending":
            continue
        print(f"\n{it.id}: {it.rule}")
        print(f"  model verdict: {it.model_verdict}   page: {it.page}")
        print(f"  quote:     {it.evidence_quote!r}")
        print(f"  reasoning: {it.reasoning}")
        print(f"  flagged:   {'; '.join(it.flags)}")
        while True:
            c = input("  [a]ccept model, [m]et [n]ot_met [x]missing [c]onflict, [s]kip > ").strip().lower()
            if c == "s":
                break
            if c == "a" or c in VERDICTS:
                if c == "a":
                    it.status = "approved"
                else:
                    it.verdict = VERDICTS[c]
                    it.status = "overridden"
                it.reviewer = reviewer
                it.reviewed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
                break
            print("  choose a, m, n, x, c or s")