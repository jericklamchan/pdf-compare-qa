import html
from pathlib import Path

CSS = """body{font-family:system-ui,sans-serif;margin:2rem;max-width:1100px}
table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px 8px;vertical-align:top;text-align:left}
.banner{padding:10px;margin:12px 0;border-radius:6px}.draft{background:#fff3cd}.ok{background:#d1e7dd}
.met{color:#0a7d33}.not_met,.missing,.conflict{color:#b42318;font-weight:600}.failed{color:#888}"""


def _status_text(i) -> str:
    if i.status == "auto":
        return "Machine-verified"
    if i.status == "approved":
        return f"Approved by {i.reviewer}"
    if i.status == "overridden":
        return f"Overridden by {i.reviewer} (model said {i.model_verdict})"
    return "AWAITING REVIEW: " + "; ".join(i.flags)


def build_report(items, path="output/report.html", source="submission.pdf") -> str:
    e = html.escape
    pending = [i for i in items if i.status == "pending"]
    findings = [i for i in items if i.verdict != "met"]
    rows = sorted(items, key=lambda i: (i.status != "pending", i.verdict == "met", int(i.id[1:])))

    banner = (
        f'<div class="banner draft">DRAFT: {len(pending)} item(s) awaiting human review</div>'
        if pending else '<div class="banner ok">All items machine-verified or human-reviewed</div>'
    )
    body = "".join(
        f"<tr><td>{e(i.id)}</td><td>{e(i.rule)}</td>"
        f'<td class="{e(i.verdict)}">{e(i.verdict)}</td>'
        f"<td>{('&ldquo;' + e(i.evidence_quote) + '&rdquo; (p.' + str(i.page) + ')') if i.evidence_quote else '&mdash;'}</td>"
        f"<td>{e(i.reasoning)}</td><td>{e(_status_text(i))}</td></tr>"
        for i in rows
    )
    doc = (
        f"<!doctype html><meta charset='utf-8'><title>QA report</title><style>{CSS}</style>"
        f"<h1>QA report: {e(source)}</h1>{banner}"
        f"<p>{len(items)} requirements checked &middot; {len(findings)} findings &middot; "
        f"{len(items) - len(findings)} met &middot; {len(pending)} pending</p>"
        "<table><tr><th>ID</th><th>Requirement</th><th>Verdict</th><th>Evidence</th>"
        f"<th>Reasoning</th><th>Status</th></tr>{body}</table>"
    )
    Path(path).parent.mkdir(exist_ok=True)
    Path(path).write_text(doc, encoding="utf-8")
    return str(path)