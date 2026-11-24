from __future__ import annotations

import csv
import io
import math
from collections import Counter
from statistics import mean

MISSING_TOKENS = {"", "NA", "N/A", "NULL", "NONE", "."}


def _is_missing(value):
    return value.strip().upper() in MISSING_TOKENS


def _to_float(value):
    try:
        return float(value)
    except Exception:
        return None


def _pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None

    xv = [x for x, _ in pairs]
    yv = [y for _, y in pairs]
    mx, my = mean(xv), mean(yv)

    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = math.sqrt(sum((x - mx) ** 2 for x in xv))
    dy = math.sqrt(sum((y - my) ** 2 for y in yv))

    if dx == 0 or dy == 0:
        return None

    return num / (dx * dy)


def analyse_delimited_dataset(name, content):
    text = content.decode("utf-8-sig", errors="replace")
    delimiter = "\t" if name.lower().endswith(".tsv") else ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))

    if not rows:
        return {
            "name": name, "rows": 0, "columns": 0,
            "column_names": [], "variables": {}, "high_correlations": []
        }

    header, data = rows[0], rows[1:]
    width = len(header)
    data = [row + [""] * (width - len(row)) for row in data]

    variables = {}

    for i, col in enumerate(header):
        values = [row[i] for row in data]
        present = [v for v in values if not _is_missing(v)]
        counts = Counter(present)
        numeric = [_to_float(v) for v in present]
        inferred = "numeric" if present and all(x is not None for x in numeric) else "categorical"

        info = {
            "type": inferred,
            "n": len(values),
            "missing_n": len(values) - len(present),
            "missing_pct": round(100 * (len(values) - len(present)) / len(values), 2) if values else 0.0,
            "unique_n": len(counts),
            "constant": len(counts) <= 1 and bool(present),
            "binary": len(counts) == 2,
        }

        if info["binary"]:
            total = sum(counts.values())
            info["minority_pct"] = round(100 * min(counts.values()) / total, 2) if total else 0.0

        if inferred == "numeric" and numeric:
            nums = [x for x in numeric if x is not None]
            info.update({
                "min": min(nums),
                "max": max(nums),
                "mean": round(mean(nums), 6),
            })

        variables[col] = info

    numeric_cols = [
        c for c, info in variables.items()
        if info["type"] == "numeric" and not info["constant"]
    ]

    numeric_values = {
        col: [
            None if _is_missing(row[header.index(col)]) else _to_float(row[header.index(col)])
            for row in data
        ]
        for col in numeric_cols
    }

    high_correlations = []

    for i, a in enumerate(numeric_cols):
        for b in numeric_cols[i + 1:]:
            corr = _pearson(numeric_values[a], numeric_values[b])
            if corr is not None and abs(corr) >= 0.8:
                high_correlations.append({
                    "var1": a,
                    "var2": b,
                    "correlation": round(corr, 4),
                })

    missing_cells = sum(info["missing_n"] for info in variables.values())
    total_cells = max(len(data) * len(header), 1)

    return {
        "name": name,
        "rows": len(data),
        "columns": len(header),
        "column_names": header,
        "missing_cells": missing_cells,
        "missing_pct": round(100 * missing_cells / total_cells, 2),
        "variables": variables,
        "high_correlations": high_correlations,
    }
