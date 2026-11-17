import argparse
import logging

from app.pipeline import run_pipeline
from app.report import build_report
from app.review import review, to_item


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", default="data/submission.pdf")
    ap.add_argument("--reviewer")
    ap.add_argument("--no-review", action="store_true")
    args = ap.parse_args()
    if not args.no_review and not args.reviewer:
        ap.error("--reviewer is required unless --no-review is set")

    logging.basicConfig(level=logging.WARNING)
    items = [to_item(r, v) for r, v in run_pipeline(args.submission)]
    if not args.no_review:
        review(items, args.reviewer)
    print("report written to", build_report(items, source=args.submission))


if __name__ == "__main__":
    main()