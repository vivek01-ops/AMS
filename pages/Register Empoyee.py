import os
import streamlit as st
from PIL import Image
import cv2
import face_recognition
import pickle
import numpy as np

# Configure the Streamlit page
st.set_page_config(
    layout="centered",
    page_title="Register Employee",
    page_icon="👨‍💼",
    initial_sidebar_state="collapsed",
)

# Directory to save captured images
output_dir = "Images"
os.makedirs(output_dir, exist_ok=True)

# Set up page title and layout
st.title("Employee Registration")

# Employee details input
st.subheader("Enter Employee Details", divider="red")
user_id = st.text_input("Employee ID:", placeholder="Enter employee ID")
user_name = st.text_input("Employee Name:", placeholder="Enter employee name")

st.caption("Press enter to turn on the camera")

# Capture image and automate encoding process
if user_id and user_name:
    st.subheader("Camera Input", divider="red")
    captured_image = st.camera_input("Register...")

    if captured_image:
        # Save the image
        sanitized_name = f"{user_id}_{user_name}".replace(" ", "")
        img_filename = os.path.join(output_dir, f"{sanitized_name}.png")
        img = Image.open(captured_image)
        img.save(img_filename)

        st.image(img, caption="Captured image", use_column_width=True)
        st.success(f"Image captured and saved as {sanitized_name}.png.")

        # Automatically encode and save face data
        st.info("Encoding and saving face data...")

        # Load the newly saved image
        try:
            pil_image = Image.open(img_filename)
            pil_image = pil_image.convert("RGB")
            img_array = np.array(pil_image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)

            # Find encoding
            encode = face_recognition.face_encodings(img_bgr)
            if encode:
                encode_data = encode[0]

                # Load existing encodings if the file exists
                try:
                    with open("EncodeFile.p", "rb") as file:
                        encodeListKnownWithIds = pickle.load(file)
                        encodeListKnown, studentIds = encodeListKnownWithIds
                except FileNotFoundError:
                    encodeListKnown, studentIds = [], []

                # Append new data
                encodeListKnown.append(encode_data)
                studentIds.append(sanitized_name)

                # Save updated encodings
                with open("EncodeFile.p", "wb") as file:
                    pickle.dump([encodeListKnown, studentIds], file)

                st.success("Face data encoded and saved successfully!")
            else:
                st.error("No face detected in the captured image. Please try again.")
        except Exception as e:
            st.error(f"Error during encoding: {e}")
else:
    st.warning("*Warning:* Please provide both Employee ID and Employee Name to proceed.")
