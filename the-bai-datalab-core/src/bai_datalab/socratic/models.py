from dataclasses import dataclass
from enum import Enum


class SocraticStatus(str, Enum):
    RESOLVED = "resolved"
    FOLLOW_UP = "follow_up"
    HINT = "hint"


@dataclass
class StudentResponse:
    finding_id: str
    text: str
    hint_level: int = 0
    attempts: int = 1


@dataclass
class SocraticOutcome:
    finding_id: str
    status: SocraticStatus
    message: str
    hint_level: int
    evidence_terms_found: list[str]
    evidence_terms_missing: list[str]
    score: float
