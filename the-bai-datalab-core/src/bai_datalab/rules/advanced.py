from __future__ import annotations

import re
import uuid

from bai_datalab.models import Finding, FindingSeverity, SourceAnchor, AnchorScope, DecisionType


def _id():
    return f"finding_{uuid.uuid4().hex[:10]}"


def _finding(rule_id, severity, concept, anchor, question, hints, evidence=None):
    return Finding(
        _id(), rule_id, severity, concept, anchor, question, hints, evidence or {}
    )


def _line_anchor(artifact: str, source: str, pattern: str, flags=0):
    m = re.search(pattern, source, flags)
    if not m:
        return None
    start = source.count("\n", 0, m.start()) + 1
    line = source.splitlines()[start - 1] if source.splitlines() else ""
    return SourceAnchor(artifact, start, start, line, AnchorScope.LINE)


def run_advanced_rules(decisions, source):
    """Higher-complexity deterministic checks for R and Python workflows.

    These are Socratic triggers, not automatic declarations that an analysis is wrong.
    They intentionally ask for justification/evidence when a complex modelling choice is
    detected.
    """
    findings = []
    models = [d for d in decisions if d.type == DecisionType.MODEL_DEFINITION]
    artifact = models[0].anchor.artifact if models else "script"
    lower = source.lower()

    for model in models:
        fn = str(model.payload.get("function") or "").lower()
        predictors = str(model.payload.get("predictors_expression") or "")
        family = str(model.payload.get("family") or "").lower()
        family_kind = str(model.payload.get("family_kind") or "").lower()

        # GLM family / link justification.
        if any(x in fn for x in ("glm", "logit", "probit")) or family:
            findings.append(_finding(
                "MODEL_GLM_FAMILY_LINK_001",
                FindingSeverity.UNDERSTANDING_CHECK,
                "distribution and link function",
                model.anchor,
                "Why is this response distribution and link function appropriate for the outcome and scientific question?",
                [
                    "Relate the outcome support (binary, count, positive continuous, etc.) to the distribution.",
                    "Explain what the link means for the scale on which effects are additive.",
                ],
                {"function": fn, "family": family or family_kind},
            ))

        # Random effects / mixed models.
        random_terms = re.findall(r"\([^()]*\|[^()]+\)", predictors)
        if random_terms or any(x in fn for x in ("lmer", "glmer", "mixedlm", "mixed")):
            findings.append(_finding(
                "MODEL_RANDOM_EFFECTS_001",
                FindingSeverity.UNDERSTANDING_CHECK,
                "multilevel structure",
                model.anchor,
                "What clustering or repeated-measures structure do the random effects represent, and why is it needed?",
                [
                    "Identify the grouping unit and which observations share that group.",
                    "Explain what dependence would be ignored by a single-level model.",
                ],
                {"random_terms": random_terms, "function": fn},
            ))
            if any("+" in term.split("|")[0] for term in random_terms) or "re_formula" in lower:
                findings.append(_finding(
                    "MODEL_RANDOM_SLOPE_001",
                    FindingSeverity.CAUTION,
                    "random slopes",
                    model.anchor,
                    "Why is this effect allowed to vary between groups, and is there enough within-group information to estimate that variation?",
                    [
                        "Distinguish variation in intercepts from variation in slopes.",
                        "Consider the number of groups and repeated observations within groups.",
                    ],
                    {"random_terms": random_terms},
                ))

        # High-order interactions.
        interactions = model.payload.get("interaction_terms") or []
        if any(term.count(":") >= 2 or term.count("*") >= 2 for term in interactions):
            findings.append(_finding(
                "MODEL_HIGH_ORDER_INTERACTION_001",
                FindingSeverity.CAUTION,
                "high-order interaction",
                model.anchor,
                "This model contains a three-way or higher interaction. How will you interpret it without treating lower-order effects as unconditional?",
                [
                    "Interpret the highest-order interaction first.",
                    "Use predicted values or marginal effects to communicate complex interactions.",
                ],
                {"interaction_terms": interactions},
            ))

        # Polynomial / spline / smooth terms.
        if re.search(r"\b(poly|ns|bs|s)\s*\(", predictors) or "**2" in predictors or "I(" in predictors:
            findings.append(_finding(
                "MODEL_NONLINEAR_TERM_001",
                FindingSeverity.UNDERSTANDING_CHECK,
                "nonlinear effects",
                model.anchor,
                "Why did you introduce this nonlinear term, and how did you assess whether its added flexibility is warranted?",
                [
                    "Compare the functional form with diagnostic/visual evidence.",
                    "Interpret the fitted shape rather than individual polynomial coefficients in isolation.",
                ],
                {"predictors": predictors},
            ))

        # GAM-specific smoothness.
        if "gam" in fn or re.search(r"\bs\s*\(", predictors):
            findings.append(_finding(
                "MODEL_GAM_SMOOTH_001",
                FindingSeverity.UNDERSTANDING_CHECK,
                "smooth effects",
                model.anchor,
                "How was smoothness controlled in this GAM, and what does the estimated smooth shape imply?",
                [
                    "Consider effective degrees of freedom or smoothing penalties.",
                    "Inspect the smooth with uncertainty rather than quoting one coefficient.",
                ],
                {"function": fn},
            ))

        # Survival.
        if any(x in fn for x in ("coxph", "cox", "phreg")) or "surv(" in lower:
            findings.append(_finding(
                "MODEL_SURVIVAL_001",
                FindingSeverity.CAUTION,
                "survival analysis",
                model.anchor,
                "How is censoring represented, and what assumptions are required for this survival-model interpretation?",
                [
                    "Distinguish event time from censoring time/status.",
                    "For Cox models, consider proportional hazards and informative censoring.",
                ],
                {"function": fn},
            ))

        # Ordinal / multinomial.
        if any(x in fn for x in ("polr", "orderedmodel", "ordinal")):
            findings.append(_finding(
                "MODEL_ORDINAL_001",
                FindingSeverity.CAUTION,
                "ordinal outcome modelling",
                model.anchor,
                "What ordering assumption does this model use, and how did you assess whether it is reasonable?",
                [
                    "Explain what the cut-points/thresholds represent.",
                    "If proportional odds is assumed, describe how you would assess it.",
                ],
                {"function": fn},
            ))
        if any(x in fn for x in ("multinom", "mnlogit", "multinomial")):
            findings.append(_finding(
                "MODEL_MULTINOMIAL_001",
                FindingSeverity.UNDERSTANDING_CHECK,
                "multinomial outcome modelling",
                model.anchor,
                "What is the reference outcome category, and how should coefficients for the other categories be interpreted?",
                [
                    "Each equation contrasts one category with the reference category.",
                    "Consider predicted probabilities for substantive interpretation.",
                ],
                {"function": fn},
            ))

        # Count models / overdispersion.
        if family_kind == "poisson" or "poisson" in family or "poisson" in fn:
            findings.append(_finding(
                "MODEL_COUNT_OVERDISPERSION_001",
                FindingSeverity.CAUTION,
                "count-model dispersion",
                model.anchor,
                "How did you assess whether the Poisson mean-variance assumption is adequate for these counts?",
                [
                    "Compare residual/deviance variation with what a Poisson model expects.",
                    "Consider overdispersion, zero inflation, or negative-binomial alternatives where appropriate.",
                ],
                {"family": family or family_kind},
            ))

    # Observation weights.
    a = _line_anchor(artifact, source, r"\b(weights\s*=|sample_weight\s*=|class_weight\s*=)")
    if a:
        findings.append(_finding(
            "MODEL_WEIGHTS_001", FindingSeverity.UNDERSTANDING_CHECK, "model weights", a,
            "What do these weights represent, and how do they change the estimand or fitting objective?",
            ["Identify whether they are sampling, frequency, precision, or class weights.",
             "Explain why treating weighted observations differently is justified."],
        ))

    # Offsets/exposure.
    a = _line_anchor(artifact, source, r"\b(offset\s*\(|offset\s*=|exposure\s*=)")
    if a:
        findings.append(_finding(
            "MODEL_OFFSET_001", FindingSeverity.UNDERSTANDING_CHECK, "offset/exposure", a,
            "Why is this term specified as an offset/exposure rather than estimated as an ordinary predictor?",
            ["Offsets usually encode known exposure with a fixed coefficient.",
             "State the rate/exposure interpretation implied by the offset."],
        ))

    # Regularisation.
    a = _line_anchor(artifact, source, r"\b(Ridge|Lasso|ElasticNet|glmnet|LogisticRegression\s*\()")
    if a and any(t in lower for t in ("ridge", "lasso", "elasticnet", "glmnet", "penalty=")):
        findings.append(_finding(
            "MODEL_REGULARIZATION_001", FindingSeverity.CAUTION, "regularisation", a,
            "Why is regularisation used here, and how was the penalty strength selected?",
            ["Describe the bias-variance trade-off.",
             "Penalty tuning should be based on validation/cross-validation rather than the final test set."],
        ))

    # Cross-validation.
    cv_pattern = r"\b(cross_val_score|cross_validate|KFold|StratifiedKFold|RepeatedKFold|cv\.glm|trainControl)\b"
    a = _line_anchor(artifact, source, cv_pattern)
    if a:
        findings.append(_finding(
            "MODEL_CROSS_VALIDATION_001", FindingSeverity.UNDERSTANDING_CHECK, "cross-validation", a,
            "How were the folds constructed, and were preprocessing and model selection repeated inside each training fold?",
            ["Keep validation observations out of every fitted preprocessing step.",
             "For classification, consider whether stratification/grouping/time order matters."],
        ))

    # Hyperparameter tuning.
    a = _line_anchor(artifact, source, r"\b(GridSearchCV|RandomizedSearchCV|BayesSearchCV|tune_grid|tune_bayes|caret::train)\b")
    if a:
        findings.append(_finding(
            "MODEL_HYPERPARAMETER_TUNING_001", FindingSeverity.CAUTION, "hyperparameter tuning", a,
            "Which data determined the hyperparameters, and what data remained untouched for final performance assessment?",
            ["Do not choose hyperparameters using the final test set.",
             "Nested validation may be needed when estimating performance after extensive tuning."],
        ))

    # Pipelines.
    a = _line_anchor(artifact, source, r"\b(Pipeline|make_pipeline|recipes?\s*\()")
    if a:
        findings.append(_finding(
            "MODEL_PIPELINE_001", FindingSeverity.UNDERSTANDING_CHECK, "analysis pipeline", a,
            "Which preprocessing operations are fitted inside this pipeline, and how does that affect leakage risk?",
            ["A well-constructed pipeline fits transformations using training data only.",
             "Check that feature selection and imputation are also inside resampling when needed."],
        ))

    # Imputation.
    a = _line_anchor(artifact, source, r"\b(SimpleImputer|KNNImputer|IterativeImputer|mice\s*\(|missForest|na\.omit\s*\(|dropna\s*\()")
    if a:
        findings.append(_finding(
            "MODEL_IMPUTATION_001", FindingSeverity.CAUTION, "missing-data handling", a,
            "What missing-data assumptions justify this strategy, and when were imputation parameters estimated relative to data splitting?",
            ["Distinguish deletion from single/multiple imputation.",
             "For predictive evaluation, estimate imputation from training data only."],
        ))

    # Feature selection before split -> leakage risk.
    selection_match = re.search(r"\b(SelectKBest|RFE|RFECV|stepAIC|step\s*\(|select_features|feature_selection)\b", source, re.I)
    split_match = re.search(r"\b(train_test_split|initial_split|createDataPartition)\b", source, re.I)
    if selection_match and split_match and selection_match.start() < split_match.start():
        a = _line_anchor(artifact, source, r"\b(SelectKBest|RFE|RFECV|stepAIC|step\s*\(|select_features|feature_selection)\b", re.I)
        findings.append(_finding(
            "MODEL_FEATURE_SELECTION_LEAKAGE_001", FindingSeverity.POTENTIAL_MODELLING_ISSUE,
            "feature-selection leakage", a,
            "Feature selection appears before the train/test split. Could test-set information influence which predictors were retained?",
            ["Feature selection is part of model fitting.",
             "Repeat selection inside training folds rather than once on the full dataset."],
        ))

    # Time-series split warning.
    if re.search(r"\b(TimeSeriesSplit|tsCV|rolling_origin)\b", source):
        a = _line_anchor(artifact, source, r"\b(TimeSeriesSplit|tsCV|rolling_origin)\b")
        findings.append(_finding(
            "MODEL_TIME_SERIES_VALIDATION_001", FindingSeverity.UNDERSTANDING_CHECK,
            "time-series validation", a,
            "How does this resampling scheme preserve temporal ordering and prevent future observations from informing the past?",
            ["Random folds may be inappropriate for temporally ordered data.",
             "Check the forecast horizon and whether lagged features are constructed without future information."],
        ))

    return findings
