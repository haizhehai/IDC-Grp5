from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import serial

app = Flask(__name__, static_folder='web')
socketio = SocketIO(app, cors_allowed_origins="*")

# Adjust the port to match your Arduino's
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@socketio.on('move')
def handle_move(data):
    try:
        command = data.get('command', '')
        # Convert directional commands to motor speeds
        if command == 'U':  # Forward
            arduino.write(b"S:0.5:0.5\n")
        elif command == 'D':  # Backward
            arduino.write(b"S:-0.5:-0.5\n")
        elif command == 'L':  # Turn left
            arduino.write(b"S:-0.3:0.3\n")
        elif command == 'R':  # Turn right
            arduino.write(b"S:0.3:-0.3\n")
        elif command == 'S':  # Stop
            arduino.write(b"S:0:0\n")
    except Exception as e:
        print(f"Error sending to Arduino: {e}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
