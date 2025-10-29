"""Student details"""
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

def fetch_student_fees(student_id):
    """Fetch fee payment history for a student."""
    try:
        response = (
            supabase_client.table("student_fee")
            .select("*")
            .eq("student_id", student_id)
            .order("date_paid", desc=True)
            .execute()
        )
        return response.data
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.exception("Error fetching student fees: %s", e)
        st.error("Error loading fee history.")
        return []

def fetch_student_attendance(student_id):
    """Fetch attendance history for a student."""
    try:
        response = (
            supabase_client.table("student_attendance")
            .select("*")
            .eq("student_id", student_id)
            .order("class_attended_date", desc=True)
            .execute()
        )
        return response.data
    except Exception as e: # pylint: disable=broad-exception-caught
        logger.exception("Error fetching student attendance: %s", e)
        st.error("Error loading attendance history.")
        return []

# ---------- UI ----------
def create_student_picker(key_prefix=""):
    """Dropdown to select a student."""
    students = fetch_students()
    if not students:
        st.warning("No students found. Please add students first.")
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

# ---------- Page starts here ----------
st.title(":material/table_chart_view: Student Details")

selected_student = create_student_picker("details")

if not selected_student:
    st.info(":material/keyboard_arrow_up: Select a student to view their details")
    st.stop()  # stop rendering the rest of the page

# --- Student Header Card ---
st.subheader(":material/inbox_text_person: Student Information")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(":material/person: Name", selected_student["student_name"])

with col2:
    st.metric(":material/school: Year", f"Year {selected_student['year']}")

with col3:
    st.metric(
        ":material/calendar_today: Preferred Day",
        selected_student["preferred_day"],
    )

st.divider()

# --- Fetch Data ---
fees = fetch_student_fees(selected_student["id"])
attendance = fetch_student_attendance(selected_student["id"])

# --- Summary ---
total_fees = sum(fee["fee_amount"] for fee in fees) if fees else 0
total_classes = len(attendance)

st.subheader(":material/analytics: Summary")
col1, col2 = st.columns(2)

with col1:
    st.metric(
        ":material/payments: Total Fees Paid",
        f"£{total_fees}",
        delta=f"{len(fees)} payments",
    )

with col2:
    st.metric(
        ":material/event_available: Classes Attended",
        total_classes,
        delta="sessions",
    )

st.divider()

# --- Fee & Attendance Tables ---
col1, col2 = st.columns(2)

# Fees
with col1:
    st.subheader(":material/account_balance_wallet: Fee Payment History")

    if fees:
        fees_df = pd.DataFrame(fees)
        display_df = pd.DataFrame({
            "Date": pd.to_datetime(fees_df["date_paid"]).dt.strftime("%d/%m/%Y"),
            "Amount": fees_df["fee_amount"].apply(lambda x: f"£{x}")
        })
        st.dataframe(display_df, hide_index=True, width='stretch', height=400)
        st.caption(f"Total: **£{total_fees}** from {len(fees)} payment(s)")
    else:
        st.info("No fee payments recorded yet.")

# Attendance
with col2:
    st.subheader(":material/event_note: Attendance History")

    if attendance:
        attendance_df = pd.DataFrame(attendance)
        display_df = pd.DataFrame({
            "Date": pd.to_datetime(attendance_df["class_attended_date"]).dt.strftime("%d/%m/%Y"),
            "Day": pd.to_datetime(attendance_df["class_attended_date"]).dt.day_name(),
        })
        st.dataframe(display_df, hide_index=True, width='stretch', height=400)
        st.caption(f"Total: **{total_classes}** class(es) attended")
    else:
        st.info("No attendance records yet.")

st.divider()

# --- Insights ---
if fees and attendance:
    st.subheader(":material/insights: Insights")

    col1, col2 = st.columns(2)

    with col1:
        latest_attendance = pd.to_datetime(attendance[0]["class_attended_date"])
        st.metric("Last Attended", latest_attendance.strftime("%d/%m/%Y"))

    with col2:
        latest_payment = pd.to_datetime(fees[0]["date_paid"])
        st.metric("Last Payment", latest_payment.strftime("%d/%m/%Y"))
