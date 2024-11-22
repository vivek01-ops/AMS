import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials


st.set_page_config(
    layout="wide",
    page_title="Register Employee",
    page_icon="📝",
    initial_sidebar_state="collapsed",
)
# Function to fetch data from Google Sheet
def fetch_sheet_data():
    # Path to your Google service account credentials JSON file
    creds_file = 'sheet.json'

    # Define the scope and authorize
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = Credentials.from_service_account_file(creds_file, scopes=scope)
    client = gspread.authorize(credentials)

    # Open the Google Sheet by name or URL
    sheet = client.open("TARS ATTENDANCE").sheet1  # Replace with your sheet name

    # Fetch data as a list of dictionaries and convert it to a DataFrame
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# Streamlit app
st.title('Employee Attendance Tracker')

# Fetch attendance data from Google Sheet
try:
    attendance_df = fetch_sheet_data()

    # Strip whitespace from column names
    attendance_df.columns = attendance_df.columns.str.strip()

    # Parse date and time columns
    attendance_df['Date'] = pd.to_datetime(attendance_df['Date'], format='%d-%m-%Y', errors='coerce').dt.date
    attendance_df['In Time'] = pd.to_datetime(attendance_df['In Time'].str.strip(), format='%I:%M:%S %p', errors='coerce').dt.time
    attendance_df['Out Time'] = pd.to_datetime(attendance_df['Out Time'].str.strip(), format='%I:%M:%S %p', errors='coerce').dt.time

    # Drop rows with invalid or missing data in critical columns
    attendance_df.dropna(subset=['Date'], inplace=True)

    # Calculate hours worked if both 'In Time' and 'Out Time' are available
    attendance_df['Hours Worked'] = attendance_df.apply(
        lambda row: (datetime.combine(datetime.today(), row['Out Time']) - datetime.combine(datetime.today(), row['In Time'])).seconds / 3600 
        if pd.notna(row['In Time']) and pd.notna(row['Out Time']) else None, 
        axis=1
    )

    # Dropdown for employee selection with an option to view all employees
    employee_names = attendance_df['Name'].unique()
    employee_names = list(employee_names)
    employee_names.insert(0, 'All Employees')
    selected_employee = st.selectbox('Select Employee:', employee_names)

    col1, col2 = st.columns(2)
    with col1:
        date_from = st.date_input('From Date', value=datetime(2023, 10, 1), min_value=datetime(2023, 1, 1), max_value=datetime.now())
    with col2:
        date_to = st.date_input('To Date', value=datetime.now(), min_value=datetime(2023, 1, 1), max_value=datetime.now())

    # Filter attendance based on selected employee and date range
    if selected_employee == 'All Employees':
        filtered_attendance = attendance_df[
            (attendance_df['Date'] >= pd.Timestamp(date_from)) &
            (attendance_df['Date'] <= pd.Timestamp(date_to))
        ]
    else:
        filtered_attendance = attendance_df[
            (attendance_df['Name'] == selected_employee) &
            (attendance_df['Date'] >= pd.Timestamp(date_from)) &
            (attendance_df['Date'] <= pd.Timestamp(date_to))
        ]

    # Display the filtered attendance
    if not filtered_attendance.empty:
        if selected_employee == 'All Employees':
            st.write(f"Attendance records for all employees from {date_from} to {date_to}:")
        else:
            st.write(f"Attendance records for {selected_employee} from {date_from} to {date_to}:")

        # Display the dataframe
        st.dataframe(filtered_attendance, use_container_width=True)

        # Calculate and display the total hours worked for the selected employee
        if selected_employee != 'All Employees':
            total_hours = filtered_attendance['Hours Worked'].sum()
            st.write(f"Total Hours Worked: {total_hours:.2f} hours")
    else:
        st.error('No attendance records found for the selected criteria.')
except Exception as e:
    st.error(f"An error occurred while processing data: {e}")
