from bai_datalab.ai_audit import (
    AuditStatus,
    AuditVerdict,
    evaluate_audit_response,
    get_audit_cases,
)


def _case(case_id):
    return next(c for c in get_audit_cases() if c.case_id == case_id)


def test_bad_significance_advice_is_challenged():
    case = _case("SIG_DROP")
    result = evaluate_audit_response(
        case,
        AuditVerdict.CHALLENGE,
        "I would challenge this because p-values do not determine predictive usefulness or confounding. "
        "Substantive domain knowledge and validation should inform variable selection.",
    )
    assert result.status == AuditStatus.RESOLVED


def test_good_causal_caution_can_be_accepted():
    case = _case("AI_CAUTION_CORRECT")
    result = evaluate_audit_response(
        case,
        AuditVerdict.ACCEPT,
        "I would accept this because observational association does not establish causal identification. "
        "The response appropriately asks about study design, confounding and assumptions, with sensitivity analysis as evidence.",
    )
    assert result.status == AuditStatus.RESOLVED


def test_more_evidence_case_requires_evidence():
    case = _case("LOG_TRANSFORM")
    result = evaluate_audit_response(
        case,
        AuditVerdict.MORE_EVIDENCE,
        "A higher R squared does not by itself justify the transformation; residual behaviour and the response scale matter.",
    )
    assert result.status != AuditStatus.RESOLVED


def test_wrong_verdict_retries():
    case = _case("IMBALANCE_ACCURACY")
    result = evaluate_audit_response(
        case,
        AuditVerdict.ACCEPT,
        "Accuracy is high.",
    )
    assert result.status == AuditStatus.RETRY


def test_case_filters():
    advanced = get_audit_cases(difficulty="Advanced")
    assert advanced
    assert all(c.difficulty == "Advanced" for c in advanced)
