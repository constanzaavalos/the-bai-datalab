from __future__ import annotations

import uuid

from bai_datalab.analysis import analyse_script
from bai_datalab.data_analysis import analyse_delimited_dataset
from bai_datalab.models import (
    AnalyticalDecision,
    AnchorScope,
    BundleAnalysisResult,
    BundleArtifact,
    DecisionType,
    EvidenceItem,
    Finding,
    FindingSeverity,
    SourceAnchor,
)
from bai_datalab.output_parser import parse_model_output


def _id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _dataset_findings(metadata, anchor):
    findings = []

    for name, info in metadata.get("variables", {}).items():
        if info.get("constant"):
            findings.append(
                Finding(
                    _id("finding"),
                    "DATA_CONSTANT_VARIABLE_001",
                    FindingSeverity.POTENTIAL_MODELLING_ISSUE,
                    "constant variable",
                    anchor,
                    f"`{name}` has no observed variation. What role can it play in the model?",
                    ["A predictor without variation cannot explain variation.", "Check whether this reflects filtering or coding."],
                    {"variable": name, **info},
                )
            )

        if info.get("missing_pct", 0) >= 30:
            findings.append(
                Finding(
                    _id("finding"),
                    "DATA_HIGH_MISSINGNESS_001",
                    FindingSeverity.CAUTION,
                    "missing data",
                    anchor,
                    f"`{name}` has {info['missing_pct']}% missing values. How did you decide how to handle it?",
                    ["Identify whether missingness is structural or substantive.", "Consider the effect on sample size and representativeness."],
                    {"variable": name, **info},
                )
            )

        if info.get("binary") and info.get("minority_pct", 100) < 15:
            findings.append(
                Finding(
                    _id("finding"),
                    "DATA_CLASS_IMBALANCE_001",
                    FindingSeverity.CAUTION,
                    "class imbalance",
                    anchor,
                    f"`{name}` has a minority class of only {info['minority_pct']}%. How would that affect evaluation if this variable is an outcome?",
                    ["Accuracy may be misleading.", "Use class-sensitive evaluation metrics."],
                    {"variable": name, **info},
                )
            )

    return findings


def _link_evidence(findings, decisions, datasets, outputs):
    model_decisions = [d for d in decisions if d.type == DecisionType.MODEL_DEFINITION]

    dataset_evidence = []
    for name, meta in datasets.items():
        dataset_evidence.append(
            EvidenceItem(
                evidence_id=_id("evidence"),
                evidence_type="dataset",
                artifact=name,
                label=f"{meta.get('rows', 0)} rows · {meta.get('columns', 0)} columns · {meta.get('missing_pct', 0)}% missing",
                payload=meta,
            )
        )

    output_evidence = []
    for name, meta in outputs.items():
        label_bits = []
        for k in ("r_squared", "adjusted_r_squared", "aic", "bic", "auc"):
            if k in meta:
                label_bits.append(f"{k}={meta[k]}")
        output_evidence.append(
            EvidenceItem(
                evidence_id=_id("evidence"),
                evidence_type="model_output",
                artifact=name,
                label=" · ".join(label_bits) if label_bits else "Parsed model output",
                payload=meta,
            )
        )

    for finding in findings:
        # Attach dataset evidence to code-anchored model findings.
        if model_decisions:
            finding.related_evidence.extend(dataset_evidence[:1])
        if finding.concept in {
            "response transformation", "interaction effects",
            "model diagnostics", "classification evaluation"
        }:
            finding.related_evidence.extend(output_evidence[:1])


def analyse_bundle(artifacts: list[BundleArtifact]) -> BundleAnalysisResult:
    decisions = []
    findings = []
    datasets = {}
    outputs = {}

    for artifact in artifacts:
        lower = artifact.name.lower()

        if lower.endswith((".r", ".py")):
            source = artifact.content.decode("utf-8", errors="replace")
            result = analyse_script(artifact.name, source)
            decisions.extend(result.decisions)
            findings.extend(result.findings)

        elif lower.endswith((".csv", ".tsv")):
            metadata = analyse_delimited_dataset(artifact.name, artifact.content)
            datasets[artifact.name] = metadata

            anchor = SourceAnchor(
                artifact=artifact.name,
                line_start=1,
                line_end=1,
                excerpt="Dataset profile",
                scope=AnchorScope.ARTIFACT,
            )

            decisions.append(
                AnalyticalDecision(
                    _id("decision"),
                    DecisionType.DATASET_SUMMARY,
                    anchor,
                    "dataset structure",
                    metadata,
                )
            )
            findings.extend(_dataset_findings(metadata, anchor))

        elif lower.endswith((".txt", ".out", ".log")):
            metadata = parse_model_output(artifact.name, artifact.content)
            outputs[artifact.name] = metadata

            anchor = SourceAnchor(
                artifact=artifact.name,
                line_start=1,
                line_end=1,
                excerpt="Model output",
                scope=AnchorScope.ARTIFACT,
            )

            decisions.append(
                AnalyticalDecision(
                    _id("decision"),
                    DecisionType.MODEL_OUTPUT,
                    anchor,
                    "model output",
                    metadata,
                )
            )

            if metadata.get("has_coefficients") and not metadata.get("has_residual_summary"):
                findings.append(
                    Finding(
                        _id("finding"),
                        "OUTPUT_DIAGNOSTICS_001",
                        FindingSeverity.CAUTION,
                        "model diagnostics",
                        anchor,
                        "The output contains coefficients but no residual summary. What other evidence would you inspect before interpreting the model?",
                        ["Coefficient significance does not establish model adequacy.", "Inspect residual, influence or calibration evidence."],
                        metadata,
                    )
                )

    # Cross-artifact code/data consistency
    if datasets:
        dataset = next(iter(datasets.values()))
        columns = set(dataset.get("column_names", []))

        for model in [d for d in decisions if d.type == DecisionType.MODEL_DEFINITION]:
            variables = []
            if model.payload.get("response_variable"):
                variables.append(model.payload["response_variable"])
            variables.extend(model.payload.get("predictor_variables", []))

            missing = sorted({
                v for v in variables
                if v and v not in columns and not v.startswith("np.")
            })

            if missing:
                findings.append(
                    Finding(
                        _id("finding"),
                        "BUNDLE_VARIABLE_MISMATCH_001",
                        FindingSeverity.POTENTIAL_MODELLING_ISSUE,
                        "code-data consistency",
                        model.anchor,
                        "Some variables referenced by the model are absent from the uploaded dataset. Where were they created or renamed?",
                        ["Check recoding, joins and feature engineering.", "Confirm that the uploaded dataset is the version used by the script."],
                        {"missing_variables": missing},
                    )
                )

    _link_evidence(findings, decisions, datasets, outputs)

    return BundleAnalysisResult(
        artifacts=artifacts,
        decisions=decisions,
        findings=findings,
        dataset_metadata=datasets,
        output_metadata=outputs,
    )
