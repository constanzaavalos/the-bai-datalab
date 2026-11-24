from __future__ import annotations

import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "data" / "bai_datalab.db"

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    student_code TEXT NOT NULL,
    assignment_name TEXT,
    strictness TEXT NOT NULL,
    llm_provider TEXT,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS submissions (
    submission_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    artifact_name TEXT NOT NULL,
    artifact_kind TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    concept TEXT NOT NULL,
    severity TEXT NOT NULL,
    artifact TEXT,
    line_start INTEGER,
    line_end INTEGER,
    resolved INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attempts (
    attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    finding_id TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    status TEXT NOT NULL,
    score REAL NOT NULL,
    hint_level INTEGER NOT NULL DEFAULT 0,
    misconception TEXT NOT NULL DEFAULT 'none',
    created_at TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
    FOREIGN KEY(finding_id) REFERENCES findings(finding_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_findings_session ON findings(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_session ON attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_attempts_finding ON attempts(finding_id);
CREATE INDEX IF NOT EXISTS idx_findings_concept ON findings(concept);
CREATE INDEX IF NOT EXISTS idx_attempts_misconception ON attempts(misconception);
"""


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def connection(db_path: str | Path | None = None):
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA journal_mode = WAL")
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db(db_path: str | Path | None = None) -> Path:
    path = Path(db_path) if db_path else DEFAULT_DB_PATH
    with connection(path) as con:
        con.executescript(SCHEMA)
    return path


def create_session(
    student_code: str,
    assignment_name: str,
    strictness: str,
    llm_provider: str,
    artifacts: Iterable,
    db_path: str | Path | None = None,
) -> str:
    init_db(db_path)
    session_id = uuid.uuid4().hex
    now = _utcnow()
    with connection(db_path) as con:
        con.execute(
            """INSERT INTO sessions
               (session_id, student_code, assignment_name, strictness, llm_provider, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, student_code.strip() or "anonymous", assignment_name.strip(), strictness, llm_provider, now),
        )
        con.executemany(
            """INSERT INTO submissions
               (session_id, artifact_name, artifact_kind, created_at)
               VALUES (?, ?, ?, ?)""",
            [
                (session_id, art.name, getattr(art, "kind", "unknown"), now)
                for art in artifacts
            ],
        )
    return session_id


def save_findings(session_id: str, findings: Iterable, db_path: str | Path | None = None) -> None:
    with connection(db_path) as con:
        con.executemany(
            """INSERT OR REPLACE INTO findings
               (finding_id, session_id, rule_id, concept, severity, artifact, line_start, line_end, resolved)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT resolved FROM findings WHERE finding_id=?), 0))""",
            [
                (
                    f.id, session_id, f.rule_id, f.concept,
                    getattr(f.severity, "value", str(f.severity)),
                    f.anchor.artifact, f.anchor.line_start, f.anchor.line_end, f.id,
                )
                for f in findings
            ],
        )


def save_attempt(
    session_id: str,
    finding_id: str,
    attempt_number: int,
    response_text: str,
    status: str,
    score: float,
    hint_level: int,
    misconception: str,
    db_path: str | Path | None = None,
) -> None:
    with connection(db_path) as con:
        con.execute(
            """INSERT INTO attempts
               (session_id, finding_id, attempt_number, response_text, status, score, hint_level, misconception, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, finding_id, attempt_number, response_text, status, score, hint_level, misconception, _utcnow()),
        )
        if status == "resolved":
            con.execute("UPDATE findings SET resolved=1 WHERE finding_id=?", (finding_id,))


def finish_session(session_id: str, db_path: str | Path | None = None) -> None:
    with connection(db_path) as con:
        con.execute(
            "UPDATE sessions SET completed_at=? WHERE session_id=?",
            (_utcnow(), session_id),
        )


def dashboard_summary(db_path: str | Path | None = None) -> dict:
    init_db(db_path)
    with connection(db_path) as con:
        row = con.execute(
            """SELECT
                COUNT(*) AS sessions,
                COUNT(DISTINCT student_code) AS students,
                SUM(CASE WHEN completed_at IS NOT NULL THEN 1 ELSE 0 END) AS completed
               FROM sessions"""
        ).fetchone()
        finding_row = con.execute(
            """SELECT COUNT(*) AS findings,
                      SUM(resolved) AS resolved
               FROM findings"""
        ).fetchone()
        attempt_row = con.execute(
            """SELECT COUNT(*) AS attempts,
                      COALESCE(AVG(hint_level),0) AS avg_hint,
                      COALESCE(AVG(score),0) AS avg_score
               FROM attempts"""
        ).fetchone()
    findings = finding_row["findings"] or 0
    resolved = finding_row["resolved"] or 0
    return {
        "sessions": row["sessions"] or 0,
        "students": row["students"] or 0,
        "completed_sessions": row["completed"] or 0,
        "findings": findings,
        "resolved_findings": resolved,
        "resolution_rate": round(100 * resolved / findings, 1) if findings else 0.0,
        "attempts": attempt_row["attempts"] or 0,
        "avg_hint_level": round(attempt_row["avg_hint"] or 0, 2),
        "avg_score": round(attempt_row["avg_score"] or 0, 3),
    }


def concept_summary(db_path: str | Path | None = None) -> list[dict]:
    init_db(db_path)
    with connection(db_path) as con:
        rows = con.execute(
            """SELECT f.concept,
                      COUNT(*) AS findings,
                      SUM(f.resolved) AS resolved,
                      COUNT(a.attempt_id) AS attempts,
                      COALESCE(AVG(a.score),0) AS avg_score,
                      COALESCE(AVG(a.hint_level),0) AS avg_hint
               FROM findings f
               LEFT JOIN attempts a ON a.finding_id=f.finding_id
               GROUP BY f.concept
               ORDER BY findings DESC, f.concept"""
        ).fetchall()
    result=[]
    for r in rows:
        findings=r["findings"] or 0
        resolved=r["resolved"] or 0
        result.append({
            "Concept": r["concept"],
            "Findings": findings,
            "Resolved": resolved,
            "Resolution %": round(100*resolved/findings,1) if findings else 0,
            "Attempts": r["attempts"] or 0,
            "Avg score": round(r["avg_score"] or 0,3),
            "Avg hint": round(r["avg_hint"] or 0,2),
        })
    return result


def misconception_summary(db_path: str | Path | None = None) -> list[dict]:
    init_db(db_path)
    with connection(db_path) as con:
        rows=con.execute(
            """SELECT misconception, COUNT(*) AS n
               FROM attempts
               WHERE misconception <> 'none'
               GROUP BY misconception
               ORDER BY n DESC"""
        ).fetchall()
    return [{"Misconception":r["misconception"],"Occurrences":r["n"]} for r in rows]


def recent_sessions(limit: int = 50, db_path: str | Path | None = None) -> list[dict]:
    init_db(db_path)
    with connection(db_path) as con:
        rows=con.execute(
            """SELECT s.session_id, s.student_code, s.assignment_name, s.strictness,
                      s.llm_provider, s.created_at, s.completed_at,
                      COUNT(DISTINCT f.finding_id) AS findings,
                      COALESCE(SUM(f.resolved),0) AS resolved,
                      COUNT(a.attempt_id) AS attempts
               FROM sessions s
               LEFT JOIN findings f ON f.session_id=s.session_id
               LEFT JOIN attempts a ON a.session_id=s.session_id
               GROUP BY s.session_id
               ORDER BY s.created_at DESC
               LIMIT ?""", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def attempts_for_session(session_id: str, db_path: str | Path | None = None) -> list[dict]:
    with connection(db_path) as con:
        rows=con.execute(
            """SELECT a.attempt_number, f.concept, f.rule_id, a.status, a.score,
                      a.hint_level, a.misconception, a.response_text, a.created_at
               FROM attempts a
               JOIN findings f ON f.finding_id=a.finding_id
               WHERE a.session_id=?
               ORDER BY a.created_at, a.attempt_id""", (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def export_attempts_rows(db_path: str | Path | None = None) -> list[dict]:
    init_db(db_path)
    with connection(db_path) as con:
        rows=con.execute(
            """SELECT s.session_id, s.student_code, s.assignment_name, s.strictness,
                      s.llm_provider, f.rule_id, f.concept, f.severity,
                      a.attempt_number, a.status, a.score, a.hint_level,
                      a.misconception, a.response_text, a.created_at
               FROM attempts a
               JOIN sessions s ON s.session_id=a.session_id
               JOIN findings f ON f.finding_id=a.finding_id
               ORDER BY a.created_at"""
        ).fetchall()
    return [dict(r) for r in rows]
