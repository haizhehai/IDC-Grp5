from picamera2 import Picamera2
import cv2
import time
from ultralytics import YOLO

# Load YOLO model
model = YOLO('plush.pt')

# Initialize PiCamera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

prev_time = time.time()

while True:
    # Capture frame
    image = picam2.capture_array()

    # Convert to BGR for OpenCV
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Run YOLO inference
    results = model(image, conf=0.6, iou=0.4)

    # Annotate frame
    annotated_frame = results[0].plot()

    # Calculate FPS
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # Overlay FPS
    cv2.putText(annotated_frame, f"FPS: {fps:.2f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display
    cv2.imshow("YOLO + PiCamera Feed", annotated_frame)

    # Exit on 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
# Release resources
# cap.release()
# cv2.destroyAllWindows()

##FPS TOO SLOW :/