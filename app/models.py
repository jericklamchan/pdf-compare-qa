import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel


class NumericSpec(BaseModel):
    op: Literal["eq", "le", "ge"] = "eq"
    value: float | None = None
    unit: str | None = None
    allowed_units: list[str] = []


class Requirement(BaseModel):
    id: str
    rule: str
    check_type: Literal["presence", "numeric", "consistency"]
    scope: Literal["relevant", "all"] = "relevant"
    keywords: list[str]
    numeric: NumericSpec | None = None


def load_requirements(path: str | Path = "data/requirements.json") -> list[Requirement]:
    data = json.loads(Path(path).read_text())
    return [Requirement.model_validate(r) for r in data]