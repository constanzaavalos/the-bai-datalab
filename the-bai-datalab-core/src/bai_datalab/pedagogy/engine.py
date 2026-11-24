from __future__ import annotations

from .misconceptions import MISCONCEPTION_PROMPTS, detect_misconception
from .models import AttemptRecord, PedagogicalState, Strictness
from bai_datalab.socratic import evaluate_response
from .deterministic_feedback import deterministic_followup


STRICTNESS_THRESHOLDS = {
    Strictness.SUPPORTIVE: 0.70,
    Strictness.STANDARD: 0.82,
    Strictness.RIGOROUS: 0.90,
}


def evaluate_attempt(
    finding,
    response,
    state: PedagogicalState,
):
    outcome = evaluate_response(finding, response)
    misconception = detect_misconception(
        finding.concept,
        response.text,
    )

    if misconception.value != "none":
        outcome.status = type(outcome.status).FOLLOW_UP
        outcome.message = MISCONCEPTION_PROMPTS[misconception]
    elif outcome.status.value != "resolved":
        # Fast, rule-specific deterministic tutoring. This is the default path
        # and requires no network/LLM call.
        outcome.message = deterministic_followup(finding, outcome.message)

    threshold = STRICTNESS_THRESHOLDS[state.strictness]

    if outcome.status.value == "resolved" and outcome.score < threshold:
        outcome.status = type(outcome.status).FOLLOW_UP
        outcome.message = (
            "Your reasoning is on the right track, but add more explicit evidence "
            "from the analysis before resolving this question."
        )

    record = AttemptRecord(
        attempt_number=len(state.attempts) + 1,
        text=response.text,
        status=outcome.status.value,
        score=outcome.score,
        hint_level=outcome.hint_level,
        misconception=misconception,
    )

    state.attempts.append(record)
    state.resolved = outcome.status.value == "resolved"

    return outcome, state
