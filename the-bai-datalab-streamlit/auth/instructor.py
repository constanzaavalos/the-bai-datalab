from __future__ import annotations

import hmac

import streamlit as st


SESSION_KEY = "is_instructor"
IDENTITY_KEY = "instructor_identity"


def instructor_is_authenticated() -> bool:
    """Return whether the current Streamlit session has instructor access."""
    return bool(st.session_state.get(SESSION_KEY, False))


def _expected_credentials() -> tuple[str, str]:
    """
    Read instructor credentials from Streamlit secrets.

    Expected local structure:

    [instructor]
    username = "instructor"
    password = "change-this-password"
    """
    try:
        section = st.secrets["instructor"]
        username = str(section.get("username", "instructor"))
        password = str(section["password"])
    except Exception as exc:
        raise RuntimeError(
            "Instructor credentials are not configured. "
            "Create .streamlit/secrets.toml from secrets.example.toml."
        ) from exc

    return username, password


def authenticate_instructor(username: str, password: str) -> bool:
    """Validate credentials without storing the submitted password."""
    expected_username, expected_password = _expected_credentials()

    user_ok = hmac.compare_digest(
        username.strip(),
        expected_username,
    )
    password_ok = hmac.compare_digest(
        password,
        expected_password,
    )

    authenticated = bool(user_ok and password_ok)

    if authenticated:
        st.session_state[SESSION_KEY] = True
        st.session_state[IDENTITY_KEY] = expected_username

    return authenticated


def logout_instructor() -> None:
    """Remove instructor authentication from the current browser session."""
    st.session_state.pop(SESSION_KEY, None)
    st.session_state.pop(IDENTITY_KEY, None)
