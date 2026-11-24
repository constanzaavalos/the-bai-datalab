import re
import uuid

from .advanced import run_advanced_rules

from bai_datalab.models import (
    DecisionType,
    Finding,
    FindingSeverity,
)


def _id():
    return f"finding_{uuid.uuid4().hex[:10]}"


def _finding(rule_id, severity, concept, anchor, question, hints, evidence):
    return Finding(
        _id(),
        rule_id,
        severity,
        concept,
        anchor,
        question,
        hints,
        evidence,
    )


def _classification_models(decisions):
    return [
        d for d in decisions
        if d.type == DecisionType.MODEL_DEFINITION
        and d.payload.get("family_kind") == "binomial"
    ]


def run_rules(decisions, source):
    findings = []

    models = [
        d for d in decisions
        if d.type == DecisionType.MODEL_DEFINITION
    ]

    response_by_model = {
        d.payload.get("object"): d.payload.get("response_expression")
        for d in models
    }

    diagnostics = {
        d.payload.get("diagnostic")
        for d in decisions
        if d.type == DecisionType.DIAGNOSTIC_CHECK
    }

    classification_metrics = {
        d.payload.get("metric_function")
        for d in decisions
        if d.type == DecisionType.CLASSIFICATION_METRIC
    }

    split_present = any(
        d.type == DecisionType.TRAIN_TEST_SPLIT
        for d in decisions
    )

    # 1. Response transformations
    for d in decisions:
        if d.type == DecisionType.RESPONSE_TRANSFORMATION:
            findings.append(
                _finding(
                    "LM_LOG_RESPONSE_001",
                    FindingSeverity.UNDERSTANDING_CHECK,
                    "response transformation",
                    d.anchor,
                    "Why did you transform the response here? What diagnostic evidence supported that choice?",
                    [
                        "Compare the response and residuals before and after transformation.",
                        "Which assumption or modelling objective were you trying to improve?",
                    ],
                    d.payload,
                )
            )

    # 2. Interactions
    for d in decisions:
        if d.type == DecisionType.INTERACTION:
            findings.append(
                _finding(
                    "LM_INTERACTION_001",
                    FindingSeverity.UNDERSTANDING_CHECK,
                    "interaction effects",
                    d.anchor,
                    "How does this interaction change the interpretation of the corresponding main effects?",
                    [
                        "Main effects become conditional when an interaction is present.",
                        "At what value of the interacting variable is the main effect interpreted?",
                    ],
                    d.payload,
                )
            )

    # 3. AIC comparison
    for d in decisions:
        if d.type != DecisionType.MODEL_COMPARISON:
            continue

        ys = {
            response_by_model.get(model)
            for model in d.payload.get("models", [])
            if response_by_model.get(model)
        }

        severity = (
            FindingSeverity.POTENTIAL_MODELLING_ISSUE
            if len(ys) > 1
            else FindingSeverity.UNDERSTANDING_CHECK
        )

        findings.append(
            _finding(
                "MODEL_AIC_001",
                severity,
                "AIC model comparison",
                d.anchor,
                "Are these AIC values directly comparable, and what must remain comparable for the comparison to be meaningful?",
                [
                    "AIC depends on the fitted likelihood and model complexity.",
                    "Check whether the response is represented on the same scale.",
                ],
                {"models": d.payload.get("models", []), "responses": list(ys)},
            )
        )

    # 4. Stepwise
    for d in decisions:
        if d.type == DecisionType.MODEL_SELECTION:
            findings.append(
                _finding(
                    "MODEL_STEPWISE_001",
                    FindingSeverity.CAUTION,
                    "automated model selection",
                    d.anchor,
                    "Why did you use automated model selection, and how did you assess its stability?",
                    [
                        "Consider uncertainty introduced by data-driven selection.",
                        "What role could substantive knowledge play instead?",
                    ],
                    d.payload,
                )
            )

    # 5. Missing diagnostics
    generic_diagnostic_present = any(
        token in source
        for token in (
            "plot(", "residuals(", "rstandard(", "rstudent(",
            "qqnorm(", "qqline(", "bptest(", "vif(", "check_model("
        )
    )

    if models and not diagnostics and not generic_diagnostic_present:
        d = models[-1]
        findings.append(
            _finding(
                "LM_DIAGNOSTICS_001",
                FindingSeverity.CAUTION,
                "model diagnostics",
                d.anchor,
                "What diagnostic evidence did you use to assess whether this model's assumptions were reasonable?",
                [
                    "Think beyond p-values.",
                    "Which residual, influence or variance diagnostics are relevant?",
                ],
                {"model_count": len(models)},
            )
        )

    # 6. Multicollinearity / VIF
    if models and "vif" not in diagnostics:
        for d in models:
            predictors = d.payload.get("predictors_expression") or ""
            predictor_count = len([
                t for t in re.split(r"\s*\+\s*", predictors)
                if t.strip()
            ])

            if predictor_count >= 3:
                findings.append(
                    _finding(
                        "LM_MULTICOLLINEARITY_001",
                        FindingSeverity.CAUTION,
                        "multicollinearity",
                        d.anchor,
                        "This model contains several predictors. How did you assess whether multicollinearity could affect coefficient stability?",
                        [
                            "Consider correlations among predictors and variance inflation.",
                            "Would unstable coefficients change how you interpret the model?",
                        ],
                        {
                            "predictor_count": predictor_count,
                            "predictors_expression": predictors,
                        },
                    )
                )

    # 7. Heteroscedasticity
    if models and "bptest" not in diagnostics and not generic_diagnostic_present:
        for d in models:
            if d.payload.get("family_kind") in {None, "gaussian"}:
                findings.append(
                    _finding(
                        "LM_HETEROSCEDASTICITY_001",
                        FindingSeverity.CAUTION,
                        "heteroscedasticity",
                        d.anchor,
                        "How did you assess whether the residual variance was approximately constant across fitted values?",
                        [
                            "Inspect residuals versus fitted values.",
                            "Consider whether a formal heteroscedasticity check would add evidence.",
                        ],
                        d.payload,
                    )
                )

    # 8. Logistic regression evaluation
    logistic = _classification_models(decisions)

    if logistic and not classification_metrics:
        for d in logistic:
            findings.append(
                _finding(
                    "GLM_CLASSIFICATION_METRICS_001",
                    FindingSeverity.CAUTION,
                    "classification evaluation",
                    d.anchor,
                    "This is a binomial model. How did you evaluate predictive performance beyond coefficient significance?",
                    [
                        "Consider sensitivity, specificity, precision, recall, ROC or calibration.",
                        "What decision threshold did you use, and why?",
                    ],
                    d.payload,
                )
            )

    # 9. Train/test split
    if logistic and not split_present:
        for d in logistic:
            findings.append(
                _finding(
                    "ML_TRAIN_TEST_SPLIT_001",
                    FindingSeverity.POTENTIAL_MODELLING_ISSUE,
                    "data partitioning",
                    d.anchor,
                    "I cannot see evidence of a train/test split. How did you ensure that predictive performance was evaluated on unseen data?",
                    [
                        "Performance measured on training data can be optimistic.",
                        "Think about validation, cross-validation, or a held-out test set.",
                    ],
                    d.payload,
                )
            )

    # 10. Potential data leakage
    leakage_tokens = (
        "scale(",
        "normalize(",
        "preProcess(",
        "recipes::step_normalize(",
        "impute",
        "mice(",
    )

    if split_present:
        split_line = min(
            d.anchor.line_start
            for d in decisions
            if d.type == DecisionType.TRAIN_TEST_SPLIT
        )

        for line_no, line in enumerate(source.splitlines(), 1):
            if line_no >= split_line:
                continue

            if any(token in line for token in leakage_tokens):
                anchor = models[0].anchor if models else decisions[0].anchor
                findings.append(
                    _finding(
                        "ML_DATA_LEAKAGE_001",
                        FindingSeverity.POTENTIAL_MODELLING_ISSUE,
                        "data leakage",
                        anchor,
                        "A preprocessing operation appears before the data split. Was that transformation estimated using the full dataset?",
                        [
                            "Preprocessing parameters should usually be learned from training data only.",
                            "Ask whether information from the test set could influence the fitted transformation.",
                        ],
                        {"line": line_no, "code": line.strip()},
                    )
                )
                break

    # 10b. Python preprocessing leakage detected from parsed decisions
    preprocessing = [
        d for d in decisions
        if d.type == DecisionType.PREPROCESSING
    ]

    if split_present and preprocessing:
        split_line = min(
            d.anchor.line_start
            for d in decisions
            if d.type == DecisionType.TRAIN_TEST_SPLIT
        )
        early = [d for d in preprocessing if d.anchor.line_start < split_line]
        if early:
            d = early[0]
            findings.append(
                _finding(
                    "DATA_LEAKAGE_001",
                    FindingSeverity.POTENTIAL_MODELLING_ISSUE,
                    "data leakage",
                    d.anchor,
                    "Preprocessing appears before the train/test split. Were preprocessing parameters learned from the full dataset?",
                    [
                        "Fit preprocessing steps using training data only.",
                        "Check whether test-set information influenced scaling or imputation.",
                    ],
                    d.payload,
                )
            )

    # 11. Class imbalance heuristic based on common code patterns
    imbalance_markers = (
        "table(",
        "prop.table(",
        "class.weights",
        "weights=",
        "smote",
        "upsample",
        "downsample",
    )

    if logistic and not any(marker.lower() in source.lower() for marker in imbalance_markers):
        d = logistic[0]
        findings.append(
            _finding(
                "GLM_CLASS_IMBALANCE_001",
                FindingSeverity.UNDERSTANDING_CHECK,
                "class imbalance",
                d.anchor,
                "How did you check whether the outcome classes were imbalanced, and how would imbalance affect your evaluation metrics?",
                [
                    "Accuracy can be misleading when one class dominates.",
                    "Compare class frequencies before choosing metrics or resampling strategies.",
                ],
                d.payload,
            )
        )

    findings.extend(run_advanced_rules(decisions, source))

    # De-duplicate exact rule/anchor combinations so overlapping parsers do not
    # create repeated cards.
    unique = {}
    for finding in findings:
        key = (finding.rule_id, finding.anchor.artifact, finding.anchor.line_start, finding.anchor.line_end)
        unique[key] = finding
    findings = list(unique.values())

    return sorted(
        findings,
        key=lambda f: (
            f.anchor.artifact,
            f.anchor.line_start,
            f.rule_id,
        ),
    )
