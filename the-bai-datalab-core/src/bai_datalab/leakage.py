from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class LeakageVerdict(str, Enum):
    LEAKAGE = "leakage"
    NO_LEAKAGE = "no_leakage"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class LeakageStatus(str, Enum):
    RETRY = "retry"
    DEVELOP = "develop"
    RESOLVED = "resolved"


@dataclass(frozen=True)
class LeakageCase:
    case_id: str
    title: str
    difficulty: str
    language: str
    topic: str
    scenario: str
    code: str
    verdict: LeakageVerdict
    mechanism_terms: tuple[str, ...]
    prevention_terms: tuple[str, ...]
    hints: tuple[str, ...]
    explanation_focus: str


@dataclass
class LeakageEvaluation:
    status: LeakageStatus
    score: float
    verdict_correct: bool
    mechanism_found: list[str] = field(default_factory=list)
    prevention_found: list[str] = field(default_factory=list)
    feedback: str = ""
    next_hint: str = ""


CASES: tuple[LeakageCase, ...] = (
    LeakageCase(
        "PY_SCALE_BEFORE_SPLIT",
        "The suspiciously polished features",
        "Foundation",
        "Python",
        "Preprocessing leakage",
        "A student standardises all predictors and then creates a train/test split. The final model is evaluated on the test set.",
        '''from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.20, random_state=42
)''',
        LeakageVerdict.LEAKAGE,
        ("full dataset", "test", "mean", "standard deviation", "scaler", "before split"),
        ("fit on training", "pipeline", "training only", "after split"),
        (
            "Ask which observations contribute to the estimated scaling parameters.",
            "The transformation itself is not the issue. Focus on when its parameters are learned.",
            "Could the test observations affect the means or standard deviations used for the training features?",
        ),
        "preprocessing parameters estimated using test-set information",
    ),
    LeakageCase(
        "R_IMPUTE_BEFORE_SPLIT",
        "The helpful imputer",
        "Foundation",
        "R",
        "Imputation leakage",
        "Missing values are imputed using the complete dataset before training and validation sets are created.",
        '''library(mice)
library(rsample)

imp <- mice(df, m = 1, printFlag = FALSE)
completed <- complete(imp)

split <- initial_split(completed, prop = 0.8)
train <- training(split)
test  <- testing(split)''',
        LeakageVerdict.LEAKAGE,
        ("test", "imputation", "full dataset", "before split", "information"),
        ("training", "within resample", "fold", "split first", "recipe"),
        (
            "Which observations help estimate the missing values?",
            "Imagine that the eventual test observations had very different distributions.",
            "Imputation should be treated as a fitted preprocessing step, not as neutral data cleaning.",
        ),
        "imputation model learned before the hold-out set is isolated",
    ),
    LeakageCase(
        "PY_FEATURE_SELECTION",
        "The ten best predictors",
        "Intermediate",
        "Python",
        "Feature-selection leakage",
        "The analyst selects variables using the outcome on the whole dataset, then evaluates a model on a held-out test set.",
        '''from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.model_selection import train_test_split

selector = SelectKBest(score_func=f_classif, k=10)
X_selected = selector.fit_transform(X, y)

X_train, X_test, y_train, y_test = train_test_split(
    X_selected, y, test_size=0.25, random_state=7
)''',
        LeakageVerdict.LEAKAGE,
        ("outcome", "y", "test", "feature selection", "full dataset", "selection"),
        ("training", "pipeline", "inside cross-validation", "fold", "nested"),
        (
            "Does the feature-selection step use y?",
            "Ask whether the eventual test labels influence which predictors survive.",
            "Selection must be re-estimated within the training data/resampling process.",
        ),
        "test labels influence feature selection",
    ),
    LeakageCase(
        "PY_PIPELINE_SAFE",
        "Pipeline under suspicion",
        "Intermediate",
        "Python",
        "Safe preprocessing",
        "A pipeline performs imputation and scaling. Cross-validation is applied to the entire pipeline.",
        '''from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
    ("model", LogisticRegression())
])

scores = cross_val_score(pipe, X, y, cv=5, scoring="roc_auc")''',
        LeakageVerdict.NO_LEAKAGE,
        ("pipeline", "fold", "training fold", "cross-validation", "fit separately"),
        ("pipeline", "within each fold", "training fold"),
        (
            "Do not flag preprocessing merely because it exists.",
            "Ask when Pipeline.fit() is called relative to each validation fold.",
            "Each preprocessing step is fitted on the training portion of each cross-validation split.",
        ),
        "preprocessing is fitted independently within each training fold",
    ),
    LeakageCase(
        "R_SMOTE_BEFORE_CV",
        "The balanced dataset",
        "Intermediate",
        "R",
        "Resampling leakage",
        "SMOTE is applied once to the complete dataset and the resulting synthetic dataset is then cross-validated.",
        '''library(themis)
library(recipes)
library(rsample)

rec <- recipe(outcome ~ ., data = df) |>
  step_smote(outcome)

balanced <- prep(rec) |> bake(new_data = NULL)

folds <- vfold_cv(balanced, v = 10, strata = outcome)''',
        LeakageVerdict.LEAKAGE,
        ("smote", "synthetic", "validation", "full dataset", "neighbors", "before"),
        ("inside fold", "recipe", "training fold", "resample"),
        (
            "Synthetic cases depend on observed cases and their neighbours.",
            "Could a validation observation influence a synthetic training observation?",
            "Sampling operations should occur inside each analysis/training fold.",
        ),
        "synthetic observations are created before validation folds are isolated",
    ),
    LeakageCase(
        "PY_TARGET_ENCODING",
        "The informative category",
        "Advanced",
        "Python",
        "Target leakage",
        "A categorical predictor is encoded using the mean outcome for each category before any resampling.",
        '''global_mean = df["y"].mean()
category_mean = df.groupby("occupation")["y"].mean()

df["occupation_te"] = (
    df["occupation"].map(category_mean).fillna(global_mean)
)

X_train, X_test, y_train, y_test = train_test_split(
    df[features], df["y"], test_size=0.2
)''',
        LeakageVerdict.LEAKAGE,
        ("target", "outcome", "y", "category mean", "test labels", "encoding"),
        ("out-of-fold", "training", "fold", "cross-fitting", "pipeline"),
        (
            "What information is used to construct occupation_te?",
            "For a test observation, could its own y value contribute to its predictor value?",
            "Target encoding requires out-of-fold/cross-fitted construction.",
        ),
        "outcome information is embedded into a predictor before evaluation",
    ),
    LeakageCase(
        "PY_TIME_RANDOM_SPLIT",
        "Tomorrow leaked into yesterday",
        "Advanced",
        "Python",
        "Temporal leakage",
        "A forecasting problem uses observations from 2018–2025. The analyst randomly splits rows into training and test sets.",
        '''X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    shuffle=True
)

model.fit(X_train, y_train)
pred = model.predict(X_test)''',
        LeakageVerdict.LEAKAGE,
        ("future", "time", "temporal", "chronological", "later", "earlier"),
        ("time split", "chronological", "rolling", "timeseriessplit", "forward"),
        (
            "Would this evaluation ever train on 2025 and test on 2021?",
            "Random independence assumptions are questionable when prediction has a temporal direction.",
            "Evaluation should preserve the information set that would have existed at prediction time.",
        ),
        "future observations can enter training for predictions about earlier periods",
    ),
    LeakageCase(
        "PY_TEST_TUNING",
        "Just one more look at the test score",
        "Advanced",
        "Python",
        "Hyperparameter leakage",
        "The analyst repeatedly evaluates candidate hyperparameters on the same test set and reports the best test result.",
        '''best_auc = -1
for depth in [2, 4, 6, 8, 12]:
    model = RandomForestClassifier(max_depth=depth)
    model.fit(X_train, y_train)
    auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
    if auc > best_auc:
        best_auc = auc
        best_depth = depth

print("Final test AUC:", best_auc)''',
        LeakageVerdict.LEAKAGE,
        ("test", "hyperparameter", "selection", "tuning", "repeated", "optimistic"),
        ("validation", "cross-validation", "nested", "untouched test", "holdout"),
        (
            "Is the test set being used only once for final evaluation?",
            "Choosing max_depth is itself part of model training/model selection.",
            "Repeatedly optimising against the test score makes the test set behave like validation data.",
        ),
        "test performance directly determines a hyperparameter",
    ),
    LeakageCase(
        "R_NESTED_CV_SAFE",
        "Nested resampling",
        "Expert",
        "R",
        "Nested validation",
        "Hyperparameters are tuned inside inner folds. Performance is estimated on outer assessment folds.",
        '''outer <- vfold_cv(df, v = 5, strata = outcome)

for (i in seq_len(nrow(outer))) {
  analysis_data   <- analysis(outer$splits[[i]])
  assessment_data <- assessment(outer$splits[[i]])

  inner <- vfold_cv(analysis_data, v = 5, strata = outcome)
  best_params <- tune_on(inner)

  final_model <- fit_with(best_params, analysis_data)
  outer_score[i] <- evaluate(final_model, assessment_data)
}''',
        LeakageVerdict.NO_LEAKAGE,
        ("outer", "inner", "assessment", "nested", "training", "held out"),
        ("nested", "outer fold", "inner fold"),
        (
            "Which data determine the hyperparameters, and which data estimate final performance?",
            "The outer assessment observations are excluded from the inner tuning process.",
            "This is the design nested cross-validation is intended to provide.",
        ),
        "model selection and performance estimation occur in separate resampling layers",
    ),
    LeakageCase(
        "PY_POST_OUTCOME_FEATURE",
        "The predictor from the future",
        "Expert",
        "Python",
        "Feature availability leakage",
        "A hospital predicts readmission at discharge. One predictor is the number of follow-up calls completed during the 30 days after discharge.",
        '''features = [
    "age",
    "length_of_stay",
    "diagnosis_group",
    "discharge_destination",
    "followup_calls_30d"
]

X = df[features]
y = df["readmitted_30d"]''',
        LeakageVerdict.LEAKAGE,
        ("future", "available", "prediction time", "after discharge", "post", "30 days"),
        ("prediction time", "remove", "available at discharge", "time-aware"),
        (
            "Forget train/test splitting for a moment. When is the prediction supposed to be made?",
            "Would followup_calls_30d be known at discharge?",
            "A feature can leak target-period information even if preprocessing and validation are technically correct.",
        ),
        "the predictor is not available at the intended prediction time",
    ),
)


