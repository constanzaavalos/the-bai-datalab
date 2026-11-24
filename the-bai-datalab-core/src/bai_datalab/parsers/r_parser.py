from __future__ import annotations

import re
import uuid
from dataclasses import dataclass

from bai_datalab.models import (
    AnalyticalDecision,
    AnchorScope,
    DecisionType,
    SourceAnchor,
)


ASSIGNMENT_MODEL_RE = re.compile(
    r"(?P<object>[A-Za-z.][A-Za-z0-9._]*)\s*<-\s*(?P<function>lm|glm|lmer|glmer|gam|coxph|polr|multinom|glm\.nb)\s*\(",
    re.MULTILINE,
)
CALL_START_RE = re.compile(
    r"\b(?P<function>AIC|step|stepAIC|vif|bptest|qqnorm|confusionMatrix|roc|initial_split|createDataPartition)\s*\("
)


@dataclass(frozen=True)
class RBlock:
    text: str
    line_start: int
    line_end: int


def _id() -> str:
    return f"decision_{uuid.uuid4().hex[:10]}"


def _strip_comments_preserve_newlines(source: str) -> str:
    """
    Remove comments while preserving line structure.
    Handles # outside quoted strings.
    """
    out = []
    in_single = False
    in_double = False
    escaped = False

    for ch in source:
        if escaped:
            out.append(ch)
            escaped = False
            continue

        if ch == "\\":
            out.append(ch)
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            out.append(ch)
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            out.append(ch)
            continue

        if ch == "#" and not in_single and not in_double:
            # Replace comment text with spaces until newline.
            out.append(" ")
            continue

        out.append(ch)

    # second pass: trim comment tails line-by-line more conservatively
    cleaned = []
    for line in "".join(out).splitlines(True):
        in_single = in_double = escaped = False
        cut = None
        for i, ch in enumerate(line):
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
            elif ch == '"' and not in_single:
                in_double = not in_double
            elif ch == "#" and not in_single and not in_double:
                cut = i
                break
        if cut is None:
            cleaned.append(line)
        else:
            suffix = "\n" if line.endswith("\n") else ""
            cleaned.append(line[:cut] + suffix)
    return "".join(cleaned)


def _line_number(source: str, char_index: int) -> int:
    return source.count("\n", 0, char_index) + 1


def _extract_balanced_call(source: str, open_paren_index: int) -> tuple[int, int] | None:
    depth = 0
    in_single = False
    in_double = False
    escaped = False

    for i in range(open_paren_index, len(source)):
        ch = source[i]

        if escaped:
            escaped = False
            continue

        if ch == "\\":
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            continue

        if in_single or in_double:
            continue

        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return open_paren_index, i + 1

    return None


def _block_from_match(source: str, match: re.Match) -> RBlock | None:
    open_paren = source.find("(", match.start())
    if open_paren < 0:
        return None

    bounds = _extract_balanced_call(source, open_paren)
    if bounds is None:
        return None

    _, end = bounds
    start = match.start()
    text = source[start:end]

    return RBlock(
        text=text,
        line_start=_line_number(source, start),
        line_end=_line_number(source, end - 1),
    )


def _inside_call(block_text: str) -> str:
    start = block_text.find("(")
    end = block_text.rfind(")")
    if start < 0 or end < 0 or end <= start:
        return ""
    return block_text[start + 1:end]


def _split_top_level_args(text: str) -> list[str]:
    args = []
    current = []
    depth = 0
    in_single = False
    in_double = False
    escaped = False

    for ch in text:
        if escaped:
            current.append(ch)
            escaped = False
            continue

        if ch == "\\":
            current.append(ch)
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            current.append(ch)
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            current.append(ch)
            continue

        if not in_single and not in_double:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 0:
                args.append("".join(current).strip())
                current = []
                continue

        current.append(ch)

    tail = "".join(current).strip()
    if tail:
        args.append(tail)

    return args


def _normalise_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _extract_formula(call_body: str) -> tuple[str | None, str | None]:
    args = _split_top_level_args(call_body)
    if not args:
        return None, None

    # Formula is normally the first unnamed argument.
    formula = None
    for arg in args:
        if "=" not in arg.split("~", 1)[0]:
            if "~" in arg:
                formula = arg
                break

    if not formula or "~" not in formula:
        return None, None

    response, predictors = formula.split("~", 1)
    return _normalise_space(response), _normalise_space(predictors)


def _extract_named_arg(call_body: str, name: str) -> str | None:
    for arg in _split_top_level_args(call_body):
        if "=" not in arg:
            continue
        lhs, rhs = arg.split("=", 1)
        if lhs.strip() == name:
            return _normalise_space(rhs)
    return None


def _response_base_and_transform(response: str | None) -> tuple[str | None, str | None]:
    if not response:
        return None, None

    log_match = re.fullmatch(r"log\s*\((.+)\)", response)
    if log_match:
        return _normalise_space(log_match.group(1)), "log"

    sqrt_match = re.fullmatch(r"sqrt\s*\((.+)\)", response)
    if sqrt_match:
        return _normalise_space(sqrt_match.group(1)), "sqrt"

    return response, None


