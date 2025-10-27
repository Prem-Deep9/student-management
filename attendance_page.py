"""Attendance management"""
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

def create_student_picker(key_prefix=""):
    """Dropdown to select a student."""
    students = fetch_students()
    if not students:
        st.warning(":material/priority_high: No students found. Please add students first.")
        return None
    student_options = {s['student_name']: s for s in students}
    selected_name = st.selectbox(
        "Select student to record attendance / fee", 
        options=list(student_options.keys()),
        key=f"student_{key_prefix}",
        index=None,
        placeholder="Select Student"
    )
    if not selected_name:
        return None
    return student_options[selected_name]

# -----------------------------------------------------------
# Validations and Logic
# -----------------------------------------------------------
def validate_attendance(attendance_date, selected_student):
    """Validate and record attendance."""
    if not attendance_date:
        st.warning(":material/priority_high: Please select a date to mark attendance")
        return

    try:
        with st.spinner("Marking attendance..."):
            supabase_client.table("student_attendance").insert({
                "class_attended_date": str(attendance_date),
                "student_id": selected_student['id']
            }).execute()

        refresh_students()
        st.success(f":material/done_all: Attendance marked for {selected_student['student_name']} on {attendance_date}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception("Error marking attendance: %s", e)
        st.error("Error marking attendance.")


def validate_fee_payment(fee_date, fee_amount, selected_student):
    """Validate and record fee payment."""
    if fee_date is None:
        st.warning(":material/priority_high: Please select a payment date")
        return

    if fee_amount <= 0:
        st.warning(":material/priority_high: Please enter an amount greater than £0.00")
        return

    try:
        with st.spinner("Recording fee payment..."):
            supabase_client.table("student_fee").insert({
                "date_paid": str(fee_date),
                "student_id": selected_student['id'],
                "fee_amount": int(fee_amount)
            }).execute()

        refresh_students()
        st.success(f":material/done_all: Fee payment of £{fee_amount} recorded for {selected_student['student_name']} on {fee_date}")

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.exception("Error recording fee payment: %s", e)
        st.error("Error recording fee payment.")

# -----------------------------------------------------------
# UI
# -----------------------------------------------------------
st.title(":material/app_registration: Attendance & Fee")

student_selected = create_student_picker("attendance")

if student_selected:
    # Display selected student prominently
    st.subheader(f":material/person: {student_selected['student_name']}")
    st.divider()
    st.subheader(':material/event: Record Attendance')
    attendance_date_selected = st.date_input("Select Date (DD/MM/YYYY)", value="today", key="attendance_date", format="DD/MM/YYYY")
    if st.button("Mark Present", type="primary", key="attendance_btn"):
        validate_attendance(attendance_date_selected, student_selected)
    st.divider()
    st.subheader(':material/payments: Record Fee Payment')
    fee_date_selected = st.date_input("Payment Date (DD/MM/YYYY)", value="today", key="fee_date", format="DD/MM/YYYY")
    fee_amount_selected = st.number_input("Amount (GBP)", min_value=0, step=1, key="fee_amount")
    if st.button("Record Fee", type="primary", key="fee_btn"):
        validate_fee_payment(fee_date_selected, fee_amount_selected, student_selected)
    