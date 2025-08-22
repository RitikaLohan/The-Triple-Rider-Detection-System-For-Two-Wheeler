// triple_alert.ino
const int ALERT_PIN = 8; // buzzer or LED pin
const unsigned long ALERT_DURATION_MS = 5000; // how long to alert

void setup() {
  pinMode(ALERT_PIN, OUTPUT);
  digitalWrite(ALERT_PIN, LOW);
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    if (cmd == "ALERT") {
      unsigned long end = millis() + ALERT_DURATION_MS;
      while (millis() < end) {
        digitalWrite(ALERT_PIN, HIGH);
        delay(200);
        digitalWrite(ALERT_PIN, LOW);
        delay(200);
      }
      // optional: send ack
      Serial.println("ALERT_ACK");
    }
  }
}