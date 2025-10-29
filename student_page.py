"""Student management"""
import pandas as pd
import streamlit as st

from core import logger, supabase_client


# -----------------------------------------------------------
# Data Functions
# -----------------------------------------------------------
@st.cache_data(ttl=600, max_entries=200)  # Cache for 10 minutes
def fetch_students():
    """Fetch all students from the database."""
    try:
        response = (
            supabase_client.table("student")
            .select("id","student_name","year","preferred_day")
            .order("student_name")
            .execute()
        )
        return response.data
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.exception("Error fetching students %s", e)
        st.error("Something went wrong while fetching students")
        return []

def refresh_students():
    """Clear cached fetch_students data."""
    fetch_students.clear()

students_data = fetch_students()
st.title(":material/manage_accounts: Student Management")
st.subheader(':material/patient_list: Student List')
st.dataframe(pd.DataFrame(students_data), width='stretch')

st.divider()
st.subheader(':material/person_add: Add New Student')
student_name = st.text_input("Enter student name", placeholder="Type student name here...")
year = st.selectbox(
    "Select student's year", 
    options=[3,4,5],
    index=None,
    placeholder="student is in year"
)
preferred_day = st.selectbox(
    "Select preferred day", 
    options=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
    index=None,
    placeholder="student attends class on"
)

if st.button("Add Student", type="primary"):
    if student_name:
        try:
            supabase_client.table("student").insert({
            "student_name": student_name,
            "year": year,
            "preferred_day": preferred_day
            }).execute()
            st.success(f":material/done_all: Student '{student_name}' added successfully!")
            refresh_students()
            st.rerun()
        except (ValueError, ConnectionError, RuntimeError) as e:
            st.error(f"Error adding student: {str(e)}")
    else:
        st.warning("Please enter a student name")
