import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def score(rows, expected):
    planted = [k for k, v in expected.items() if v["verdict"] != "met"]
    controls = [k for k, v in expected.items() if v["verdict"] == "met"]
    flagged = lambda v: v.result.verdict != "met" or v.status == "needs_review"
    return {
        "detected": sum(flagged(rows[k]) for k in planted),
        "planted": len(planted),
        "false_alarms": sum(rows[k].result.verdict != "met" for k in controls),
        "controls": len(controls),
        "exact": sum(rows[k].result.verdict == expected[k]["verdict"] for k in expected),
        "total": len(expected),
        # wrong verdicts that were auto-approved with no human review: the dangerous kind
        "silent_errors": sum(
            rows[k].status == "auto" and rows[k].result.verdict != expected[k]["verdict"]
            for k in expected
        ),
        "needs_review": sum(v.status == "needs_review" for v in rows.values()),
        "failed": sum(v.result.verdict == "failed" for v in rows.values()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--use-cache", action="store_true", help="reuse cached LLM results")
    args = ap.parse_args()
    if not args.use_cache:
        os.environ["LLM_CACHE"] = "0"

    from app.pipeline import run_pipeline  # imported after the cache flag is set

    expected = json.loads(Path("data/expected.json").read_text())
    scores, verdicts = [], []
    for n in range(1, args.runs + 1):
        rows = {req.id: v for req, v in run_pipeline()}
        verdicts.append({k: v.result.verdict for k, v in rows.items()})
        scores.append(score(rows, expected))
        print(f"run {n}: " + " ".join(f"{k}:{v}" for k, v in verdicts[-1].items()))

    def total(key):
        return sum(s[key] for s in scores)

    r = args.runs
    model = os.getenv("LLM_MODEL", "?")
    print(f"\nmodel: {model}   runs: {r}")
    print(f"detected:       {total('detected')}/{scores[0]['planted'] * r}")
    print(f"false alarms:   {total('false_alarms')}/{scores[0]['controls'] * r}")
    print(f"exact verdicts: {total('exact')}/{scores[0]['total'] * r}")
    print(f"silent errors:  {total('silent_errors')}  (wrong verdict approved with no review)")
    print(f"needs review:   {total('needs_review')} across {r} run(s)")
    print(f"failed:         {total('failed')}")
    print("\n| model | runs | detected | false alarms | exact | silent errors | sent to review |")
    print("|---|---|---|---|---|---|---|")
    print(
        f"| {model} | {r} | {total('detected')}/{scores[0]['planted'] * r} "
        f"| {total('false_alarms')}/{scores[0]['controls'] * r} "
        f"| {total('exact')}/{scores[0]['total'] * r} | {total('silent_errors')} "
        f"| {total('needs_review')} |"
    )

    Path("output").mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = Path("output") / f"eval-{stamp}.json"
    out.write_text(json.dumps({"model": model, "scores": scores, "verdicts": verdicts}, indent=2))
    print("\nsaved", out)


if __name__ == "__main__":
    main()