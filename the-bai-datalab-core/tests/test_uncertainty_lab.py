from bai_datalab.uncertainty_lab import (
    UncertaintySettings,
    decompose_uncertainty,
    more_data_experiment,
    evaluate_uncertainty_reasoning,
)


def test_more_data_reduces_sampling():
    before, after = more_data_experiment(
        UncertaintySettings(sample_size=100),
        multiplier=4,
    )
    assert after.sampling < before.sampling


def test_more_data_does_not_remove_aleatoric():
    before, after = more_data_experiment(
        UncertaintySettings(sample_size=100, noise=0.7),
        multiplier=10,
    )
    assert after.aleatoric == before.aleatoric


def test_domain_distance_increases_epistemic():
    near = decompose_uncertainty(
        UncertaintySettings(domain_distance=0.0)
    )
    far = decompose_uncertainty(
        UncertaintySettings(domain_distance=1.0)
    )
    assert far.epistemic > near.epistemic


def test_noise_increases_predictive_uncertainty():
    low = decompose_uncertainty(
        UncertaintySettings(noise=0.1)
    )
    high = decompose_uncertainty(
        UncertaintySettings(noise=0.9)
    )
    assert high.predictive > low.predictive


def test_reasoning_about_more_data_can_resolve():
    status, _ = evaluate_uncertainty_reasoning(
        "more_data",
        "Sampling uncertainty should decrease with more data. Aleatoric uncertainty remains because the noise is irreducible. "
        "Epistemic uncertainty may reduce partly, but model mismatch and domain limitations can remain.",
    )
    assert status == "resolved"
