import streamlit as st

from pages.completion_report import show_completion_report


user_id = st.session_state.get("user_id")

if user_id is None:
    st.info("Please log in from the main app to view your completion report.")
else:
    show_completion_report(user_id)
