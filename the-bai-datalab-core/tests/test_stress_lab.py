from bai_datalab.stress_lab import StressSettings, simulate_stress, evaluate_prediction

def test_shift_hurts_test_more_than_train():
    base=simulate_stress(StressSettings(shift=0.0))
    shifted=simulate_stress(StressSettings(shift=0.8))
    assert shifted.test_score < base.test_score
    assert shifted.calibration_error > base.calibration_error

def test_small_samples_reduce_stability():
    small=simulate_stress(StressSettings(sample_size=50))
    large=simulate_stress(StressSettings(sample_size=2000))
    assert small.stability < large.stability

def test_prediction_evaluator():
    before=simulate_stress(StressSettings(shift=0))
    after=simulate_stress(StressSettings(shift=.8))
    status,_=evaluate_prediction("decrease", "Distribution shift changes the test distribution and harms generalisation to unseen observations.", before, after)
    assert status=="resolved"
