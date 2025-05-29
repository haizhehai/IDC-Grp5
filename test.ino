// Include the Cytron Motor Driver Library
#include <CytronMotorDriver.h>

// Define the motor pins
// Motor 1 (Left Motor)
const int MOTOR1_PWM_PIN = 3;  // Connect to PWM pin of Cytron driver for Motor 1
const int MOTOR1_DIR_PIN = 9;  // Connect to DIR pin of Cytron driver for Motor 1

// Motor 2 (Right Motor)
const int MOTOR2_PWM_PIN = 10; // Connect to PWM pin of Cytron driver for Motor 2
const int MOTOR2_DIR_PIN = 11; // Connect to DIR pin of Cytron driver for Motor 2

// Create CytronMotorDriver objects.
// Assuming your Cytron driver is configured for PWM_DIR mode.
// If it's a different mode (e.g., SIGNED_PWM), you might need to adjust.
CytronMotorDriver motor1(PWM_DIR, MOTOR1_PWM_PIN, MOTOR1_DIR_PIN); // Left motor
CytronMotorDriver motor2(PWM_DIR, MOTOR2_PWM_PIN, MOTOR2_DIR_PIN); // Right motor

void setup() {
  Serial.begin(9600); // Match baud rate with Python/serial setup
                      // Consider increasing to 115200 for faster updates if needed.
  Serial.println("Arduino Ready with Cytron Motor Drivers.");
  Serial.println("Waiting for commands in format: S:<left_float>:<right_float>");
  
  // It's good practice to ensure motors are stopped at startup.
  // The Cytron library usually defaults to stopped, but explicit is good.
  motor1.setSpeed(0);
  motor2.setSpeed(0);
}

void loop() {
  if (Serial.available() > 0) {
    String commandString = Serial.readStringUntil('\n');
    commandString.trim(); // Remove any leading/trailing whitespace
    parseAndDrive(commandString);
  }
}

void parseAndDrive(String cmdStr) {
  // Add debug output for raw input
  Serial.print("Raw input: ");
  Serial.println(cmdStr);
  
  // Expected format: "S:<float_left>:<float_right>"
  if (cmdStr.startsWith("S:")) {
    String valuesPart = cmdStr.substring(2); // Remove the "S:" prefix
    int separatorIndex = valuesPart.indexOf(':');

    if (separatorIndex > 0 && separatorIndex < valuesPart.length() - 1) {
      String leftSpeedStr = valuesPart.substring(0, separatorIndex);
      String rightSpeedStr = valuesPart.substring(separatorIndex + 1);

      // Debug the parsed strings
      Serial.print("Left speed string: ");
      Serial.println(leftSpeedStr);
      Serial.print("Right speed string: ");
      Serial.println(rightSpeedStr);

      float leftSpeedFloat = leftSpeedStr.toFloat();
      float rightSpeedFloat = rightSpeedStr.toFloat();

      // Debug the converted floats
      Serial.print("Left speed float: ");
      Serial.println(leftSpeedFloat);
      Serial.print("Right speed float: ");
      Serial.println(rightSpeedFloat);

      driveMotors(leftSpeedFloat, rightSpeedFloat);
    } else {
      Serial.print("Invalid command format: ");
      Serial.println(cmdStr);
    }
  } else if (cmdStr.length() > 0) {
    Serial.print("Unknown command: ");
    Serial.println(cmdStr);
  }
}

void driveMotors(float leftFloat, float rightFloat) {
  // Constrain inputs to be between -1.0 and 1.0
  leftFloat = constrain(leftFloat, -1.0, 1.0);
  rightFloat = constrain(rightFloat, -1.0, 1.0);

  // Convert float speed (-1.0 to 1.0) to integer speed for Cytron library (-255 to 255)
  int leftMotorSpeedCytron = (int)(leftFloat * 255.0);
  int rightMotorSpeedCytron = (int)(rightFloat * 255.0);

  // Debug the final motor speeds
  Serial.print("Final motor speeds - Left: ");
  Serial.print(leftMotorSpeedCytron);
  Serial.print(" Right: ");
  Serial.println(rightMotorSpeedCytron);

  // Send speed commands to the motors using the Cytron library
  motor1.setSpeed(leftMotorSpeedCytron);
  motor2.setSpeed(rightMotorSpeedCytron);
}