import cv2
import face_recognition
import pickle
import os
from PIL import Image
import numpy as np

# Importing student images
folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Images in folder:", pathList)

imgList = []
studentIds = []

# Read images from the folder and store them in imgList and studentIds
for path in pathList:
    img_path = os.path.join(folderPath, path)

    # Open image using PIL to ensure correct format
    try:
        pil_image = Image.open(img_path)
        
        # Convert the image to RGB if it isn't already
        pil_image = pil_image.convert("RGB")
        
        # Convert the PIL image to a numpy array (OpenCV format)
        img = np.array(pil_image)
        
        # Convert image from RGB to BGR for OpenCV compatibility
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        # Add to the image list and student IDs
        imgList.append(img_bgr)
        studentIds.append(os.path.splitext(path)[0])  # Store student ID from image filename (without extension)
    except Exception as e:
        print(f"Failed to process image {img_path}: {e}")

print("Student IDs:", studentIds)

# Function to find encodings for each image
def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        print(f"Processing image with shape: {img.shape}")  # Debugging image shape
        
        try:
            # Attempt to get the face encoding
            encode = face_recognition.face_encodings(img)
            if encode:  # If faces are detected
                encodeList.append(encode[0])  # Add encoding to the list
            else:
                print("No faces found in image")
        except Exception as e:
            print(f"Error processing image: {e}")
    
    return encodeList

# Start encoding process
print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)  # Get encodings for all images
encodeListKnownWithIds = [encodeListKnown, studentIds]  # Store encodings with IDs
print("Encoding Complete")

# Save the encodings to a file
try:
    with open("EncodeFile.p", 'wb') as file:
        pickle.dump(encodeListKnownWithIds, file)  # Save the encodings and IDs to a file
    print("File Saved")
except Exception as e:
    print(f"Error saving the file: {e}")
