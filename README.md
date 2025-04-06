**Empowering Elderly Care with multi agent AI system**

The project focusses on engineering a multi agent system to provide healthcare services to the elderly.
Involves different agents for safety and health monitoring along with daily reminders for never missing out on any updates.
**The different sections are mentioned below:**

**🧠 Health Monitor Section**

**🩺 Purpose:**
The Health Monitoring section predicts whether an elderly person is at risk based on their real-time physiological parameters such as heart rate, blood pressure, etc.

**🧮 Input Features:**
Users manually input the following health parameters:

Age
Heart Rate
Systolic Blood Pressure
Diastolic Blood Pressure
Oxygen Saturation
Temperature

These values are sent as input to the machine learning models.

**🤖 ML Models Used:**
This section uses an ensemble of three machine learning classifiers:

K-Nearest Neighbors (KNN)

Logistic Regression

Support Vector Machine (SVM)

Each model was pre-trained using relevant health datasets and saved as .pkl files. These are loaded during runtime.

**✅ Prediction Logic:**
Each model makes an independent prediction: "At Risk" or "Healthy"

Majority Voting is used to determine the final output:

If 2 or more models predict "At Risk" → the user is flagged as "At Risk"

Else → the user is considered "Healthy"

**🔔 Features:**
Displays each model’s prediction
Shows the final decision
Can trigger alerts or notify caretakers in future extensions


**🚨 Safety Monitor Section**

**🛡️ Purpose:**
This module is designed to detect emergency situations such as falls, sudden lack of movement, or dangerous impacts using smart wearable inputs.

**🧾 Input Features:**
One-hot encoded inputs based on:

**Movement:**
Movement_Walking
Movement_Sitting
Movement_No Movement

**Fall:**
Fall_Yes

**Impact:**
Impact_Low
Impact_Medium
Impact_Negligible

These inputs simulate how wearables might encode data to be ingested by the system.

**🤖 ML Models Used:**
Just like the health section, this one uses:

K-Nearest Neighbors (KNN)
Logistic Regression
Support Vector Machine (SVM)

These models are trained to detect the probability of an alert condition (e.g., fall detected, no movement after impact, etc.).

**✅ Prediction Logic:**
All three models make a prediction: "Alert" or "No Alert"

Majority Voting decides the final action:

If majority votes are "Alert" → System flags an emergency

**🔴 Additional Features:**

Voice alert using pyttsx3 to immediately notify anyone nearby
Ideal for real-time monitoring and connecting with wearable BLE devices


**📅 Daily Reminder Section:**

**⏰ Purpose:**
Helps elderly users keep track of medications, meals, appointments, or any task they need reminders for throughout the day.

**🧾 Functionality:**

Add a new reminder:
Choose type: Medication, Meal, Appointment, etc.
Set a date and time
Provide a short message
View existing reminders filtered by date
Acknowledge reminders to track completion

**💾 Data Handling:**
Reminders are stored in MongoDB Atlas

Each reminder is associated with the user's email (session ID)

Reminders have fields like:

json
Copy
Edit
{
  "device_id": "user@example.com",
  "reminder_type": "Medication",
  "timestamp": "2025-04-05T15:30:00",
  "message": "Take blood pressure medicine",
  "reminder_sent": "No",
  "acknowledged": "No"
}

**🧠 Features:**
View all reminders for a selected date

Reminders are displayed in a clean format with:

Reminder type
Time
Message
Acknowledge button
Acknowledged status is saved back to MongoDB



**🧰 Tech Stack Used:**

**🖥️ Frontend/UI**

**Streamlit:**
Used to create an intuitive and interactive web-based UI for the system.
Handles user login/signup
Manages form inputs for health/safety/reminders
Displays model outputs, charts, and alerts
Includes session management and role-based content
Deployed on streamlit Community Cloud:


**🧠 Machine Learning**

**Python (Scikit-learn):**

Used to build and train the ML models for:
Health Monitoring (KNN, Logistic Regression, SVM)
Safety Monitoring (KNN, Logistic Regression, SVM)
Trained models saved as .pkl files using pickle


**☁️ Database**

**MongoDB Atlas (Cloud):**

Stores all user data and app content:
User login/signup credentials
Reminder data per user
Caretaker information
Device-user mappings


**PyMongo:**

Python client to connect and query MongoDB Atlas

**🔊 Audio Alerts**

pyttsx3 (Offline Text-to-Speech):



**🔮 Future Work**


**📶 Bluetooth Integration**
BLE (Bluetooth Low Energy) support is already provisioned using the bleak library.

Future development can enable:

Real-time integration with smart wearable devices (e.g., fitness bands, health monitors).

Continuous health data monitoring (heart rate, step count, etc.).

Direct emergency alerts from physical devices.

**📢 Real-time Notifications and Alerts**
Enable instant notifications to caretakers via:
Email
SMS
Push Notifications
Auto-triggered alerts for unacknowledged reminders or safety risks.

**📊 Advanced Analytics Dashboard**
Build a caretaker dashboard with trends, statistics, and history of health, reminders, and alerts.

**🗣️ Multilingual and Voice Interaction**
Add voice assistant integration using TTS + STT (like pyttsx3, Google STT).
