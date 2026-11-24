from bai_datalab.analysis import analyse_r_script


def _ids(source):
    return {
        finding.rule_id
        for finding in analyse_r_script("model.R", source).findings
    }


def test_multicollinearity_rule():
    source = "m <- lm(y ~ x1 + x2 + x3 + x4, data=d)"
    assert "LM_MULTICOLLINEARITY_001" in _ids(source)


def test_vif_suppresses_multicollinearity_prompt():
    source = "\n".join([
        "m <- lm(y ~ x1 + x2 + x3 + x4, data=d)",
        "vif(m)",
    ])
    assert "LM_MULTICOLLINEARITY_001" not in _ids(source)


def test_heteroscedasticity_rule():
    source = "m <- lm(y ~ x1 + x2, data=d)"
    assert "LM_HETEROSCEDASTICITY_001" in _ids(source)


def test_bptest_suppresses_heteroscedasticity_prompt():
    source = "\n".join([
        "m <- lm(y ~ x1 + x2, data=d)",
        "bptest(m)",
    ])
    assert "LM_HETEROSCEDASTICITY_001" not in _ids(source)


def test_logistic_requires_metrics_and_split():
    source = "m <- glm(y ~ x1 + x2, family=binomial(), data=d)"
    ids = _ids(source)
    assert "GLM_CLASSIFICATION_METRICS_001" in ids
    assert "ML_TRAIN_TEST_SPLIT_001" in ids
    assert "GLM_CLASS_IMBALANCE_001" in ids


def test_classification_metrics_detected():
    source = "\n".join([
        "m <- glm(y ~ x1 + x2, family=binomial(), data=d)",
        "confusionMatrix(pred, truth)",
    ])
    assert "GLM_CLASSIFICATION_METRICS_001" not in _ids(source)


def test_split_detected():
    source = "\n".join([
        "split <- initial_split(d, prop=.8)",
        "m <- glm(y ~ x1 + x2, family=binomial(), data=train)",
    ])
    assert "ML_TRAIN_TEST_SPLIT_001" not in _ids(source)


def test_potential_leakage_before_split():
    source = "\n".join([
        "d$x <- scale(d$x)",
        "split <- initial_split(d, prop=.8)",
        "m <- glm(y ~ x, family=binomial(), data=train)",
    ])
    assert "ML_DATA_LEAKAGE_001" in _ids(source)
