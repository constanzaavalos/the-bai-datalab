from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DecisionType(str, Enum):
    MODEL_DEFINITION = "model_definition"
    RESPONSE_TRANSFORMATION = "response_transformation"
    INTERACTION = "interaction"
    MODEL_COMPARISON = "model_comparison"
    MODEL_SELECTION = "model_selection"
    DATASET_SUMMARY = "dataset_summary"
    MODEL_OUTPUT = "model_output"
    TRAIN_TEST_SPLIT = "train_test_split"
    CLASSIFICATION_METRIC = "classification_metric"
    DIAGNOSTIC_CHECK = "diagnostic_check"
    PREPROCESSING = "preprocessing"


class FindingSeverity(str, Enum):
    UNDERSTANDING_CHECK = "understanding_check"
    CAUTION = "caution"
    POTENTIAL_MODELLING_ISSUE = "potential_modelling_issue"


class AnchorScope(str, Enum):
    LINE = "line"
    BLOCK = "block"
    ARTIFACT = "artifact"


@dataclass(frozen=True)
class SourceAnchor:
    artifact: str
    line_start: int = 1
    line_end: int = 1
    excerpt: str = ""
    scope: AnchorScope = AnchorScope.LINE


@dataclass
class AnalyticalDecision:
    id: str
    type: DecisionType
    anchor: SourceAnchor
    concept: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceItem:
    evidence_id: str
    evidence_type: str
    artifact: str
    label: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class Finding:
    id: str
    rule_id: str
    severity: FindingSeverity
    concept: str
    anchor: SourceAnchor
    question: str
    hints: list[str]
    evidence: dict[str, Any] = field(default_factory=dict)
    related_evidence: list[EvidenceItem] = field(default_factory=list)


@dataclass
class AnalysisResult:
    artifact: str
    decisions: list[AnalyticalDecision]
    findings: list[Finding]


@dataclass
class BundleArtifact:
    name: str
    kind: str
    content: bytes


@dataclass
class BundleAnalysisResult:
    artifacts: list[BundleArtifact]
    decisions: list[AnalyticalDecision]
    findings: list[Finding]
    dataset_metadata: dict[str, Any] = field(default_factory=dict)
    output_metadata: dict[str, Any] = field(default_factory=dict)
