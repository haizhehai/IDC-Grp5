import serial
import keyboard  # pip install keyboard
import time

ser = serial.Serial('COM3', 9600)  # Change to your port (e.g., /dev/ttyUSB0 on Linux)
time.sleep(2)  # Give Arduino time to reset

print("Use arrow keys to control the robot. Press Esc to quit.")

while True:
    if keyboard.is_pressed('up'):
        ser.write(b'F')
        time.sleep(0.2)
    elif keyboard.is_pressed('down'):
        ser.write(b'B')
        time.sleep(0.2)
    elif keyboard.is_pressed('left'):
        ser.write(b'L')
        time.sleep(0.2)
    elif keyboard.is_pressed('right'):
        ser.write(b'R')
        time.sleep(0.2)
    elif keyboard.is_pressed('space'):
        ser.write(b'S')
        time.sleep(0.2)
    elif keyboard.is_pressed('esc'):
        print("Exiting...")
        break
