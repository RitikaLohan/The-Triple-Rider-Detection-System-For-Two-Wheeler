# 🚦 Triple Rider Detection System for Two-Wheelers

##  Patent Information

This project is **patented and published** under the Government of India, Intellectual Property Office.

* **Application Number:** 202311080300
* **Application Type:** Ordinary Application
* **Date of Filing:** 26/11/2023
* **Title of Invention:** *The Triple Rider Detection System for Two Wheeler*
* **Field of Invention:** Physics / IoT / AI in Traffic Safety
* **Publication Date (U/S 11A):** 29/12/2023


##  Project Overview

The **Triple Rider Detection System (TRDS)** is an **AI-powered IoT solution** designed to **automatically detect and prevent triple riding** on two-wheelers. Triple riding not only violates traffic safety laws but also leads to higher accident risks and fatalities.

Our system integrates:

* **Computer Vision / AI models** to detect the number of riders.
* **Weight and Infrared Sensors** for accurate detection in all light conditions.
* **Arduino-based Alert System** to instantly warn riders.
* **Optional IoT communication** for reporting to traffic authorities.

This project is designed as a **cost-effective, scalable, and practical safety innovation** that supports **road safety regulations** and reduces the burden on traffic police.



##  Key Features

*  **Real-Time Detection** of triple riders using AI & sensors.
*  **Low-Cost Alert System** with buzzer/LED for immediate warning.
*  **Integration with IoT** (future scope: GSM, Cloud monitoring).
*  **Traffic Violation Prevention** by discouraging unsafe riding.
*  **Published Patent** (Government of India).




##  System Architecture

1. **Detection Layer (AI + Sensors)**

   * Camera captures riders.
   * AI model + weight/IR sensors confirm rider count.

2. **Processing Layer (Python)**

   * Runs image classification/counting algorithm.
   * If > 2 riders → sends `"ALERT"` command to Arduino.

3. **Alert Layer (Arduino)**

   * Arduino runs `triple_alert.ino`.
   * Buzzer/LED signals violation for 5 seconds.
   * Sends `"ALERT_ACK"` back to system.

4. **Communication Layer**

   * Serial data exchange between Python & Arduino.
   * Can be extended to **GSM/IoT Cloud** for authority alerts.

---

##  Arduino Code – `triple_alert.ino`

```cpp
const int ALERT_PIN = 8; // buzzer or LED pin
const unsigned long ALERT_DURATION_MS = 5000; 

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
      Serial.println("ALERT_ACK");
    }
  }
}
```



##  Real-Life Use Cases

* **Traffic Safety Enforcement** → Detect & warn riders violating safety norms.
* **Smart Cities** → Automated traffic monitoring.
* **Insurance & Road Safety Agencies** → Data collection on unsafe practices.
* **Police Authorities** → Real-time alerts for law enforcement.
* **Public Awareness** → Discourages risky behavior by instant warnings.

---

##  Advantages

* Improves **road safety** by reducing accident risks.
* Supports **traffic police** in monitoring.
* **Cost-effective** compared to advanced traffic surveillance systems.
* Works in **real-time** with simple hardware.
* Scalable for **large-scale smart city deployment**.



##  Limitations

* Requires **camera visibility** (not ideal in blind spots).
* Night detection accuracy depends on **infrared sensor quality**.
* Needs **internet/GSM upgrade** for city-wide deployment.
* Limited to detecting only rider count, not helmets (can be added later).



##  Future Scope

*  **Helmet Detection Integration** → Ensure helmet safety compliance.
*  **IoT Expansion** → GSM/WiFi modules for sending alerts to traffic authorities.
*  **Data Analytics Dashboard** → Cloud-based monitoring of violations.
*  **Integration with Police Fines System** → Automatic challan generation.
*  **AI Enhancement** → Detect unsafe posture, minors driving, or overloading.





##  Legal Notice

This project is **patented under the Government of India**. Unauthorized reproduction, distribution, or commercial use is prohibited without written permission.



Do you want me to also make a **short 300–350 characters version** (for GitHub project description section), along with this **long README**?

