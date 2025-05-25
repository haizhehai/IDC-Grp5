//this is the final code for the IR motor thing
#include "CytronMotorDriver.h" //Include "Cytron Motor Library"
  
// Maker Line Sensor Pin Connection
#define IR_LEFT  6
#define IR_RIGHT   7
#define IR_MID 8

  
// Configure the motor driver.
CytronMD motor1(PWM_PWM, 3, 9);   // motor 1 = Left motor, M1A = Pin 3, M1B = Pin 9.
CytronMD motor2(PWM_PWM, 10, 11); // motor 2= right motor, M2A = Pin 10, M2B = Pin 11.

void robotStop()
{
 motor1.setSpeed(0);     // Motor 1 stops.
 motor2.setSpeed(0);     // Motor 2 stops.
}


void robotReverse()
{
 motor1.setSpeed(150);   // Motor 1 runs forward.
 motor2.setSpeed(150);   // Motor 2 runs forward.
} 


void robotForward()
{
 motor1.setSpeed(-150);   // Motor 1 runs backward.
 motor2.setSpeed(-150);   // Motor 2 runs backward.
}


void robotTurnLeft()
{
 motor1.setSpeed(-100);    // Motor 1 runs forward.
 motor2.setSpeed(100); // Motor 2 runs backward.

}


void robotTurnRight()
{
 motor1.setSpeed(100);   // Motor 1 runs backward.
 motor2.setSpeed(-100);    // Motor 2 runs forkward.
}
void setup()
{

 pinMode(IR_LEFT, INPUT);
 pinMode(IR_RIGHT, INPUT);
 
 Serial.begin(115200);

}


void loop()
{


   while (true) {
     if (digitalRead(IR_LEFT) == LOW &&
         digitalRead(IR_RIGHT) == LOW && digitalRead(IR_MID) == HIGH) {
       robotForward();
       Serial.println("Forward");
     }
     else if (digitalRead(IR_LEFT) == LOW &&
         digitalRead(IR_RIGHT) == LOW ) {
       robotForward();

       Serial.println("Forward");
     }
     else if (digitalRead(IR_LEFT) == LOW &&
            digitalRead(IR_RIGHT) == HIGH) {
           robotTurnLeft();
           delay(100); 
           Serial.println("Left");
     }
     else if (digitalRead(IR_LEFT) == HIGH &&
              digitalRead(IR_RIGHT) == LOW) {
       robotTurnRight();
       Serial.println("Right");
       delay(100); 
     }
     else if (digitalRead(IR_LEFT) == HIGH &&
              digitalRead(IR_RIGHT) == HIGH && digitalRead(IR_MID)==HIGH) {
       Serial.println("stop");
       robotStop();
       
       break;
     }
       else if (digitalRead(IR_LEFT) == HIGH && digitalRead(IR_MID) == HIGH && digitalRead (IR_RIGHT) ==LOW){
      Serial.print("hardturn");
      robotTurnRight();
      delay(1500); 
     }
   }
 }
