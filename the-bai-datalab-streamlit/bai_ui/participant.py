from __future__ import annotations

import uuid
from urllib.parse import urlencode

import streamlit as st

from persistence import log_activity

PARTICIPANT_CODE_KEY = "participant_code"
PILOT_SESSION_KEY = "pilot_session_id"
LAST_LOGGED_PAGE_KEY = "_last_logged_page"


def init_participant_session() -> None:
    """Initialise pilot session ID and auto-capture ?code= from the URL (Qualtrics)."""
    if PILOT_SESSION_KEY not in st.session_state:
        st.session_state[PILOT_SESSION_KEY] = uuid.uuid4().hex

    url_code = st.query_params.get("code")
    if isinstance(url_code, list):
        url_code = url_code[0] if url_code else ""
    url_code = str(url_code or "").strip().upper()

    if url_code:
        st.session_state[PARTICIPANT_CODE_KEY] = url_code
    elif PARTICIPANT_CODE_KEY not in st.session_state:
        st.session_state[PARTICIPANT_CODE_KEY] = ""

    # Keep ?code= in the URL so reloads or direct links preserve the participant code
    active_code = st.session_state.get(PARTICIPANT_CODE_KEY, "")
    if active_code and st.query_params.get("code") != active_code:
        st.query_params["code"] = active_code


def get_participant_code() -> str:
    """Return the active pseudonymous participant code, or 'anonymous'."""
    init_participant_session()
    return st.session_state.get(PARTICIPANT_CODE_KEY, "").strip().upper() or "anonymous"


def get_pilot_session_id() -> str:
    """Return the per-browser-session UUID."""
    init_participant_session()
    return str(st.session_state[PILOT_SESSION_KEY])


def log_page_view(page_title: str) -> None:
    """Log a page_view event once each time the user navigates to a new page."""
    init_participant_session()
    if st.session_state.get(LAST_LOGGED_PAGE_KEY) == page_title:
        return
    st.session_state[LAST_LOGGED_PAGE_KEY] = page_title
    log_activity(
        participant_code=get_participant_code(),
        session_id=get_pilot_session_id(),
        lab=page_title,
        event_type="page_view",
    )


def _post_survey_url(code: str) -> str:
    try:
        base_url = str(st.secrets.get("pilot", {}).get("post_survey_url", "")).strip()
    except Exception:
        base_url = ""
    if not base_url:
        return ""
    if not code or code == "anonymous":
        return base_url
    sep = "&" if "?" in base_url else "?"
    return f"{base_url}{sep}{urlencode({'code': code})}"


def render_participant_sidebar() -> None:
    """Render an unobtrusive participant code widget and optional post-survey link in the sidebar."""
    init_participant_session()
    active_code = st.session_state.get(PARTICIPANT_CODE_KEY, "")

    with st.sidebar:
        st.divider()
        if active_code:
            st.markdown(f"🎟️ **Participant:** `{active_code}`")
            with st.expander("Change code", expanded=False):
                new_code = st.text_input(
                    "Participant code",
                    value=active_code,
                    placeholder="e.g. BAI-P66J",
                    key="_sidebar_change_code_input",
                    label_visibility="collapsed",
                )
                if st.button("Update code", key="_sidebar_update_code_btn", use_container_width=True):
                    cleaned = new_code.strip().upper()
                    st.session_state[PARTICIPANT_CODE_KEY] = cleaned
                    if cleaned:
                        st.query_params["code"] = cleaned
                    elif "code" in st.query_params:
                        del st.query_params["code"]
                    st.rerun()
        else:
            st.caption("🎟️ **Pilot participant code**")
            entered = st.text_input(
                "Participant code",
                value="",
                placeholder="e.g. BAI-P66J (optional)",
                key="_sidebar_enter_code_input",
                label_visibility="collapsed",
            )
            if st.button("Save code", key="_sidebar_save_code_btn", use_container_width=True):
                cleaned = entered.strip().upper()
                if cleaned:
                    st.session_state[PARTICIPANT_CODE_KEY] = cleaned
                    st.query_params["code"] = cleaned
                    st.rerun()

        survey_url = _post_survey_url(active_code)
        if survey_url:
            st.link_button(
                "📝 Finish & Open Post-Survey →",
                survey_url,
                use_container_width=True,
            )