def _interaction_terms(predictors: str | None) -> list[str]:
    if not predictors:
        return []

    terms = []
    for token in re.split(r"\s*\+\s*", predictors):
        token = token.strip()
        if "*" in token or ":" in token:
            terms.append(token)
    return terms


def _model_decisions(filename: str, source: str) -> list[AnalyticalDecision]:
    decisions = []

    for match in ASSIGNMENT_MODEL_RE.finditer(source):
        block = _block_from_match(source, match)
        if block is None:
            continue

        object_name = match.group("object")
        function_name = match.group("function")
        call_body = _inside_call(block.text)
        response_expr, predictors = _extract_formula(call_body)
        response_var, transformation = _response_base_and_transform(response_expr)
        interactions = _interaction_terms(predictors)
        family = _extract_named_arg(call_body, "family")

        anchor = SourceAnchor(
            artifact=filename,
            line_start=block.line_start,
            line_end=block.line_end,
            excerpt=block.text,
            scope=AnchorScope.BLOCK if block.line_end > block.line_start else AnchorScope.LINE,
        )

        predictor_variables = sorted(set(
            re.findall(r"\b[A-Za-z.][A-Za-z0-9._]*\b", predictors or "")
        ))
        family_kind = None
        if family:
            lower_family = family.lower()
            if "binomial" in lower_family:
                family_kind = "binomial"
            elif "poisson" in lower_family:
                family_kind = "poisson"
            elif "gaussian" in lower_family:
                family_kind = "gaussian"
        if function_name in {"polr", "multinom"}:
            family_kind = "categorical"
        elif function_name == "coxph":
            family_kind = "survival"
        elif function_name == "glm.nb":
            family_kind = "negative_binomial"

        payload = {
            "language": "r",
            "object": object_name,
            "function": function_name,
            "response_expression": response_expr,
            "response_variable": response_var,
            "predictors_expression": predictors,
            "predictor_variables": predictor_variables,
            "interaction_terms": interactions,
            "family": family,
            "family_kind": family_kind,
            "data_argument": _extract_named_arg(call_body, "data"),
        }

        decisions.append(
            AnalyticalDecision(
                id=_id(),
                type=DecisionType.MODEL_DEFINITION,
                anchor=anchor,
                concept="statistical model specification",
                payload=payload,
            )
        )

        if transformation:
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.RESPONSE_TRANSFORMATION,
                    anchor=anchor,
                    concept="response transformation",
                    payload={
                        **payload,
                        "transformation": transformation,
                    },
                )
            )

        if interactions:
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.INTERACTION,
                    anchor=anchor,
                    concept="interaction effects",
                    payload={
                        **payload,
                        "interaction_terms": interactions,
                    },
                )
            )

    return decisions


def _other_call_decisions(filename: str, source: str) -> list[AnalyticalDecision]:
    decisions = []

    for match in CALL_START_RE.finditer(source):
        block = _block_from_match(source, match)
        if block is None:
            continue

        function_name = match.group("function")
        args = _split_top_level_args(_inside_call(block.text))
        anchor = SourceAnchor(
            artifact=filename,
            line_start=block.line_start,
            line_end=block.line_end,
            excerpt=block.text,
            scope=AnchorScope.BLOCK if block.line_end > block.line_start else AnchorScope.LINE,
        )

        if function_name == "AIC":
            models = [_normalise_space(a) for a in args if a]
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.MODEL_COMPARISON,
                    anchor=anchor,
                    concept="information-criterion model comparison",
                    payload={"criterion": "AIC", "models": models, "language": "r"},
                )
            )

        elif function_name in {"step", "stepAIC"}:
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.MODEL_SELECTION,
                    anchor=anchor,
                    concept="automated model selection",
                    payload={"method": function_name, "arguments": [_normalise_space(a) for a in args], "language": "r"},
                )
            )

        elif function_name in {"vif", "bptest", "qqnorm"}:
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.DIAGNOSTIC_CHECK,
                    anchor=anchor,
                    concept="model diagnostics",
                    payload={"diagnostic": function_name, "arguments": [_normalise_space(a) for a in args], "language": "r"},
                )
            )

        elif function_name in {"confusionMatrix", "roc"}:
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.CLASSIFICATION_METRIC,
                    anchor=anchor,
                    concept="classification evaluation",
                    payload={"metric_function": function_name, "arguments": [_normalise_space(a) for a in args], "language": "r"},
                )
            )

        elif function_name in {"initial_split", "createDataPartition"}:
            decisions.append(
                AnalyticalDecision(
                    id=_id(),
                    type=DecisionType.TRAIN_TEST_SPLIT,
                    anchor=anchor,
                    concept="data partitioning",
                    payload={"method": function_name, "arguments": [_normalise_space(a) for a in args], "language": "r"},
                )
            )

    return decisions


def parse_r_script(filename: str, source: str) -> list[AnalyticalDecision]:
    cleaned = _strip_comments_preserve_newlines(source)

    decisions = [
        *_model_decisions(filename, cleaned),
        *_other_call_decisions(filename, cleaned),
    ]

    return sorted(
        decisions,
        key=lambda d: (
            d.anchor.line_start,
            d.anchor.line_end,
            d.type.value,
        ),
    )
