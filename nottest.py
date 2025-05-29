from flask import Flask, send_from_directory
from flask_socketio import SocketIO
import serial
import RPi.GPIO as GPIO
import time
import sys

app = Flask(__name__, static_folder='web')
socketio = SocketIO(app, cors_allowed_origins="*")

# Adjust the port to match your Arduino's
arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=0.05)

def cleanup():
    try:
        pwm.stop()
        GPIO.cleanup()
    except:
        pass

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the servo pin
SERVO_PIN = 18

# Set up the servo pin as output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM instance with frequency 50Hz
pwm = GPIO.PWM(SERVO_PIN, 50)

# Start PWM with 0% duty cycle
pwm.start(0)

def set_angle(angle):
    try:
        # Constrain angle between 0 and 180
        angle = max(0, min(180, angle))
        
        # Convert angle to duty cycle
        duty = angle / 18 + 2.5
        
        # Ensure duty cycle is within valid range
        duty = max(2.5, min(12.5, duty))
        
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)
    except Exception as e:
        print(f"Error setting angle: {e}")
        cleanup()
        sys.exit(1)

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@socketio.on('move')
def handle_move(data):
    try:
        command = data.get('command', '')
        # Increased motor speeds and balanced left/right
        if command == 'U':  # Forward - increased speed
            arduino.write(b"S:1.0:1.0\n")
        elif command == 'D':  # Backward - increased speed
            arduino.write(b"S:-1.0:-1.0\n")
        elif command == 'L':  # Turn left - balanced speeds
            arduino.write(b"S:-0.5:0.5\n")
        elif command == 'R':  # Turn right - balanced speeds
            arduino.write(b"S:0.5:-0.5\n")
        elif command == 'S':  # Stop
            arduino.write(b"S:0:0\n")
        elif command == 'open':
            set_angle(90)
        elif command == 'close':
            set_angle(0)

    except Exception as e:
        print(f"Error sending to Arduino: {e}")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)