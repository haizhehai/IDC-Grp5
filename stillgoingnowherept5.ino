#include "CytronMotorDriver.h" // Include "Cytron Motor Library"

// Maker Line Sensor Pin Connection
#define IR_LEFT  6
#define IR_RIGHT 7
#define IR_MID 8

// Configure the motor driver.
CytronMD motor1(PWM_PWM, 3, 9);   // motor 1 = Left motor, M1A = Pin 3, M1B = Pin 9.
CytronMD motor2(PWM_PWM, 10, 11); // motor 2 = right motor, M2A = Pin 10, M2B = Pin 11.

bool ignoreFirstTurn = false; // Flag to ignore the first turn

void setup()
{

 pinMode(IR_LEFT, INPUT);
 pinMode(IR_RIGHT, INPUT);
 pinMode(IR_MID, INPUT);
 Serial.begin(115200);

}

void robotStop() {
    motor1.setSpeed(0);     // Motor 1 stops.
    motor2.setSpeed(0);     // Motor 2 stops.
}

void robotReverse() {
    motor1.setSpeed(150);   // Motor 1 runs forward.
    motor2.setSpeed(150);   // Motor 2 runs forward.
}

void robotForward() {
    motor1.setSpeed(-150);   // Motor 1 runs backward.
    motor2.setSpeed(-150);   // Motor 2 runs backward.
}

void robotTurnLeft() {
    motor1.setSpeed(-100);    // Motor 1 runs forward.
    motor2.setSpeed(100); // Motor 2 runs backward.
    delay(1000); // Adjust delay for the turn duration
}

void robotTurnRight() {
    motor1.setSpeed(100);   // Motor 1 runs backward.
    motor2.setSpeed(-100);    // Motor 2 runs forward.
    delay(1000); // Adjust delay for the turn duration
}



void lineTrace() {
   while (true) {
     if (digitalRead(IR_LEFT) == LOW &&
         digitalRead(IR_RIGHT) == LOW && digitalRead(IR_MID) == HIGH) {
       robotForward();
     }
     else if (digitalRead(IR_LEFT) == LOW &&
         digitalRead(IR_RIGHT) == LOW ) {
       robotForward();

     }
     else if (digitalRead(IR_LEFT) == LOW &&
            digitalRead(IR_RIGHT) == HIGH) {
           robotTurnLeft();
           delay(100); 
           
     }
     else if (digitalRead(IR_LEFT) == HIGH &&
              digitalRead(IR_RIGHT) == LOW) {
       robotTurnRight();
       
       delay(100); 
     }
     else if (digitalRead(IR_LEFT) == HIGH &&
              digitalRead(IR_RIGHT) == HIGH && digitalRead(IR_MID)==HIGH) {
       
       robotStop();
       
       break;
     }
       else if (digitalRead(IR_LEFT) == HIGH && digitalRead(IR_MID) == HIGH && digitalRead (IR_RIGHT) ==LOW){
      
      robotTurnRight();
      delay(1500); 
     }
   }
 }
  
void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n'); // Read the command until newline

        if (command.equals("milk")) {
            ignoreFirstTurn = true; // Set flag to ignore the first turn
            motor1.setSpeed(-100);
            motor2.setSpeed(100);// Turn 90 degrees left
            delay(1000); // Adjust delay as necessary for the turn
            lineTrace(); // Start line tracing after the turn
        } else if (command.equals("water")) {
            ignoreFirstTurn = true; // Set flag to ignore the first turn
            motor1.setSpeed(100);
            motor2.setSpeed(100);// Turn 90 degrees left
            delay(100);
            lineTrace();
        }

        else if (command.equals("stop")){
          robotStop();
        }
        // Start line tracing
        lineTrace();
    } else {
        // Check for other commands
        if (Serial.available() > 0) {
            String command = Serial.readStringUntil('\n'); // Read the command until newline
            if (command.equals("burger") || command.equals("sandwich") || command.equals("hotdog")) {
                // Execute original line tracing behavior
                motor1.setSpeed(100);
                motor2.setSpeed(100);// Turn 90 degrees left
                delay(100);
                lineTrace();
            
         }
        }
    }
    
}
