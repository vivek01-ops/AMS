import streamlit as st
import cv2
import face_recognition
import pickle
import numpy as np
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import time

# Streamlit Page Configuration
st.set_page_config(
    layout="centered",
    page_title="Attendance System",
    page_icon="📍",
    initial_sidebar_state="collapsed"
)

# Google Sheets Authentication and Setup
def authenticate_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file('sheet.json', scopes=scope)
    client = gspread.authorize(creds)
    return client

def log_attendance_google_sheets(empid, name):
    client = authenticate_google_sheets()
    if not client:
        return

    try:
        sheet = client.open("TARS ATTENDANCE").sheet1
        current_time = datetime.now()
        current_date = current_time.strftime('%d/%m/%Y')
        current_timestamp = current_time.strftime('%I:%M:%S %p')

        records = sheet.get_all_records()
        today_records = [
            record for record in records
            if record['EMPID'] == str(empid) and 
               record['Date'] == current_date
        ]
        open_records = [
            record for record in today_records 
            if not record['Out Time']
        ]

        if open_records:
            last_open_record = open_records[-1]
            row_index = records.index(last_open_record) + 2
            try:
                sheet.update_cell(row_index, 4, current_timestamp)
                if last_open_record['In Time']:
                    total_hours = calculate_total_hours(last_open_record['In Time'], current_timestamp)
                    sheet.update_cell(row_index, 5, total_hours)
                sheet.update_cell(row_index, 6, 'Present')
                st.success(f"Out Time logged for {name}")
            except Exception as e:
                st.error(f"Error updating Out Time: {e}")
        else:
            create_new_entry(sheet, empid, name, current_timestamp, current_date)
    except Exception as e:
        st.error(f"Attendance Logging Error: {e}")

def create_new_entry(sheet, empid, name, current_timestamp, current_date):
    try:
        sheet.append_row([
            str(empid), name, current_timestamp, '', '', 'Partially Present', current_date
        ])
        st.toast(f"In Time logged for {name} (EMPID: {empid})", icon="✅")
        time.sleep(.5)
    except Exception as e:
        st.error(f"Error creating new entry: {e}")

def calculate_total_hours(in_time_str, out_time_str):
    in_time = datetime.strptime(in_time_str, '%I:%M:%S %p')
    out_time = datetime.strptime(out_time_str, '%I:%M:%S %p')
    total_hours = out_time - in_time
    total_seconds = total_hours.total_seconds()
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}"

# Load Known Face Encodings
encode_file = 'EncodeFile.p'
if os.path.exists(encode_file):
    with open(encode_file, 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    encodeListKnown, studentIds = encodeListKnownWithIds
else:
    st.error("Encoding file not found. Please check the path and file.")
    st.stop()

# Page Layout
st.title("Mark Attendence")
st.subheader("Capture Image to Log Attendance", divider="red")
# Camera Input
if st.button("Open camera to mark attendence", use_container_width=True, type="secondary"):
    uploaded_image = st.camera_input("Capture Image to Log Attendance")

    if uploaded_image is not None:
        # Convert the uploaded image to OpenCV format
        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        frame = cv2.imdecode(file_bytes, 1)

        # Display the captured image
        st.image(frame, channels="BGR", caption="Captured Image")

        # Process the captured frame for face recognition
        imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        # Detect faces in the frame
        faceCurFrame = face_recognition.face_locations(imgS)
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

        if faceCurFrame:
            for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

                # If a match is found
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    empid = studentIds[matchIndex]
                    name = studentIds[matchIndex]  # Assuming name and empid are the same for simplicity
                    st.success(f"Attendance Marked: Welcome, {name}!")
                    log_attendance_google_sheets(empid, name)
                    break
                else:
                    st.warning("No matching face found. Please try again.")
        else:
            st.warning("No face detected. Please capture a clearer image.")