def get_cases(difficulty: str | None = None, language: str | None = None) -> list[LeakageCase]:
    cases = list(CASES)
    if difficulty and difficulty != "All":
        cases = [c for c in cases if c.difficulty == difficulty]
    if language and language != "All":
        cases = [c for c in cases if c.language == language]
    return cases


def evaluate_leakage_response(case: LeakageCase, verdict: LeakageVerdict, reasoning: str, hint_level: int = 0) -> LeakageEvaluation:
    text = " ".join(reasoning.lower().split())
    verdict_correct = verdict == case.verdict
    mechanism_found = [term for term in case.mechanism_terms if term.lower() in text]
    prevention_found = [term for term in case.prevention_terms if term.lower() in text]
    reasoning_length = len(reasoning.split())

    mechanism_score = min(len(mechanism_found) / 2, 1.0)
    prevention_score = min(len(prevention_found), 1.0)
    score = round(
        0.40 * float(verdict_correct)
        + 0.35 * mechanism_score
        + 0.15 * prevention_score
        + 0.10 * min(reasoning_length / 25, 1.0),
        3,
    )
    next_hint = case.hints[min(hint_level, len(case.hints) - 1)]

    if not verdict_correct:
        return LeakageEvaluation(
            LeakageStatus.RETRY, score, False, mechanism_found, prevention_found,
            "Re-examine the information flow rather than the model type. Ask exactly what information is available when each fitted step is learned.",
            next_hint,
        )

    if reasoning_length < 12 or not mechanism_found:
        return LeakageEvaluation(
            LeakageStatus.DEVELOP, score, True, mechanism_found, prevention_found,
            "Your verdict is plausible, but the mechanism is not yet explicit. Identify what information crosses the training/evaluation boundary—or explain why it does not.",
            next_hint,
        )

    if case.verdict == LeakageVerdict.LEAKAGE and not prevention_found:
        return LeakageEvaluation(
            LeakageStatus.DEVELOP, score, True, mechanism_found, prevention_found,
            "You identified the leakage mechanism. Now state how you would redesign the workflow so that evaluation remains genuinely out of sample.",
            next_hint,
        )

    return LeakageEvaluation(
        LeakageStatus.RESOLVED, score, True, mechanism_found, prevention_found,
        "Resolved: your answer identifies the information-flow issue and connects it to an appropriate evaluation/preprocessing design.",
        "",
    )
