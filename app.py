"""Main APP combining all pages"""
import streamlit as st

# -----------------------------------------------------------
# Navigation
# -----------------------------------------------------------
with st.sidebar:
    st.title(":material/school: Sunitha11plus")
    st.divider()

pages = [
    st.Page("attendance_page.py", title="Attendance & Fee", icon=":material/app_registration:"),
    st.Page("student_page.py", title="Student Management", icon=":material/manage_accounts:"),
    st.Page("student_details.py", title="Student Details", icon=":material/table_chart_view:")
]

pg = st.navigation(pages)

pg.run()
