from __future__ import annotations
from dataclasses import dataclass
import math
import random


@dataclass(frozen=True)
class StressSettings:
    sample_size: int = 500
    noise: float = 0.20
    outliers: float = 0.00
    nonlinearity: float = 0.00
    shift: float = 0.00
    minority_rate: float = 0.30


@dataclass(frozen=True)
class StressResult:
    train_score: float
    test_score: float
    calibration_error: float
    generalisation_gap: float
    stability: float
    dominant_failure: str
    question: str


def _clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def simulate_stress(settings: StressSettings, seed: int = 42) -> StressResult:
    """Deterministic pedagogical simulator, not a claim about any fitted real-world model."""
    rng = random.Random(seed)
    n_effect = 0.10 / math.sqrt(max(settings.sample_size, 20) / 100)
    imbalance = abs(settings.minority_rate - 0.5) * 2

    train = (
        0.94
        - 0.20 * settings.noise
        - 0.06 * settings.outliers
        - 0.04 * settings.nonlinearity
        - 0.02 * imbalance
        + rng.uniform(-0.005, 0.005)
    )
    test = (
        train
        - 0.10 * settings.nonlinearity
        - 0.14 * settings.shift
        - 0.08 * settings.outliers
        - 0.08 * imbalance
        - n_effect
        + rng.uniform(-0.005, 0.005)
    )
    cal = (
        0.025
        + 0.11 * settings.shift
        + 0.08 * settings.noise
        + 0.07 * imbalance
        + 0.04 * settings.outliers
    )
    stability = 1.0 - (
        0.28 * settings.noise
        + 0.30 * settings.shift
        + 0.20 * settings.outliers
        + 0.15 * settings.nonlinearity
        + min(n_effect * 2.5, 0.30)
    )

    factors = {
        "distribution shift": settings.shift * 1.4,
        "noise": settings.noise,
        "outliers": settings.outliers * 1.1,
        "nonlinearity / misspecification": settings.nonlinearity,
        "class imbalance": imbalance,
        "small-sample instability": min(n_effect * 4, 1),
    }
    dominant = max(factors, key=factors.get)

    questions = {
        "distribution shift": "Why can performance deteriorate even when the training procedure itself has not changed?",
        "noise": "Which part of the observed variation is irreducible, and which uncertainty might shrink with more data?",
        "outliers": "Which fitted quantities or loss functions are especially sensitive to a small number of extreme observations?",
        "nonlinearity / misspecification": "What structure in the data-generating process can the current model fail to represent?",
        "class imbalance": "Which performance summaries could remain deceptively reassuring as the minority class becomes rarer?",
        "small-sample instability": "How would repeated samples from the same population change your confidence in this fitted model?",
    }

    train = _clip(train)
    test = _clip(test)
    return StressResult(
        train_score=round(train, 3),
        test_score=round(test, 3),
        calibration_error=round(_clip(cal), 3),
        generalisation_gap=round(max(train-test, 0), 3),
        stability=round(_clip(stability), 3),
        dominant_failure=dominant,
        question=questions[dominant],
    )


def evaluate_prediction(prediction: str, explanation: str, before: StressResult, after: StressResult):
    """Evaluate whether the student's directional prediction and mechanism are defensible."""
    delta = after.test_score - before.test_score
    expected = "decrease" if delta < -0.015 else "increase" if delta > 0.015 else "similar"
    p = prediction.lower()
    predicted = "decrease" if "decre" in p or "worse" in p or "drop" in p else "increase" if "incre" in p or "better" in p else "similar"
    correct = predicted == expected
    words = explanation.lower()
    mechanism_terms = (
        "shift", "noise", "variance", "outlier", "nonlinear", "imbalance", "minority",
        "sample", "general", "calibr", "distribution", "misspec", "uncert"
    )
    mechanism = any(term in words for term in mechanism_terms)
    substantive = len(explanation.split()) >= 12

    if correct and mechanism and substantive:
        return "resolved", "Your prediction is consistent with the simulated result and your explanation identifies a relevant statistical mechanism."
    if correct:
        return "develop", "The direction is plausible. Strengthen the explanation by identifying the statistical mechanism rather than describing the metric change."
    return "retry", "Compare your prediction with the observed change. Explain which assumption or data property changed and why that should affect generalisation."
