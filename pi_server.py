from flask import Flask, request, jsonify
import serial
import time

app = Flask(__name__)

# Configure serial connection to Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)  # Adjust port and baud rate as needed
time.sleep(2)  # Wait for Arduino to reset

@app.route('/detections', methods=['POST'])
def receive_detections():
    try:
        detections = request.json
        
        # Process detections
        for detection in detections:
            # Format data for Arduino
            # Example: "CLASS:confidence:x1,y1,x2,y2\n"
            data = f"{detection['class']}:{detection['confidence']:.2f}:{','.join(map(str, detection['bbox']))}\n"
            
            # Send to Arduino
            arduino.write(data.encode())
            time.sleep(0.01)  # Small delay between messages
        
        return jsonify({"status": "success"})
    
    except Exception as e:
        print(f"Error processing detections: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)