from picamera2 import Picamera2
import cv2
import time
import threading
import queue
from ultralytics import YOLO
from collections import Counter

# Explicitly start window thread
cv2.startWindowThread()

# Create window first before capturing
cv2.namedWindow("YOLO + PiCamera Feed", cv2.WINDOW_NORMAL)
cv2.resizeWindow("YOLO + PiCamera Feed", 640, 480)

class VideoStreamThread:
    def __init__(self, width=640, height=480, fps=30):
        # Initialize PiCamera
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"},
            controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
        )
        self.picam2.configure(config)
        self.picam2.start()
        
        # Initialize the queue and thread
        self.frame_queue = queue.Queue(maxsize=1)
        self.stopped = False
        
        # Get the first frame
        frame = self.picam2.capture_array()
        if frame is not None:
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        else:
            raise RuntimeError("Could not read from camera")
    
    def start(self):
        # Start the thread to read frames from the video stream
        threading.Thread(target=self.update, daemon=True).start()
        return self
    
    def update(self):
        while not self.stopped:
            # Capture frame
            frame = self.picam2.capture_array()
            if frame is None:
                self.stopped = True
                break
            
            # Convert to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # If queue is full, remove the oldest frame
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    pass
            
            # Add the frame to the queue
            self.frame_queue.put(frame)
    
    def read(self):
        try:
            return self.frame_queue.get(timeout=1.0)
        except queue.Empty:
            return self.current_frame
    
    def stop(self):
        self.stopped = True
        self.picam2.stop()

class ModelInferenceThread:
    def __init__(self, model_path='plush.pt', conf=0.6, iou=0.4, max_det=5):
        # Load the YOLO model
        self.model = YOLO(model_path)
        self.conf = conf
        self.iou = iou
        self.max_det = max_det
        
        # Initialize queues
        self.input_queue = queue.Queue(maxsize=1)
        self.output_queue = queue.Queue(maxsize=1)
        
        self.stopped = False
    
    def start(self):
        threading.Thread(target=self.inference_loop, daemon=True).start()
        return self
    
    def inference_loop(self):
        while not self.stopped:
            try:
                frame = self.input_queue.get(timeout=1.0)
                results = self.model(frame, conf=self.conf, iou=self.iou, max_det=self.max_det)
                
                if self.output_queue.full():
                    try:
                        self.output_queue.get_nowait()
                    except queue.Empty:
                        pass
                
                self.output_queue.put((frame, results))
                
            except queue.Empty:
                continue
    
    def submit_frame(self, frame):
        if self.input_queue.full():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                pass
        self.input_queue.put(frame)
    
    def get_results(self):
        try:
            return self.output_queue.get(block=False)
        except queue.Empty:
            return None
    
    def stop(self):
        self.stopped = True

def main():
    print("Starting video stream...")
    video_stream = VideoStreamThread(width=640, height=480, fps=30).start()
    time.sleep(1.0)
    
    print("Loading YOLO model...")
    model_thread = ModelInferenceThread(model_path='plush.pt').start()
    
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
            resized_frame = cv2.resize(frame, (320, 240))
            
            # Process every third frame to reduce load
            if frame_count % 3 == 0:
                model_thread.submit_frame(resized_frame.copy())
            
            # Get inference results if available
            results = model_thread.get_results()
            if results:
                frame, yolo_results = results
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
            cv2.imshow('YOLO + PiCamera Feed', display_frame)
            
            # Break the loop if 'q' is pressed
            if cv2.waitKey(5) & 0xFF == ord('q'):
                break
    
    finally:
        print("Stopping threads...")
        video_stream.stop()
        model_thread.stop()
        cv2.destroyAllWindows()
        print("Clean shutdown complete")

if __name__ == "__main__":
    main()