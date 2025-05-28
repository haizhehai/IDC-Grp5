import cv2
import os
import numpy as np
import time
import threading
import queue
from datetime import datetime
from ultralytics import YOLO
from collections import Counter
import requests
import json

# Explicitly start window thread
cv2.startWindowThread()

# Create window first before capturing
cv2.namedWindow("Object Detection", cv2.WINDOW_NORMAL)

class VideoStreamThread:
    def __init__(self, src="http://10.163.206.60:8080/video", width=360, height=360, fps=30):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Initialize the queue and thread
        self.frame_queue = queue.Queue(maxsize=1)
        self.stopped = False
        
        # Get the first frame
        ret, frame = self.cap.read()
        if ret:
            self.current_frame = frame
        else:
            raise RuntimeError("Could not read from camera")
    
    def start(self):
        # Start the thread to read frames from the video stream
        threading.Thread(target=self.update, daemon=True).start()
        return self
    
    def update(self):
        # Keep looping infinitely until the thread is stopped
        while not self.stopped:
            # Read the next frame from the stream
            ret, frame = self.cap.read()
            if not ret:
                self.stopped = True
                break
            
            # If queue is full, remove the oldest frame
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
                
            # Add the frame to the queue
            self.frame_queue.put(frame)
    
    def read(self):
        # Return the most recent frame
        try:
            return self.frame_queue.get(timeout=1.0)
        except queue.Empty:
            return self.current_frame  # Return the last frame if queue is empty
    
    def stop(self):
        # Indicate that the thread should be stopped
        self.stopped = True
        # Release the video stream resources
        self.cap.release()


class ModelInferenceThread:
    def __init__(self, model_path='plush.pt', conf=0.25, iou=0.45, max_det=10, pi_url="http://192.168.215.79:5000/detections"):
        # Load the YOLO model
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.max_det = max_det
        
        # Initialize queues
        self.input_queue = queue.Queue(maxsize=1)
        self.output_queue = queue.Queue(maxsize=1)
        
        self.stopped = False
        self.pi_url = pi_url  # URL of the Raspberry Pi server
    
    def start(self):
        # Start the thread for model inference
        threading.Thread(target=self.inference_loop, daemon=True).start()
        return self
    
    def inference_loop(self):
        while not self.stopped:
            try:
                # Get a frame from the input queue
                frame = self.input_queue.get(timeout=1.0)
                
                # Run inference
                results = self.model(frame, conf=self.conf, iou=self.iou, max_det=self.max_det)
                
                # Process detections
                detections = []
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        detections.append({
                            'class': r.names[cls],
                            'confidence': conf,
                            'bbox': [x1, y1, x2, y2],
                            'timestamp': datetime.now().isoformat()
                        })
                
                # Send detections to Raspberry Pi
                try:
                    response = requests.post(
                        self.pi_url,
                        json=detections,
                        timeout=0.5  # Short timeout to not block the main loop
                    )
                    if response.status_code != 200:
                        print(f"Error sending detections: {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to send detections: {e}")
                
                # If output queue is full, remove the oldest result
                if self.output_queue.full():
                    try:
                        self.output_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                # Put the results in the output queue
                self.output_queue.put((frame, results))
                
            except queue.Empty:
                continue
    
    def submit_frame(self, frame):
        # Submit a new frame for inference
        if self.input_queue.full():
            try:
                self.input_queue.get_nowait()  # Remove old frame if queue is full
            except queue.Empty:
                pass
        self.input_queue.put(frame)
    
    def get_results(self):
        # Get the inference results
        try:
            return self.output_queue.get(block=False)
        except queue.Empty:
            return None
    
    def stop(self):
        # Indicate that the thread should be stopped
        self.stopped = True


def main():
    # Initialize video stream and model inference threads
    print("Starting video stream...")
    try:
        video_stream = VideoStreamThread(src="http://10.163.206.60:8080/video", width=360, height=360, fps=30).start()
    except RuntimeError as e:
        print(f"Error: {e}")
        print("Please check that:")
        print("1. Your camera is properly connected")
        print("2. No other application is using the camera")
        print("3. You have granted camera permissions to the application")
        return
    
    print("Loading YOLO model...")
    model_thread = ModelInferenceThread(
        model_path='plush.pt',
        conf=0.25,
        iou=0.45,
        max_det=10,
        pi_url="http://192.168.215.79:5000/detections"  # Add port and endpoint
    ).start()
    
    # Initialize variables for FPS calculation
    fps_counter = 0
    fps_start_time = time.time()
    fps = 0
    
    # Initialize counter for objects
    object_counter = Counter()
    
    print("Starting detection loop...")
    
    # Placeholder for the latest annotated frame
    latest_annotated_frame = None
    frame_count = 0
    
    try:
        while True:
            frame_count += 1
            frame = video_stream.read()

            # Resize frame for faster processing
            resized_frame = cv2.resize(frame, (640, 360))
            
            # Process every third frame to reduce load
            if frame_count % 3 == 0:
                # Submit the frame for inference
                model_thread.submit_frame(resized_frame.copy())
            
            # Get inference results if available
            results = model_thread.get_results()
            if results:
                resized_frame, yolo_results = results
                # Get the current detections
                current_detections = yolo_results[0].boxes.cls.cpu().numpy()
                # Count objects in current frame
                current_counts = Counter([yolo_results[0].names[int(cls)] for cls in current_detections])
                # Update total counts
                object_counter = current_counts
                
                # Process the results and draw on the frame
                annotated_frame = yolo_results[0].plot()
                latest_annotated_frame = annotated_frame
            
            # Display the annotated frame if available, otherwise show the original frame
            display_frame = latest_annotated_frame if latest_annotated_frame is not None else frame
            
            # Calculate and display FPS
            fps_counter += 1
            if (time.time() - fps_start_time) > 1.0:
                fps = fps_counter / (time.time() - fps_start_time)
                fps_counter = 0
                fps_start_time = time.time()
            
            # Display FPS on the frame
            cv2.putText(display_frame, f"FPS: {fps:.2f}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display object counts
            y_offset = 70
            for class_name, count in object_counter.items():
                text = f"{class_name}: {count}"
                cv2.putText(display_frame, text, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_offset += 30
            
            # Show the frame
            cv2.imshow('Object Detection', display_frame)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    
    finally:
        # Clean up
        print("Stopping threads...")
        video_stream.stop()
        model_thread.stop()
        cv2.destroyAllWindows()
        print("Clean shutdown complete")


if __name__ == "__main__":
    main()