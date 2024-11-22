import streamlit as st
import pandas as pd
from datetime import datetime
# import time

# Set page configuration
st.set_page_config(layout="wide",
                   page_title="Attendance System",
                   page_icon="👋",
                   initial_sidebar_state="collapsed")

# Function to read today's attendance from CSV
def get_today_attendance():
    try:
        df = pd.read_csv("attendance.csv")  # Load the CSV
    except FileNotFoundError:
        st.error("Attendance file not found.")
        return 0

    # Get today's date in the same format as in the CSV ('DD-MM-YYYY')
    today_date = datetime.today().strftime("%d-%m-%Y")

    # Check if 'Date' column exists
    if "Date" not in df.columns:
        st.error("The 'Date' column is missing in the CSV file.")
        return 0

    # Strip extra spaces from column names (in case there are any)
    df.columns = df.columns.str.strip()

    # Strip extra spaces from the 'Date' column (in case there are any)
    df["Date"] = df["Date"].str.strip()

    # Count how many times today's date appears in the 'Date' column
    date_count = df[df["Date"] == today_date].shape[0]

    # Return the count of today's date occurrences
    return date_count

# Home page content
st.markdown(
    """
    <style>
        h1 {
            color: #2E86C1;
            font-size: 3.5rem;
            text-align: center;
        }
        .counter {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            color: #A8C7D3;
            margin: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3, = st.columns(3)

with col2:
    st.image("asset/TARS.png", use_column_width=True)

st.markdown(
    """
    <h1 style="font-size: 50px; text-align: center; color: #007bff;">
        Welcome to <br> <span style="color: #e0516e; font-style: italic; font-weight: bold">TARS TECHNOLOGIES</span>
    </h1>
    """, 
    unsafe_allow_html=True
)

# Add a GIF or image as a header

# Get the count of entries for today (total present count) on the home page
total_entries_today = get_today_attendance()

# Display Total Entries count on the home page
st.markdown(f"<div class='counter'>Total Present for Today: {total_entries_today}</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    if st.button("📍 Mark Attendance", use_container_width=True):
        st.switch_page("pages/Attendence.py")

with col2:
    if st.button("👨‍💼 Register Employee", use_container_width=True):
        st.switch_page("pages/Register Empoyee.py")  

with col3:
    if st.button("📊 View Attendance", use_container_width=True):
        st.switch_page("pages/View Attendence.py")

# Footer
st.markdown(
    """
    <div style="text-align: center; color: grey; font-size: 0.8rem;">
        Made with ❤️ by Tars Technologies Team
    </div>
    """,
    unsafe_allow_html=True,
)
