from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class Strictness(str, Enum):
    SUPPORTIVE = "supportive"
    STANDARD = "standard"
    RIGOROUS = "rigorous"


class Misconception(str, Enum):
    FIT_EQUALS_VALIDITY = "fit_equals_validity"
    SIGNIFICANCE_EQUALS_IMPORTANCE = "significance_equals_importance"
    MAIN_EFFECT_UNCONDITIONAL = "main_effect_unconditional"
    ACCURACY_IS_ENOUGH = "accuracy_is_enough"
    TRAINING_PERFORMANCE_IS_GENERALISATION = "training_performance_is_generalisation"
    PREPROCESSING_BEFORE_SPLIT_IS_SAFE = "preprocessing_before_split_is_safe"
    TRANSFORMATION_WITHOUT_DIAGNOSTIC = "transformation_without_diagnostic"
    NONE = "none"


@dataclass
class AttemptRecord:
    attempt_number: int
    text: str
    status: str
    score: float
    hint_level: int
    misconception: Misconception = Misconception.NONE


@dataclass
class PedagogicalState:
    finding_id: str
    attempts: list[AttemptRecord] = field(default_factory=list)
    resolved: bool = False
    strictness: Strictness = Strictness.STANDARD
