from bai_datalab.bundle import analyse_bundle
from bai_datalab.models import BundleArtifact


def test_code_data_mismatch():
    script = BundleArtifact(
        "model.R",
        "r_script",
        b"m <- lm(y ~ x1 + x_missing, data=d)",
    )

    data = BundleArtifact(
        "data.csv",
        "dataset",
        b"y,x1\n1,2\n2,3\n",
    )

    result = analyse_bundle(
        [script, data]
    )

    ids = {
        finding.rule_id
        for finding in result.findings
    }

    assert "BUNDLE_VARIABLE_MISMATCH_001" in ids


def test_constant_variable_finding():
    data = BundleArtifact(
        "data.csv",
        "dataset",
        b"y,x\n1,5\n2,5\n3,5\n",
    )

    result = analyse_bundle(
        [data]
    )

    ids = {
        finding.rule_id
        for finding in result.findings
    }

    assert "DATA_CONSTANT_VARIABLE_001" in ids


def test_binary_imbalance():
    rows = ["y,x"]

    rows.extend(
        ["0,1"] * 19
    )

    rows.append("1,2")

    data = BundleArtifact(
        "data.csv",
        "dataset",
        ("\n".join(rows)).encode(),
    )

    result = analyse_bundle(
        [data]
    )

    ids = {
        finding.rule_id
        for finding in result.findings
    }

    assert "DATA_CLASS_IMBALANCE_001" in ids
