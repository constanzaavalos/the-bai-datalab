from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from persistence.db import (
    init_db, create_session, save_findings, save_attempt,
    dashboard_summary, concept_summary, misconception_summary,
)


def test_sqlite_roundtrip():
    with TemporaryDirectory() as td:
        db = Path(td) / "test.db"
        init_db(db)
        artifact = SimpleNamespace(name="model.R", kind="r_script")
        session = create_session("S001", "Demo", "standard", "Deterministic only", [artifact], db)
        anchor = SimpleNamespace(artifact="model.R", line_start=2, line_end=2)
        severity = SimpleNamespace(value="caution")
        finding = SimpleNamespace(
            id="f1", rule_id="RULE_1", concept="model diagnostics",
            severity=severity, anchor=anchor,
        )
        save_findings(session, [finding], db)
        save_attempt(session, "f1", 1, "I checked residual patterns and assumptions.",
                     "resolved", 0.9, 1, "none", db)
        summary = dashboard_summary(db)
        assert summary["sessions"] == 1
        assert summary["resolved_findings"] == 1
        assert concept_summary(db)[0]["Concept"] == "model diagnostics"
        assert misconception_summary(db) == []
