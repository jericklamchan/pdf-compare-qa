import re
import unicodedata
from typing import Literal

from pydantic import BaseModel

from app.check import CheckResult
from app.models import Requirement

CONF_THRESHOLD = 0.7
NUM_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s*([A-Za-z]+)")


class Verified(BaseModel):
    result: CheckResult
    status: Literal["auto", "needs_review"]
    reasons: list[str] = []


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    for a, b in (("\u2019", "'"), ("\u2018", "'"), ("\u201c", '"'), ("\u201d", '"')):
        s = s.replace(a, b)
    return " ".join(s.split()).casefold()


def numeric_verdict(req: Requirement, quote: str) -> str | None:
    """Decide met/not_met in code from the quoted text. None = can't tell."""
    spec = req.numeric
    if spec is None:
        return None
    found = [(float(v), u) for v, u in NUM_UNIT.findall(quote)]
    if spec.allowed_units:
        units = [u for _, u in found]
        if not units:
            return None
        return "met" if all(u in spec.allowed_units for u in units) else "not_met"
    values = [v for v, u in found if u == spec.unit]
    if not values:
        return None
    v = values[0]
    ok = {"eq": v == spec.value, "le": v <= spec.value, "ge": v >= spec.value}[spec.op]
    return "met" if ok else "not_met"


def verify(req: Requirement, result: CheckResult, pages: list[dict]) -> Verified:
    reasons: list[str] = []
    by_page = {p["page"]: p["text"] for p in pages}

    if result.verdict == "failed":
        reasons.append("model gave no valid output")

    elif result.verdict == "missing":
        # the model says the content is absent: look for its keywords anyway
        for p in pages:
            text = _norm(p["text"])
            for kw in req.keywords:
                if re.search(rf"(?<!\w){re.escape(_norm(kw))}s?(?!\w)", text):
                    reasons.append(f"called missing, but '{kw}' appears on page {p['page']}")
                    break

    else:  # met / not_met / conflict need real evidence
        quote = _norm(result.evidence_quote)
        if not quote or result.page not in by_page:
            reasons.append("no usable quote or page")
        elif quote not in _norm(by_page[result.page]):
            reasons.append(f"quote not found on cited page {result.page}")
        else:
            code = numeric_verdict(req, result.evidence_quote)
            if code and result.verdict in ("met", "not_met") and code != result.verdict:
                reasons.append(f"code says {code}, model says {result.verdict}")

    if result.confidence < CONF_THRESHOLD and result.verdict != "failed":
        reasons.append(f"low confidence ({result.confidence})")

    return Verified(result=result, status="needs_review" if reasons else "auto", reasons=reasons)


if __name__ == "__main__":
    import logging
    from app.check import check_requirement
    from app.extract import extract_pages
    from app.models import load_requirements
    from app.retrieve import retrieve

    logging.basicConfig(level=logging.WARNING)
    pages = extract_pages("data/submission.pdf")
    for r in load_requirements():
        v = verify(r, check_requirement(r, retrieve(r, pages)), pages)
        print(f"{r.id:4} {v.result.verdict:9} {v.status:13} {'; '.join(v.reasons)}")