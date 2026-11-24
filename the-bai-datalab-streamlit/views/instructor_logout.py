import streamlit as st

from auth import logout_instructor


logout_instructor()
st.success("Instructor session closed.")
st.caption("The Instructor Dashboard has been removed from navigation for this browser session.")

if st.button("Return to Model Doctor", type="primary"):
    st.switch_page("views/model_doctor.py")
