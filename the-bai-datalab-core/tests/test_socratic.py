from bai_datalab.analysis import analyse_r_script
from bai_datalab.socratic import (
    StudentResponse,
    SocraticStatus,
    evaluate_response,
)


def _finding(rule_id):
    source = "\n".join([
        "m1 <- lm(price ~ area + rooms, data = homes)",
        "m2 <- lm(log(price) ~ area * rooms, data = homes)",
        "AIC(m1, m2)",
    ])
    result = analyse_r_script("model.R", source)
    return next(f for f in result.findings if f.rule_id == rule_id)


def test_short_answer_gets_hint():
    f = _finding("LM_LOG_RESPONSE_001")
    o = evaluate_response(
        f,
        StudentResponse(f.id, "Because it fit better."),
    )
    assert o.status == SocraticStatus.HINT
    assert o.hint_level == 1


def test_partial_answer_gets_follow_up():
    f = _finding("LM_LOG_RESPONSE_001")
    o = evaluate_response(
        f,
        StudentResponse(
            f.id,
            "I used the log because the response was very skewed and this seemed more appropriate.",
        ),
    )
    assert o.status == SocraticStatus.FOLLOW_UP


def test_strong_answer_resolves():
    f = _finding("LM_LOG_RESPONSE_001")
    o = evaluate_response(
        f,
        StudentResponse(
            f.id,
            "The original residuals were strongly skewed and showed non-constant variance, "
            "so I used the log transformation to stabilise the residual variance.",
        ),
    )
    assert o.status == SocraticStatus.RESOLVED


def test_interaction_reasoning_resolves():
    f = _finding("LM_INTERACTION_001")
    o = evaluate_response(
        f,
        StudentResponse(
            f.id,
            "With the interaction, the effect or slope of area depends on rooms, "
            "so the coefficient is conditional rather than an unconditional effect.",
        ),
    )
    assert o.status == SocraticStatus.RESOLVED
