import sys
from pathlib import Path

import streamlit as st

_CORE_SRC = Path(__file__).resolve().parents[1] / "the-bai-datalab-core" / "src"
if _CORE_SRC.exists() and str(_CORE_SRC) not in sys.path:
    sys.path.insert(0, str(_CORE_SRC))

from auth import instructor_is_authenticated
from bai_ui.branding import APP_NAME
from bai_ui.participant import (
    init_participant_session,
    log_page_view,
)


st.set_page_config(
    page_title=APP_NAME,
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

student_pages = [
    st.Page("views/home.py", title="Home", icon="🏠", default=True),
    st.Page("views/model_doctor.py", title="Model Doctor", icon="🩺", url_path="model_doctor"),
    st.Page("views/model_court.py", title="Model Court", icon="⚖️", url_path="model_court"),
    st.Page("views/leakage_detective.py", title="Leakage Detective", icon="🕵️", url_path="leakage_detective"),
    st.Page("views/break_the_model.py", title="Break the Model", icon="💥", url_path="break_the_model"),
    st.Page("views/uncertainty_lab.py", title="Uncertainty Lab", icon="🎲", url_path="uncertainty_lab"),
    st.Page("views/human_vs_ai.py", title="Human vs AI Statistician", icon="🤖", url_path="human_vs_ai"),
]

more_pages = [
    st.Page("views/discussions.py", title="Discussions", icon="💬", url_path="discussions"),
    st.Page("views/team.py", title="Meet the Team", icon="👥", url_path="team"),
    st.Page("views/challenge.py", title="Challenge", icon="⚡", url_path="challenge"),
]

if instructor_is_authenticated():
    access_pages = [
        st.Page("views/instructor.py", title="Instructor Dashboard", icon="📊", url_path="instructor"),
        st.Page("views/instructor_logout.py", title="Sign out", icon="🚪", url_path="instructor-sign-out"),
    ]
else:
    access_pages = [
        st.Page("views/instructor_login.py", title="Instructor sign in", icon="🔐", url_path="instructor-sign-in"),
    ]

pg = st.navigation(
    {
        "Student": student_pages,
        "More": more_pages,
        "Instructor access": access_pages,
    },
    position="sidebar",
)

init_participant_session()
log_page_view(pg.title)

pg.run()
