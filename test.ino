void setup() {
  Serial.begin(9600);
  // Initialize any other components (LEDs, motors, etc.)
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    
    // Parse the data
    // Format: "CLASS:confidence:x1,y1,x2,y2"
    int firstColon = data.indexOf(':');
    int secondColon = data.indexOf(':', firstColon + 1);
    
    String className = data.substring(0, firstColon);
    float confidence = data.substring(firstColon + 1, secondColon).toFloat();
    String bbox = data.substring(secondColon + 1);
    
    // Process the detection
    // Example: Turn on LED for specific class
    if (className == "target_class" && confidence > 0.5) {
      // Do something (e.g., turn on LED, move motor, etc.)
    }
  }
}