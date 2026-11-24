from bai_datalab.analysis import analyse_r_script
from bai_datalab.models import AnchorScope, DecisionType


def test_single_line_regression_still_works():
    source = "\n".join([
        "m1 <- lm(price ~ area + rooms, data = homes)",
        "m2 <- lm(log(price) ~ area * rooms, data = homes)",
        "AIC(m1, m2)",
    ])

    result = analyse_r_script("model.R", source)

    rule_ids = {f.rule_id for f in result.findings}
    assert "LM_LOG_RESPONSE_001" in rule_ids
    assert "LM_INTERACTION_001" in rule_ids
    assert "MODEL_AIC_001" in rule_ids


def test_multiline_model_anchor_and_metadata():
    source = """m2 <- lm(
  log(price) ~
    area * rooms +
    age +
    location,
  data = homes
)
"""

    result = analyse_r_script("model.R", source)

    model = next(
        d for d in result.decisions
        if d.type == DecisionType.MODEL_DEFINITION
    )

    assert model.anchor.line_start == 1
    assert model.anchor.line_end == 7
    assert model.anchor.scope == AnchorScope.BLOCK

    assert model.payload["object"] == "m2"
    assert model.payload["function"] == "lm"
    assert model.payload["response_expression"] == "log(price)"
    assert model.payload["response_variable"] == "price"
    assert model.payload["predictors_expression"] == "area * rooms + age + location"
    assert model.payload["interaction_terms"] == ["area * rooms"]


def test_multiline_glm_family():
    source = """fit <- glm(
  outcome ~ age + income,
  family = binomial(link = "logit"),
  data = survey
)
"""

    result = analyse_r_script("logit.R", source)

    model = next(
        d for d in result.decisions
        if d.type == DecisionType.MODEL_DEFINITION
    )

    assert model.payload["function"] == "glm"
    assert model.payload["response_variable"] == "outcome"
    assert model.payload["family"] == 'binomial(link = "logit")'


def test_multiline_aic():
    source = """m1 <- lm(price ~ area, data = homes)
m2 <- lm(log(price) ~ area, data = homes)

AIC(
  m1,
  m2
)
"""

    result = analyse_r_script("compare.R", source)

    comparison = next(
        d for d in result.decisions
        if d.type == DecisionType.MODEL_COMPARISON
    )

    assert comparison.anchor.line_start == 4
    assert comparison.anchor.line_end == 7
    assert comparison.payload["models"] == ["m1", "m2"]


def test_diagnostics_suppressed():
    source = """m1 <- lm(
  price ~ area,
  data = homes
)
plot(m1)
"""
    result = analyse_r_script("model.R", source)

    assert "LM_DIAGNOSTICS_001" not in {
        f.rule_id for f in result.findings
    }
