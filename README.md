# FLEX – Bicep Curl Form Monitoring & Live Dashboard

*FLEX* is a wearable IoT project for monitoring bicep curl form in real time. It uses the accelerometer and gyroscope of a 9-DOF sensor (accelerometer, gyro, magnetometer) to gather workout data, optionally processes it with machine learning, and displays results on a Flask-based web app. The public-facing marketing page showcases product features, while a protected dashboard provides live feedback to logged-in users.

---

## Table of Contents

1. [Overview](#overview)  
2. [Project Structure](#project-structure)  
4. [Usage](#usage)  
7. [Spec (Requirements)](#spec-requirements)  
   - [Core Functional Specifications](#core-functional-specifications)  
   - [Non-Functional Specifications](#non-functional-specifications)  
   - [Documentation Specifications](#documentation-specifications)  
   - [Advanced Functionality](#advanced-functionality)  


---

## Overview

FLEX aims to help users perfect their *bicep curl form* by providing:  
- Real-time **Range of Motion,** **shoulder movement/ bicep engagement** detection, **Time Under Tension** metrics  
- A **Flask-based web application with** **user authentication** (login, logout)  
- A **public landing page** (marketing site) featuring an eye-catching chart  
- **machine-learning** inference for advanced workout analysis, hosted on an ec2 server.  
- A data pipeline that can easily be adapted to real sensor data from a Raspberry Pi.

---

## Project Structure
*Key Files & Directories*  
- **webapp/**: Main Flask application folder  
- **raspi/**: Contains sensor drivers (I2C) and main.py for the embedded device  
- **ec2server/**: Contains backend or ML scripts for advanced processing
## Spec (Requirements)

Below we map the project’s implementation to each requirement from your specification list.

---

### Core Functional Specifications

1. *Functional Prototype (IoT)*
   - *Implementation*: The Raspberry Pi + 9-DOF sensor forms an IoT device. The Flask app serves as the remote UI.

2. *Standalone Hardware with I2C*
   - *Implementation*: The raspi/FXOS8700.py (accel + mag) and raspi/FXAS21002C.py (gyro) provide low-level I2C reads.

3. *Sends Data to Remote Client*
   - *Implementation*: Data can be sent via HTTP to the Flask server. The user sees a real-time UI in the browser.

4. *Process/Format Sensor Data*
   - *Implementation*: bicep_curl_detector.py, rep_data_processor.py, ML logic. Results shown as *ROM, **Swinging, **TUT* and ml feedback.

5. *Appropriate Sampling Interval*
   - *Implementation*: Sensor code typically samples at ~50Hz (adjustable).

---

### Non-Functional Specifications

6. *Imaginative, Potential for Product*
   - *Implementation*: A bicep curl monitor with real-time feedback is unique and could be commercialized (gamification, data analytics, etc.).

7. *Relevant & Understandable Data Presentation*
   - *Implementation: The dashboard focuses on **Time Under Tension & **Range of Motion metrics—immediately meaningful to fitness users.

8. *Appropriately Structured Code*
   - *Implementation*: Clear separation of concerns:
     - app.py (Flask + DB)
     - raspi/ for hardware drivers and main.py entry point
     - static/ + templates/ for front-end

9. *Scalable to Multiple Users*
   - *Implementation*: Flask with SQLAlchemy can handle multiple user accounts, each with its own data.

10. *Byte-Level I2C Communication*
   - *Implementation*: FXOS8700.py and FXAS21002C.py manually implement I2C reads/writes using smbus, not a prepackaged sensor library.

---

### Documentation Specifications

11. *Marketing Website*
    - *Implementation*: The landing page (index.html) plus CSS, images, and comedic chart demonstrate product benefits to prospects.

12. *Marketing Video*
    - *Implementation: *Not included here in code, but placeholders for an embedded video or link can fulfill the <2min marketing clip requirement.

13. *Website & Video Browser-Viewable*
    - *Implementation*: The Flask site is fully browser-accessible. Video link or embed can also be made accessible similarly.

---

### Advanced Functionality

14. *Multi-Sensor Fusion*
    - *Implementation*: We combine data from accelerometer and gyroscope for more advanced analysis if desired.

15. *Machine Learning*
    - *Implementation*: usage via k_cluster.py for classifying rep quality.

18. *Web/Mobile App*
    - *Implementation*: The Flask site is responsive and can be accessed from mobile browsers.

20. *Remote Database*
    - *Implementation*: Currently local SQLite (flex_app.db), but partial references to firebase/ or ec2_server/ show potential for remote DB usage.

21. *Backend Server*
    - *Implementation*: The entire Flask app is a backend. Additional advanced logic can run in ec2server/.

23. *Offline Functionality*
    - The system primarily expects connectivity, but the raspberry pi saves a buffer of the data if the connection gets lost. once connection is reestablished, the buffer is flushed.
    