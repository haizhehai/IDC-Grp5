import RPi.GPIO as GPIO
import time
import sys

def cleanup():
    try:
        pwm.stop()
        GPIO.cleanup()
    except:
        pass

try:
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

    # Test with a single movement first
    print("Moving to 90 degrees...")
    set_angle(90)
    time.sleep(1)
    
    print("Moving to 0 degrees...")
    set_angle(0)
    time.sleep(1)
    
    print("Moving to 180 degrees...")
    set_angle(180)
    time.sleep(1)
    
    print("Moving back to 90 degrees...")
    set_angle(90)
    time.sleep(1)

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()
    sys.exit(1)

finally:
    cleanup()
