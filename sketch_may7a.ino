const int handSensorPin = 2;

bool handIsRaised = false;
bool raisePrompted = false;
unsigned long raiseStartTime = 0;
const unsigned long raiseDurationLimit = 5000;  // 5 seconds

void setup() {
  Serial.begin(9600);
  pinMode(handSensorPin, INPUT);
}

void loop() {
  int sensorValue = digitalRead(handSensorPin);  // LOW = hand present

  // Hand just placed
  if (sensorValue == LOW && !handIsRaised) {
    Serial.println("Hand raised");
    raiseStartTime = millis();
    handIsRaised = true;
    raisePrompted = false;
  }

  // Hand still up too long
  else if (sensorValue == LOW && handIsRaised) {
    if (millis() - raiseStartTime >= raiseDurationLimit) {
      Serial.println("Lower your hand");
      // Don’t spam — reset so this message only prints once
      raiseStartTime = millis();  // Reset so it doesn't repeat too often
    }
  }

  // Hand just lowered
  else if (sensorValue == HIGH && handIsRaised) {
    Serial.println("Hand lowered");
    handIsRaised = false;
    raisePrompted = false;
  }

  // Hand is lowered and we haven’t prompted yet
  else if (sensorValue == HIGH && !handIsRaised && !raisePrompted) {
    Serial.println("Raise your hand");
    raisePrompted = true;
  }

  delay(100);
}
