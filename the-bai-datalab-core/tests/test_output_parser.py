from bai_datalab.output_parser import parse_model_output


def test_r_output_values():
    content = b"""
Residuals:
 Min 1Q Median 3Q Max
 -1 0 0 0 1

Coefficients:
            Estimate Std. Error t value Pr(>|t|)
(Intercept)  1.2000   0.2000   6.0 0.001
x1           0.5000   0.1000   5.0 0.002

Multiple R-squared: 0.81
Adjusted R-squared: 0.79
AIC = 120.4
"""
    out = parse_model_output("output.txt", content)
    assert out["r_squared"] == 0.81
    assert out["adjusted_r_squared"] == 0.79
    assert out["aic"] == 120.4
    assert len(out["coefficients"]) == 2
