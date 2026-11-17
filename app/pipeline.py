from app.check import check_requirement
from app.extract import extract_pages
from app.models import load_requirements
from app.retrieve import retrieve
from app.verify import verify


def run_pipeline(submission: str = "data/submission.pdf"):
    """Return [(Requirement, Verified)] for every requirement."""
    pages = extract_pages(submission)
    out = []
    for req in load_requirements():
        result = check_requirement(req, retrieve(req, pages))
        out.append((req, verify(req, result, pages)))
    return out