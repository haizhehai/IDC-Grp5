

#include "CytronMotorDriver.h" //Include "Cytron Motor Library"
  
// Maker Line Sensor Pin Connection
#define IR_LEFT  6
#define IR_RIGHT   7


  
// Configure the motor driver.
CytronMD motor1(PWM_PWM, 3, 9);   // motor 1 = Left motor, M1A = Pin 3, M1B = Pin 9.
CytronMD motor2(PWM_PWM, 10, 11); // motor 2= right motor, M2A = Pin 10, M2B = Pin 11.

void robotStop()
{
 motor1.setSpeed(0);     // Motor 1 stops.
 motor2.setSpeed(0);     // Motor 2 stops.
}


void robotForward()
{
 motor1.setSpeed(128);   // Motor 1 runs forward.
 motor2.setSpeed(-128);   // Motor 2 runs forward.
} 


void robotReverse()
{
 motor1.setSpeed(-128);   // Motor 1 runs backward.
 motor2.setSpeed(128);   // Motor 2 runs backward.
}


void robotTurnLeft()
{
 motor1.setSpeed(10);    // Motor 1 runs forward.
 motor2.setSpeed(10);   // Motor 2 runs backward.
}


void robotTurnRight()
{
 motor1.setSpeed(-10);   // Motor 1 runs backward.
 motor2.setSpeed(-10);    // Motor 2 runs forkward.
}
void setup()
{

 pinMode(IR_LEFT, INPUT);
 pinMode(IR_RIGHT, INPUT);
 
 Serial.begin(9600);
}

void loop()
{


   while (true) {
     if (digitalRead(IR_LEFT) == HIGH &&
         digitalRead(IR_RIGHT) == HIGH) {
       robotForward();
       Serial.println("Forward");
     }
     else if (digitalRead(IR_LEFT) == HIGH &&
            digitalRead(IR_RIGHT) == LOW) {
           robotTurnLeft();
       Serial.println("Left");
     }
     else if (digitalRead(IR_LEFT) == LOW &&
              digitalRead(IR_RIGHT) == HIGH) {
       robotTurnRight();
       Serial.println("Right");
     }
     else if (digitalRead(IR_LEFT) == LOW &&
              digitalRead(IR_RIGHT) == LOW) {
       Serial.println("stop");
       robotStop();
       
       break;
     }
   }
 }
