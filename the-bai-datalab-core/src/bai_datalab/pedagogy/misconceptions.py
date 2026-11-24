from .models import Misconception


def detect_misconception(concept: str, text: str) -> Misconception:
    t = text.lower()

    if concept == "response transformation" and (
        "because it fit better" in t or "higher r2" in t or "higher r-squared" in t
    ):
        return Misconception.FIT_EQUALS_VALIDITY

    if concept == "interaction effects" and (
        "main effect is the overall effect" in t
        or "independent of" in t
    ):
        return Misconception.MAIN_EFFECT_UNCONDITIONAL

    if concept == "classification evaluation" and (
        "accuracy is enough" in t
        or "accuracy alone" in t
    ):
        return Misconception.ACCURACY_IS_ENOUGH

    if concept == "data partitioning" and (
        "training accuracy" in t
        or "training performance" in t
    ):
        return Misconception.TRAINING_PERFORMANCE_IS_GENERALISATION

    if concept == "data leakage" and (
        "before the split is fine" in t
        or "does not matter before splitting" in t
    ):
        return Misconception.PREPROCESSING_BEFORE_SPLIT_IS_SAFE

    return Misconception.NONE


MISCONCEPTION_PROMPTS = {
    Misconception.FIT_EQUALS_VALIDITY:
        "Model fit alone does not establish that a modelling decision is appropriate. What diagnostic evidence would you need?",
    Misconception.MAIN_EFFECT_UNCONDITIONAL:
        "In an interaction model, is that coefficient really an unconditional overall effect? What is it conditional on?",
    Misconception.ACCURACY_IS_ENOUGH:
        "Could a model have high accuracy while performing poorly on the minority class? Which metric would reveal that?",
    Misconception.TRAINING_PERFORMANCE_IS_GENERALISATION:
        "What is the difference between fitting performance and performance on unseen data?",
    Misconception.PREPROCESSING_BEFORE_SPLIT_IS_SAFE:
        "Could information from the future test set influence preprocessing parameters if preprocessing is fitted before the split?",
}
