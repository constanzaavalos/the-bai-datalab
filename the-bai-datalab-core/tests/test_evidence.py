from bai_datalab.bundle import analyse_bundle
from bai_datalab.models import BundleArtifact


def test_output_evidence_attached():
    script = BundleArtifact(
        "model.R", "r_script",
        b"m <- lm(log(y) ~ x1 * x2, data=d)"
    )
    output = BundleArtifact(
        "output.txt", "model_output",
        b"Residuals:\nMin 1Q Median 3Q Max\n-1 0 0 0 1\nMultiple R-squared: 0.9\n"
    )
    result = analyse_bundle([script, output])
    transformed = next(f for f in result.findings if f.concept == "response transformation")
    assert transformed.related_evidence
    assert transformed.related_evidence[0].evidence_type == "model_output"
