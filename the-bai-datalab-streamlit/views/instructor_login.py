import streamlit as st

from auth import authenticate_instructor, instructor_is_authenticated
from bai_ui.branding import PROVENANCE


st.markdown("## 🔐 Instructor sign in")
st.caption(PROVENANCE)

if instructor_is_authenticated():
    st.success("Instructor access is already active in this browser session.")
    if st.button("Open Instructor Dashboard", type="primary"):
        st.switch_page("views/instructor.py")
    st.stop()

st.write(
    "Instructor analytics contain cohort-level and student-session information. "
    "Authentication is required before the dashboard is added to the application navigation."
)

with st.form("instructor_login_form", clear_on_submit=False):
    username = st.text_input(
        "Instructor username",
        autocomplete="username",
    )
    password = st.text_input(
        "Password",
        type="password",
        autocomplete="current-password",
    )
    submitted = st.form_submit_button(
        "Sign in",
        type="primary",
        use_container_width=True,
    )

if submitted:
    try:
        if authenticate_instructor(username, password):
            st.success("Instructor access granted.")
            st.rerun()
        else:
            st.error("Incorrect instructor credentials.")
    except RuntimeError as exc:
        st.error(str(exc))

st.caption(
    "Credentials are read from Streamlit secrets and are not stored in the SQLite learning log."
)
