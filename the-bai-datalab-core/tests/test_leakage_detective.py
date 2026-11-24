from bai_datalab.leakage import (
    LeakageStatus, LeakageVerdict, evaluate_leakage_response, get_cases
)

def _case(case_id):
    return next(c for c in get_cases() if c.case_id == case_id)

def test_scaling_before_split_resolves():
    case = _case("PY_SCALE_BEFORE_SPLIT")
    result = evaluate_leakage_response(
        case, LeakageVerdict.LEAKAGE,
        "The scaler uses the full dataset, so test observations affect the mean and standard deviation. "
        "I would split first and fit on training only using a pipeline."
    )
    assert result.status == LeakageStatus.RESOLVED

def test_safe_pipeline_resolves_as_no_leakage():
    case = _case("PY_PIPELINE_SAFE")
    result = evaluate_leakage_response(
        case, LeakageVerdict.NO_LEAKAGE,
        "The pipeline is fitted separately in each cross-validation training fold, so preprocessing does not use "
        "the validation fold. The pipeline keeps preprocessing within each fold."
    )
    assert result.status == LeakageStatus.RESOLVED

def test_short_answer_not_resolved():
    case = _case("PY_TARGET_ENCODING")
    result = evaluate_leakage_response(case, LeakageVerdict.LEAKAGE, "It leaks.")
    assert result.status != LeakageStatus.RESOLVED

def test_wrong_verdict_retries():
    case = _case("PY_TEST_TUNING")
    result = evaluate_leakage_response(case, LeakageVerdict.NO_LEAKAGE, "The model uses the test set.")
    assert result.status == LeakageStatus.RETRY

def test_filters():
    cases = get_cases(difficulty="Advanced", language="Python")
    assert cases
    assert all(c.difficulty == "Advanced" and c.language == "Python" for c in cases)
