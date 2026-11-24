from __future__ import annotations


RULE_FOLLOWUPS = {
    "MODEL_AIC_001": (
        "Compare the response used by each model before interpreting the AIC values. "
        "Are the fitted likelihoods based on the same observed response scale?"
    ),
    "LM_LOG_RESPONSE_001": (
        "A transformation needs evidence, not just improved fit. Identify a residual, "
        "variance, linearity, or distributional feature that motivated the change."
    ),
    "MODEL_RESPONSE_TRANSFORMATION_001": (
        "A transformation needs evidence, not just improved fit. Identify a diagnostic "
        "feature that motivated the change and what improved after transformation."
    ),
    "LM_INTERACTION_001": (
        "With an interaction present, interpret each main effect conditionally. State the "
        "value/reference level of the interacting variable for that coefficient."
    ),
    "MODEL_INTERACTION_001": (
        "With an interaction present, interpret each main effect conditionally rather "
        "than as an unconditional average effect."
    ),
    "LM_MULTICOLLINEARITY_001": (
        "Explain what evidence you used to judge predictor redundancy or coefficient "
        "instability, for example correlations or variance inflation."
    ),
    "LM_HETEROSCEDASTICITY_001": (
        "Describe the residual-versus-fitted pattern you would expect under constant "
        "variance and what departure would concern you."
    ),
    "GLM_CLASSIFICATION_METRICS_001": (
        "Choose evaluation metrics that match the decision problem. Explain why accuracy "
        "alone may be insufficient and how the threshold was chosen."
    ),
    "CLASSIFICATION_METRICS_001": (
        "Choose evaluation metrics that match the decision problem and justify the "
        "classification threshold or ranking metric."
    ),
    "ML_TRAIN_TEST_SPLIT_001": (
        "Separate fitting from evaluation. Explain where the model first encounters data "
        "that were not used to estimate preprocessing or model parameters."
    ),
    "TRAIN_TEST_SPLIT_001": (
        "Separate fitting from evaluation. Identify the unseen data used for the final "
        "performance estimate."
    ),
    "ML_DATA_LEAKAGE_001": (
        "Trace preprocessing in chronological order. Which quantities were estimated "
        "before the test set was isolated?"
    ),
    "DATA_LEAKAGE_001": (
        "Trace preprocessing in chronological order and identify whether any information "
        "from validation/test observations could influence fitted transformations."
    ),
    "MODEL_RANDOM_EFFECTS_001": (
        "Explain the grouping structure represented by the random effects and why that "
        "dependence cannot be treated as independent observations."
    ),
    "MODEL_RANDOM_SLOPE_001": (
        "Explain why the effect is allowed to vary across groups and whether the data "
        "contain enough within-group information to estimate that variation."
    ),
    "MODEL_GLM_FAMILY_LINK_001": (
        "Connect the outcome scale to the chosen distribution and link. What feature of "
        "the response makes this family/link appropriate?"
    ),
    "MODEL_COUNT_OVERDISPERSION_001": (
        "For count outcomes, compare the variability implied by the model with the "
        "observed variability. What would overdispersion change?"
    ),
    "MODEL_NONLINEAR_TERM_001": (
        "Explain what form of nonlinearity this term permits and how you checked that the "
        "added flexibility is warranted rather than simply improving in-sample fit."
    ),
    "MODEL_HIGH_ORDER_INTERACTION_001": (
        "A high-order interaction makes lower-order terms conditional. Work from the "
        "highest-order term down and state what each coefficient is conditional on."
    ),
    "MODEL_WEIGHTS_001": (
        "Explain what the observation weights represent and whether they are frequency, "
        "precision, sampling, or another type of weight."
    ),
    "MODEL_OFFSET_001": (
        "Explain why this quantity is an offset rather than an estimated predictor and "
        "what exposure/rate interpretation it imposes."
    ),
    "MODEL_REGULARIZATION_001": (
        "Explain the bias-variance trade-off introduced by regularisation and how the "
        "penalty strength was selected."
    ),
    "MODEL_CROSS_VALIDATION_001": (
        "Explain how folds were constructed and whether all preprocessing and tuning were "
        "performed inside each training fold."
    ),
    "MODEL_HYPERPARAMETER_TUNING_001": (
        "Separate tuning data from final evaluation data. Which observations influenced "
        "hyperparameter selection and which were reserved for final assessment?"
    ),
    "MODEL_PIPELINE_001": (
        "Explain which transformations are fitted inside the pipeline and why that helps "
        "prevent leakage across validation folds."
    ),
    "MODEL_IMPUTATION_001": (
        "Explain what information was used to estimate missing-value replacements and "
        "whether imputation was learned separately within training folds."
    ),
    "MODEL_SURVIVAL_001": (
        "Explain how censoring is represented and what assumption is required for the "
        "survival-model interpretation to be credible."
    ),
    "MODEL_GAM_SMOOTH_001": (
        "Explain why a smooth term is needed, how smoothness was controlled, and what the "
        "estimated shape implies substantively."
    ),
    "MODEL_MULTINOMIAL_001": (
        "Explain the reference category and how each coefficient compares an outcome "
        "category with that reference."
    ),
    "MODEL_ORDINAL_001": (
        "Explain the ordering assumption and, where relevant, how you assessed the "
        "proportional-odds/parallel-lines assumption."
    ),
}


def deterministic_followup(finding, fallback: str) -> str:
    """Return a rule-specific local Socratic follow-up where available."""
    return RULE_FOLLOWUPS.get(finding.rule_id, fallback)
