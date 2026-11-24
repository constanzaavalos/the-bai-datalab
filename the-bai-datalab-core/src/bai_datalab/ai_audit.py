from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class AuditVerdict(str, Enum):
    ACCEPT = "accept"
    CHALLENGE = "challenge"
    MORE_EVIDENCE = "more_evidence"


class AuditStatus(str, Enum):
    RETRY = "retry"
    DEVELOP = "develop"
    RESOLVED = "resolved"


@dataclass(frozen=True)
class AIAuditCase:
    case_id: str
    title: str
    difficulty: str
    domain: str
    scenario: str
    ai_advice: str
    preferred_verdict: AuditVerdict
    key_terms: tuple[str, ...]
    evidence_terms: tuple[str, ...]
    hints: tuple[str, ...]
    rationale: str


@dataclass
class AuditEvaluation:
    status: AuditStatus
    score: float
    verdict_correct: bool
    key_terms_found: list[str]
    evidence_terms_found: list[str]
    feedback: str
    next_hint: str


CASES: tuple[AIAuditCase, ...] = (
    AIAuditCase(
        case_id="SIG_DROP",
        title="Remove all non-significant predictors",
        difficulty="Foundation",
        domain="Regression",
        scenario=(
            "A multiple regression is being used for explanation and prediction. "
            "Several predictors have p-values above 0.05, but some are known confounders."
        ),
        ai_advice=(
            "Remove every predictor with p > 0.05. Non-significant variables do not contribute "
            "useful information and will only make the model worse."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("confound", "prediction", "uncertainty", "effect", "selection", "bias"),
        evidence_terms=("cross-validation", "substantive", "domain", "confidence interval", "aic", "validation"),
        hints=(
            "Does a p-value answer the same question as predictive usefulness or confounding control?",
            "Could removing a non-significant confounder change other coefficient estimates?",
            "Model selection should depend on the modelling objective, not a universal p-value rule.",
        ),
        rationale="Statistical significance is not equivalent to predictive or causal relevance.",
    ),
    AIAuditCase(
        case_id="HIGH_R2_GOOD",
        title="R-squared proves the model is good",
        difficulty="Foundation",
        domain="Regression",
        scenario=(
            "A model reports R² = 0.94 on the training data. No residual diagnostics or external validation are shown."
        ),
        ai_advice=(
            "An R-squared of 0.94 proves that the model is excellent, so further diagnostics are unnecessary."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("diagnostic", "residual", "overfit", "general", "assumption", "validation"),
        evidence_terms=("test", "cross-validation", "residual plot", "out-of-sample", "influence"),
        hints=(
            "What does R² measure—and what does it not measure?",
            "Could a badly specified model still have a high R²?",
            "Separate in-sample fit from model adequacy and generalisation.",
        ),
        rationale="High in-sample fit does not establish valid assumptions or generalisation.",
    ),
    AIAuditCase(
        case_id="IMBALANCE_ACCURACY",
        title="Accuracy is enough",
        difficulty="Intermediate",
        domain="Classification",
        scenario=(
            "A classifier predicts a rare disease with prevalence 4%. It reports 96% accuracy."
        ),
        ai_advice=(
            "The classifier is highly reliable because it achieves 96% accuracy."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("imbalance", "minority", "prevalence", "sensitivity", "recall", "specificity", "precision"),
        evidence_terms=("confusion matrix", "pr-auc", "roc", "calibration", "f1"),
        hints=(
            "What accuracy would a model achieve by predicting the majority class every time?",
            "Which metric tells you whether rare positive cases are actually detected?",
            "Evaluate minority-class performance explicitly.",
        ),
        rationale="Accuracy can be misleading under strong class imbalance.",
    ),
    AIAuditCase(
        case_id="LOG_TRANSFORM",
        title="Use logs because fit improved",
        difficulty="Intermediate",
        domain="Regression",
        scenario=(
            "A student compares a raw-response linear model with a log-response model. "
            "The log model has a higher R²."
        ),
        ai_advice=(
            "Use the log-transformed model because its R-squared is higher. That proves the transformation is better."
        ),
        preferred_verdict=AuditVerdict.MORE_EVIDENCE,
        key_terms=("transformation", "residual", "variance", "skew", "scale", "interpret"),
        evidence_terms=("residual plot", "diagnostic", "distribution", "prediction", "assumption"),
        hints=(
            "Can R² from different response scales always be compared directly?",
            "What diagnostic evidence would justify a transformation?",
            "Think about both assumptions and interpretation after transformation.",
        ),
        rationale="A transformation should be justified by diagnostics and modelling goals; fit summaries alone are insufficient.",
    ),
    AIAuditCase(
        case_id="AIC_SCALE",
        title="The smallest AIC always wins",
        difficulty="Advanced",
        domain="Model comparison",
        scenario=(
            "Model A predicts y. Model B predicts log(y). AIC values are 820 and 140 respectively."
        ),
        ai_advice=(
            "Choose Model B because 140 is much smaller than 820. AIC values are always directly comparable."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("likelihood", "response", "scale", "comparable", "transformation"),
        evidence_terms=("same response", "likelihood", "jacobian", "prediction scale"),
        hints=(
            "What exactly is the likelihood defined for in each model?",
            "Are the two AIC values based on the same observed response representation?",
            "Information criteria require comparable likelihood targets.",
        ),
        rationale="AIC comparisons can be invalid across differently represented response variables.",
    ),
    AIAuditCase(
        case_id="RANDOM_EFFECTS",
        title="Ignore clustering if ICC is small",
        difficulty="Advanced",
        domain="Multilevel modelling",
        scenario=(
            "Students are nested within schools. The estimated ICC is modest, but inference concerns school-level variation and treatment effects."
        ),
        ai_advice=(
            "The ICC is small, so you can ignore schools and fit an ordinary regression because clustering will not matter."
        ),
        preferred_verdict=AuditVerdict.MORE_EVIDENCE,
        key_terms=("cluster", "school", "dependence", "icc", "standard error", "random"),
        evidence_terms=("design", "cluster size", "random effect", "robust", "likelihood", "treatment"),
        hints=(
            "Does a small ICC automatically imply negligible design effects?",
            "How do cluster size and the inferential target matter?",
            "The decision should consider dependence structure, not ICC alone.",
        ),
        rationale="Ignoring clustering may still distort uncertainty or target the wrong variance structure.",
    ),
    AIAuditCase(
        case_id="CALIBRATION_AUC",
        title="Higher AUC means better probabilities",
        difficulty="Advanced",
        domain="Classification",
        scenario=(
            "Two models have ROC-AUC 0.91 and 0.88. The second has much better calibration and Brier score."
        ),
        ai_advice=(
            "Model 1 is unquestionably better because it has the larger ROC-AUC, so calibration does not matter."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("calibr", "probability", "brier", "discrimination", "auc", "decision"),
        evidence_terms=("reliability", "calibration plot", "threshold", "risk"),
        hints=(
            "Does ROC-AUC assess absolute probability accuracy?",
            "If probabilities will be communicated or used for decisions, what else matters?",
            "Discrimination and calibration measure different properties.",
        ),
        rationale="AUC measures ranking/discrimination, not probability calibration.",
    ),
    AIAuditCase(
        case_id="PIPELINE_SAFE",
        title="Scaling before every fold is leakage",
        difficulty="Advanced",
        domain="Machine learning",
        scenario=(
            "A scikit-learn Pipeline contains imputation, StandardScaler and LogisticRegression, "
            "and the entire pipeline is passed to cross_val_score."
        ),
        ai_advice=(
            "This definitely leaks information because scaling happens before model fitting."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("pipeline", "fold", "training fold", "cross-validation", "fit"),
        evidence_terms=("pipeline", "within fold", "validation fold", "transform"),
        hints=(
            "Distinguish code order from resampling execution order.",
            "When does scikit-learn fit each pipeline step inside cross-validation?",
            "Preprocessing is safe when learned only from each training fold.",
        ),
        rationale="A correctly resampled pipeline fits preprocessing separately within training folds.",
    ),
    AIAuditCase(
        case_id="OOD_CONFIDENCE",
        title="More training data guarantees certainty everywhere",
        difficulty="Expert",
        domain="Uncertainty",
        scenario=(
            "A model has millions of training examples concentrated in one operating region. "
            "It is now used far outside that region."
        ),
        ai_advice=(
            "Because the training sample is enormous, epistemic uncertainty is effectively zero everywhere."
        ),
        preferred_verdict=AuditVerdict.CHALLENGE,
        key_terms=("epistemic", "domain", "out-of-distribution", "extrapolat", "coverage", "support"),
        evidence_terms=("training domain", "distance", "shift", "uncertainty"),
        hints=(
            "Does sample size in one region guarantee knowledge in another region?",
            "Think about support of the training distribution.",
            "Large n reduces sampling uncertainty within represented regions, not structural/domain uncertainty everywhere.",
        ),
        rationale="Large sample size does not remove epistemic uncertainty under extrapolation or domain shift.",
    ),
    AIAuditCase(
        case_id="AI_CAUTION_CORRECT",
        title="The AI refuses to overclaim",
        difficulty="Expert",
        domain="Responsible statistical AI",
        scenario=(
            "A student asks an AI whether a significant association in observational data proves a causal effect."
        ),
        ai_advice=(
            "No. Statistical significance alone does not establish causality. I would need to understand the study design, "
            "confounding structure, temporal ordering, identification assumptions and sensitivity to alternative explanations."
        ),
        preferred_verdict=AuditVerdict.ACCEPT,
        key_terms=("causal", "confound", "design", "assumption", "observational", "identification"),
        evidence_terms=("sensitivity", "temporal", "dag", "random", "design"),
        hints=(
            "Not every AI answer is wrong.",
            "Does the response appropriately distinguish association from causal identification?",
            "The task is to audit, not reflexively disagree.",
        ),
        rationale="The advice is appropriately cautious and identifies evidence needed for causal claims.",
    ),
)


def get_audit_cases(
    difficulty: str | None = None,
    domain: str | None = None,
) -> list[AIAuditCase]:
    cases = list(CASES)

    if difficulty and difficulty != "All":
        cases = [c for c in cases if c.difficulty == difficulty]

    if domain and domain != "All":
        cases = [c for c in cases if c.domain == domain]

    return cases


def evaluate_audit_response(
    case: AIAuditCase,
    verdict: AuditVerdict,
    reasoning: str,
    hint_level: int = 0,
) -> AuditEvaluation:
    text = " ".join(reasoning.lower().split())
    verdict_correct = verdict == case.preferred_verdict
    key_terms_found = [t for t in case.key_terms if t.lower() in text]
    evidence_terms_found = [t for t in case.evidence_terms if t.lower() in text]
    words = len(reasoning.split())

    score = round(
        0.45 * float(verdict_correct)
        + 0.30 * min(len(key_terms_found) / 2, 1.0)
        + 0.15 * min(len(evidence_terms_found), 1.0)
        + 0.10 * min(words / 30, 1.0),
        3,
    )

    next_hint = case.hints[min(hint_level, len(case.hints) - 1)]

    if not verdict_correct:
        return AuditEvaluation(
            AuditStatus.RETRY,
            score,
            False,
            key_terms_found,
            evidence_terms_found,
            "Re-audit the AI's claim. Ask whether the advice overstates, understates, or appropriately limits what the evidence can support.",
            next_hint,
        )

    if words < 12 or not key_terms_found:
        return AuditEvaluation(
            AuditStatus.DEVELOP,
            score,
            True,
            key_terms_found,
            evidence_terms_found,
            "Your verdict is plausible, but the statistical reason is not yet explicit. Identify the principle, assumption or evidence requirement behind your audit.",
            next_hint,
        )

    if case.preferred_verdict == AuditVerdict.MORE_EVIDENCE and not evidence_terms_found:
        return AuditEvaluation(
            AuditStatus.DEVELOP,
            score,
            True,
            key_terms_found,
            evidence_terms_found,
            "You correctly identified that the claim is not settled. Specify what additional evidence or diagnostic would change your judgement.",
            next_hint,
        )

    return AuditEvaluation(
        AuditStatus.RESOLVED,
        score,
        True,
        key_terms_found,
        evidence_terms_found,
        "Resolved: your audit evaluates the AI claim using statistical principles rather than accepting or rejecting it reflexively.",
        "",
    )
