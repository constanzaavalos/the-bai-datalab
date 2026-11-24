from __future__ import annotations

import ast
import uuid

from bai_datalab.models import AnalyticalDecision, AnchorScope, DecisionType, SourceAnchor


def _id():
    return f"decision_{uuid.uuid4().hex[:10]}"


def _source_segment(source, node):
    try:
        return ast.get_source_segment(source, node) or ""
    except Exception:
        return ""


def _anchor(filename, source, node):
    start = getattr(node, "lineno", 1)
    end = getattr(node, "end_lineno", start)
    return SourceAnchor(
        artifact=filename,
        line_start=start,
        line_end=end,
        excerpt=_source_segment(source, node),
        scope=AnchorScope.BLOCK if end > start else AnchorScope.LINE,
    )


def _name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


def _keywords(call):
    out = {}
    for kw in call.keywords:
        if kw.arg is not None:
            try:
                out[kw.arg] = ast.unparse(kw.value)
            except Exception:
                out[kw.arg] = ""
    return out


def parse_python_script(filename: str, source: str):
    decisions = []

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return decisions

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            call = node.value
            func = _name(call.func)
            target = _name(node.targets[0]) if node.targets else ""
            kws = _keywords(call)

            # statsmodels formula API
            if (func.endswith(".ols") or func.endswith(".logit") or func.endswith(".glm")
                or func.endswith(".mixedlm") or func.endswith(".mnlogit") or func.endswith(".probit")
                or func in {"ols", "logit", "glm", "mixedlm", "mnlogit", "probit"}):
                formula = ""
                if call.args:
                    try:
                        formula = ast.literal_eval(call.args[0])
                    except Exception:
                        formula = ast.unparse(call.args[0])

                response, predictors = (None, None)
                if "~" in formula:
                    response, predictors = [x.strip() for x in formula.split("~", 1)]

                family_kind = "binomial" if (func.endswith((".logit", ".probit")) or func in {"logit", "probit"}) else None
                if func.endswith(".mnlogit") or func == "mnlogit":
                    family_kind = "categorical"

                payload = {
                    "language": "python",
                    "object": target,
                    "function": func,
                    "response_expression": response,
                    "response_variable": response,
                    "predictors_expression": predictors,
                    "predictor_variables": [
                        token.strip()
                        for token in (predictors or "").replace("*", "+").replace(":", "+").split("+")
                        if token.strip()
                    ],
                    "interaction_terms": [
                        term.strip()
                        for term in (predictors or "").split("+")
                        if "*" in term or ":" in term
                    ],
                    "family_kind": family_kind,
                    "data_argument": kws.get("data"),
                }

                anchor = _anchor(filename, source, node)
                decisions.append(
                    AnalyticalDecision(
                        _id(), DecisionType.MODEL_DEFINITION, anchor,
                        "statistical model specification", payload
                    )
                )

                if response and response.startswith("np.log("):
                    decisions.append(
                        AnalyticalDecision(
                            _id(), DecisionType.RESPONSE_TRANSFORMATION, anchor,
                            "response transformation",
                            {**payload, "transformation": "log"}
                        )
                    )

                if payload["interaction_terms"]:
                    decisions.append(
                        AnalyticalDecision(
                            _id(), DecisionType.INTERACTION, anchor,
                            "interaction effects", payload
                        )
                    )

            # sklearn estimators
            elif func in {
                "LinearRegression", "LogisticRegression", "Ridge", "Lasso", "ElasticNet",
                "RandomForestClassifier", "RandomForestRegressor", "GradientBoostingClassifier",
                "GradientBoostingRegressor", "SVC", "SVR"
            } or func.endswith((
                ".LinearRegression", ".LogisticRegression", ".Ridge", ".Lasso", ".ElasticNet",
                ".RandomForestClassifier", ".RandomForestRegressor", ".GradientBoostingClassifier",
                ".GradientBoostingRegressor", ".SVC", ".SVR"
            )):
                family_kind = "binomial" if ("Classifier" in func or "LogisticRegression" in func or func.endswith("SVC")) else None
                decisions.append(
                    AnalyticalDecision(
                        _id(),
                        DecisionType.MODEL_DEFINITION,
                        _anchor(filename, source, node),
                        "statistical model specification",
                        {
                            "language": "python",
                            "object": target,
                            "function": func,
                            "response_expression": None,
                            "response_variable": None,
                            "predictors_expression": None,
                            "predictor_variables": [],
                            "interaction_terms": [],
                            "family_kind": family_kind,
                        },
                    )
                )

        if isinstance(node, ast.Call):
            func = _name(node.func)
            anchor = _anchor(filename, source, node)

            if func.endswith("train_test_split"):
                decisions.append(
                    AnalyticalDecision(
                        _id(), DecisionType.TRAIN_TEST_SPLIT, anchor,
                        "data partitioning",
                        {"language": "python", "method": func}
                    )
                )

            if func.endswith(("StandardScaler", "MinMaxScaler", "SimpleImputer")):
                decisions.append(
                    AnalyticalDecision(
                        _id(), DecisionType.PREPROCESSING, anchor,
                        "preprocessing",
                        {"language": "python", "method": func}
                    )
                )

            if func.endswith((
                "accuracy_score", "precision_score", "recall_score",
                "f1_score", "roc_auc_score", "confusion_matrix"
            )):
                decisions.append(
                    AnalyticalDecision(
                        _id(), DecisionType.CLASSIFICATION_METRIC, anchor,
                        "classification evaluation",
                        {"language": "python", "metric_function": func}
                    )
                )

    return sorted(decisions, key=lambda d: (d.anchor.line_start, d.type.value))
