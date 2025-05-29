import RPi.GPIO as GPIO
import time

# Set up GPIO mode
GPIO.setmode(GPIO.BCM)

# Define the servo pin (use the GPIO number, not the physical pin number)
SERVO_PIN = 18  # GPIO18, you can change this to match your connection

# Set up the servo pin as output
GPIO.setup(SERVO_PIN, GPIO.OUT)

# Create PWM instance with frequency 50Hz
pwm = GPIO.PWM(SERVO_PIN, 50)

# Start PWM with 0% duty cycle
pwm.start(0)

def set_angle(angle):
    # Convert angle to duty cycle
    # Most servos work with duty cycles between 2.5% and 12.5%
    # 2.5% = 0 degrees, 12.5% = 180 degrees
    duty = angle / 18 + 2.5
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.3)  # Give the servo time to move

try:
    while True:
        # Move to 0 degrees
        set_angle(0)
        time.sleep(1)
        
        # Move to 90 degrees
        set_angle(90)
        time.sleep(1)
        
        # Move to 180 degrees
        set_angle(180)
        time.sleep(1)
        
        # Move back to 90 degrees
        set_angle(90)
        time.sleep(1)

except KeyboardInterrupt:
    # Clean up
    pwm.stop()
    GPIO.cleanup()
