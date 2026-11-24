from __future__ import annotations

import re


def parse_model_output(name: str, content: bytes) -> dict:
    text = content.decode("utf-8", errors="replace")

    out = {
        "name": name,
        "has_residual_summary": "Residuals:" in text,
        "has_coefficients": "Coefficients:" in text or "coef" in text.lower(),
        "has_confusion_matrix": "Confusion Matrix" in text,
        "has_auc": bool(re.search(r"\bAUC\b|area under", text, re.I)),
        "coefficients": [],
    }

    patterns = {
        "r_squared": r"(?:Multiple )?R-squared:\s*([0-9.]+)",
        "adjusted_r_squared": r"Adjusted R-squared:\s*([0-9.]+)",
        "aic": r"\bAIC\b\s*[:=]\s*(-?[0-9.]+)",
        "bic": r"\bBIC\b\s*[:=]\s*(-?[0-9.]+)",
        "auc": r"\bAUC\b\s*[:=]\s*([0-9.]+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.I)
        if m:
            out[key] = float(m.group(1))

    # Basic R coefficient-table extraction
    coeff_section = re.search(
        r"Coefficients:\s*\n(?P<body>.*?)(?:\n\s*\n|Residual standard error|Null deviance|AIC:|$)",
        text,
        re.S,
    )

    if coeff_section:
        lines = coeff_section.group("body").splitlines()
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.lower().startswith("estimate"):
                continue

            parts = stripped.split()
            if len(parts) >= 4:
                try:
                    estimate = float(parts[1])
                    std_error = float(parts[2])
                    statistic = float(parts[3])
                except Exception:
                    continue

                p_value = None
                if len(parts) >= 5:
                    raw_p = parts[4].replace("<", "")
                    try:
                        p_value = float(raw_p)
                    except Exception:
                        pass

                out["coefficients"].append({
                    "term": parts[0],
                    "estimate": estimate,
                    "std_error": std_error,
                    "statistic": statistic,
                    "p_value": p_value,
                })

    return out
