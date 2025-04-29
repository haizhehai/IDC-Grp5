#include "CytronMotorDriver.h" // Include Cytron Motor Library

// 5 Array Sensor Pin Connection
#define LEFT_SENSOR A0
#define LEFT_MID_SENSOR A1
#define MID_SENSOR A2
#define RIGHT_MID_SENSOR A3
#define RIGHT_SENSOR A4

// Motor Configuration
CytronMD motor1(PWM_PWM, 3, 9);   // Motor 1 = Left motor (M1A=Pin 3, M1B=Pin 9)
CytronMD motor2(PWM_PWM, 10, 11); // Motor 2 = Right motor (M2A=Pin 10, M2B=Pin 11)

void setup() {
  // Sensor Pin Setup
  pinMode(LEFT_SENSOR, INPUT);
  pinMode(LEFT_MID_SENSOR, INPUT);
  pinMode(MID_SENSOR, INPUT);
  pinMode(RIGHT_MID_SENSOR, INPUT);
  pinMode(RIGHT_SENSOR, INPUT);

  Serial.begin(115200);
}

void move(int leftSpeed, int rightSpeed) {
  motor1.setSpeed(leftSpeed);   // Left Motor
  motor2.setSpeed(rightSpeed); // Right Motor
}

void loop() {
  int left = digitalRead(LEFT_SENSOR);
  int leftMid = digitalRead(LEFT_MID_SENSOR);
  int mid = digitalRead(MID_SENSOR);
  int rightMid = digitalRead(RIGHT_MID_SENSOR);
  int right = digitalRead(RIGHT_SENSOR);

  // Check if all sensors detect black (LOW)
  if (left == LOW && leftMid == LOW && mid == LOW && rightMid == LOW && right == LOW) {
    move(200, 200);
    Serial.println("All Black Detected: Moving forward briefly...");
    delay(100); // Move forward for 100ms

    // Re-read sensors after moving
    left = digitalRead(LEFT_SENSOR);
    leftMid = digitalRead(LEFT_MID_SENSOR);
    mid = digitalRead(MID_SENSOR);
    rightMid = digitalRead(RIGHT_MID_SENSOR);
    right = digitalRead(RIGHT_SENSOR);

    if (left == LOW && leftMid == LOW && mid == LOW && rightMid == LOW && right == LOW) {
      move(0, 0); // Stop if still all black
      Serial.println("Still All Black: Stopping!");
    }
    return; // Skip rest of the loop after handling this condition
  }

  // Line following logic
  if (left == HIGH && leftMid == LOW && mid == LOW && rightMid == LOW && right == HIGH) {
    move(200, 200);
    Serial.println("Moving Forward");
  }
  else if (left == HIGH && leftMid == HIGH && mid == LOW && rightMid == LOW && right == HIGH) {
    move(190, 200);
    Serial.println("Moving Forward");
  }
  else if (left == HIGH && leftMid == LOW && mid == LOW && rightMid == HIGH && right == HIGH) {
    move(200, 190);
    Serial.println("Moving Forward");
  }
  else if (left == LOW && leftMid == LOW && mid == LOW && rightMid == HIGH && right == HIGH) {
    move(150, 200);
    Serial.println("Hard Left");
  }
  else if (left == HIGH && leftMid == HIGH && mid == LOW && rightMid == LOW && right == LOW) {
    move(200, 150);
    Serial.println("Spin Left");
  }
  else if (left == LOW && leftMid == LOW && mid == HIGH && rightMid == HIGH && right == HIGH) {
    move(100, 200);
    Serial.println("Slight Right");
  }
  else if (left == HIGH && leftMid == HIGH && mid == HIGH && rightMid == LOW && right == LOW) {
    move(200, 100);
    Serial.println("Sharply Right");
  }
  else if (left == HIGH && leftMid == HIGH && mid == HIGH && rightMid == HIGH && right == LOW) {
    move(200, 200);
    delay(100);
    Serial.println("Hard Right");
  }
  else if (left == LOW && leftMid == HIGH && mid == HIGH && rightMid == HIGH && right == HIGH) {
    move(200, 200);
    delay(100);
    Serial.println("Spin Right");
  }
  else {
    move(200, 200);
    delay(100);
    move(0, 0);
    Serial.println("Stop - Line Lost!");
  }

  delay(10); // Small delay for stability
}
