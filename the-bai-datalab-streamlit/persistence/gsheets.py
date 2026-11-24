from __future__ import annotations

import json
import sys
from typing import Any

import streamlit as st

ACTIVITY_HEADERS = [
    "timestamp_utc",
    "participant_code",
    "session_id",
    "lab",
    "case_id",
    "event_type",
    "choice",
    "response_text",
    "status",
    "score",
    "hint_level",
    "misconception",
]


def is_gsheets_configured() -> bool:
    """Return True if [google_sheets] secrets are configured."""
    try:
        cfg = st.secrets.get("google_sheets")
        if not cfg:
            return False
        has_target = bool(cfg.get("spreadsheet_url") or cfg.get("spreadsheet_id"))
        has_creds = bool(cfg.get("service_account") or cfg.get("service_account_json"))
        return has_target and has_creds
    except Exception:
        return False


@st.cache_resource(show_spinner=False)
def _get_worksheet():
    """Authenticate once and return the target gspread worksheet."""
    import gspread
    from google.oauth2.service_account import Credentials

    cfg = st.secrets["google_sheets"]
    if "service_account" in cfg:
        creds_info = dict(cfg["service_account"])
    else:
        creds_info = json.loads(str(cfg["service_account_json"]))

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
    client = gspread.authorize(creds)

    if cfg.get("spreadsheet_url"):
        spreadsheet = client.open_by_url(str(cfg["spreadsheet_url"]))
    else:
        spreadsheet = client.open_by_key(str(cfg["spreadsheet_id"]))

    worksheet_name = str(cfg.get("worksheet_name", "activity_logs")).strip() or "activity_logs"
    try:
        ws = spreadsheet.worksheet(worksheet_name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(title=worksheet_name, rows=1000, cols=len(ACTIVITY_HEADERS))

    # Ensure header row exists
    first_row = ws.row_values(1)
    if not first_row:
        ws.append_row(ACTIVITY_HEADERS, value_input_option="RAW")

    return ws


def append_activity_row(row: dict[str, Any]) -> bool:
    """Append a single activity event to Google Sheets if configured.

    Never raises to the caller so student sessions are never interrupted.
    """
    if not is_gsheets_configured():
        return False
    try:
        ws = _get_worksheet()
        values = [
            "" if row.get(col) is None else str(row.get(col))
            for col in ACTIVITY_HEADERS
        ]
        ws.append_row(values, value_input_option="RAW")
        return True
    except Exception as exc:
        print(f"[BAI DataLab] Google Sheets logging skipped: {exc}", file=sys.stderr)
        return False
