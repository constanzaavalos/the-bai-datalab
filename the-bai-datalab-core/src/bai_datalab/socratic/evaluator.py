import re

from .models import SocraticOutcome, SocraticStatus


CRITERIA = {
    "response transformation": [
        {"residual", "variance", "diagnostic"},
        {"skew", "stabilise", "stabilize"},
    ],
    "interaction effects": [
        {"conditional", "depends", "interaction"},
        {"effect", "slope", "coefficient"},
    ],
    "model diagnostics": [
        {"residual", "qq", "variance", "influence", "calibration"},
        {"assumption", "diagnostic", "pattern"},
    ],
    "classification evaluation": [
        {"precision", "recall", "sensitivity", "specificity", "roc", "auc", "f1"},
        {"threshold", "test", "validation"},
    ],
    "data partitioning": [
        {"train", "test", "validation"},
        {"unseen", "generalisation", "generalization"},
    ],
    "data leakage": [
        {"train", "training"},
        {"test", "leakage", "preprocessing"},
    ],
    "class imbalance": [
        {"imbalance", "class", "minority"},
        {"accuracy", "precision", "recall", "f1"},
    ],
}


GENERIC_EVIDENCE_TERMS = {
    "because", "evidence", "diagnostic", "data", "model", "assumption",
    "validation", "residual", "compare", "checked", "estimated", "group",
    "distribution", "variance", "threshold", "training", "test", "fold",
}

FOLLOW = {
    "response transformation": "What specific diagnostic evidence supports the transformation?",
    "interaction effects": "What value of the interacting variable makes the main-effect interpretation meaningful?",
    "model diagnostics": "Name one diagnostic and describe the pattern that would concern you.",
    "classification evaluation": "Which metric best reflects your modelling objective, and why?",
    "data partitioning": "How did you ensure the final performance estimate used unseen data?",
    "data leakage": "Which preprocessing parameters were learned only from the training data?",
    "class imbalance": "Why could overall accuracy be misleading in this setting?",
}


def evaluate_response(finding, response):
    text = re.sub(r"\s+", " ", response.text.lower()).strip()
    words = re.findall(r"\b\w+\b", text)
    groups = CRITERIA.get(finding.concept, [])
    if not groups:
        # Generic criterion for advanced rules: substantive reasoning + an explicit
        # evidence/assumption link can resolve without requiring an LLM.
        groups = [GENERIC_EVIDENCE_TERMS]

    found, missing, matched = [], [], 0

    for i, group in enumerate(groups, 1):
        hits = [t for t in group if t in text]
        if hits:
            matched += 1
            found.extend(hits)
        else:
            missing.append(f"group_{i}")

    score = round(
        0.85 * (matched / len(groups) if groups else 0)
        + 0.15 * min(len(words) / 8, 1),
        3,
    )

    if len(words) < 5:
        level = min(response.hint_level + 1, len(finding.hints)) if finding.hints else 0
        msg = finding.hints[level - 1] if finding.hints and level else "Develop your reasoning further."
        return SocraticOutcome(
            finding.id, SocraticStatus.HINT, msg, level,
            found, missing or ["more developed reasoning"], score
        )

    if groups and matched == len(groups) and len(words) >= 8:
        return SocraticOutcome(
            finding.id, SocraticStatus.RESOLVED,
            "Your explanation identifies the key conceptual issue and connects it to relevant evidence.",
            response.hint_level, found, [], score
        )

    return SocraticOutcome(
        finding.id, SocraticStatus.FOLLOW_UP,
        FOLLOW.get(finding.concept, "Can you justify this using specific evidence from your analysis?"),
        response.hint_level, found, missing or ["stronger evidence"], score
    )
