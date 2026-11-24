# The B-AI DataLab Core v0.8

v0.8 is cumulative and adds:

- Python AST parsing;
- initial statsmodels support;
- initial scikit-learn support;
- train/test split detection;
- preprocessing detection;
- data leakage checks;
- classification metric detection;
- structured model-output parsing;
- Evidence Items linking questions to dataset and output evidence.

Run:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## v0.12 advanced rule library

Adds deterministic Socratic triggers for GLM family/link choices, mixed models, random slopes, nonlinear terms, GAMs, count dispersion, survival/ordinal/multinomial models, weights/offsets, regularisation, cross-validation, hyperparameter tuning, pipelines, imputation, feature-selection leakage and time-series validation.
