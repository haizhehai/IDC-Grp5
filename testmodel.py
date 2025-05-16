import cv2
import os
import numpy as np

from datetime import datetime
from ultralytics import YOLO

# Load the YOLO model with your weights
model = YOLO('best.pt')

# Initialize webcam (0 for default camera, or try 1,2,etc. for external cameras)
cap = cv2.VideoCapture(1)

# Set camera resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Set camera FPS (try 30 or 60 depending on your camera)
cap.set(cv2.CAP_PROP_FPS, 30)

# Optional: Reduce buffer size to minimize latency
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while True:
    # Read frame from webcam
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    
    # Run inference on the frame with optimized settings
    results = model(frame, conf=0.45, iou=0.6, max_det=16, vid_stride=2) 
    
    # Plot the results on the frame
    annotated_frame = results[0].plot()
    
    # Display the frame with detections
    cv2.imshow('Object Detection', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()