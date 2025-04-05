import streamlit as st
from pymongo import MongoClient
import bcrypt
import os
from dotenv import load_dotenv
import pickle
import numpy as np
import pandas as pd
import requests
import pyttsx3
from datetime import datetime
import asyncio
from bleak import BleakScanner
import streamlit.components.v1 as components


load_dotenv()  # load environment variables from .env file

# Access the MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)

db = client["user_detail"]
users_collection = db["Detail"]
caretakers_collection = db["Caretakers"]
reminders_collection = db["Reminders"]

#Loading the models for health_monitor..
@st.cache_resource
def health_monitor_models():
    knn = pickle.load(open(r"C:\Users\Administrator\Downloads\Dataset\app\models\health_monitor\knn_model.pkl", "rb"))
    lr = pickle.load(open(r"C:\Users\Administrator\Downloads\Dataset\app\models\health_monitor\logistic_regression_model.pkl", "rb"))
    svm = pickle.load(open(r"C:\Users\Administrator\Downloads\Dataset\app\models\health_monitor\svm_model.pkl", "rb"))
    return knn, lr, svm


#Load models for safety_monitor
@st.cache_resource
def safety_monitor_models():
    with open(r"C:\Users\Administrator\Downloads\Dataset\app\models\safety_monitor\knn_model.pkl", "rb") as f1:
        knn_model = pickle.load(f1)
    with open(r"C:\Users\Administrator\Downloads\Dataset\app\models\safety_monitor\logistic_regression_model.pkl", "rb") as f2:
        lr_model = pickle.load(f2)
    with open(r"C:\Users\Administrator\Downloads\Dataset\app\models\safety_monitor\svm_model.pkl", "rb") as f3:
        svm_model = pickle.load(f3)
    return knn_model, lr_model, svm_model

#alert for the health_monitor section..
def speak_alert():
    msg="An alert has been sent to your caretakers"
    st.components.v1.html(f"""
    <script>
        var msg = new SpeechSynthesisUtterance("{msg}");
        window.speechSynthesis.speak(msg);
    </script>
    """)
    
#Message to be displayed
def blinking_alert(text, color):
    st.markdown(
        f"""
        <style>
        .blinking {{
            animation: blinker 1s linear infinite;
            color: {color};
            font-size: 28px;
            font-weight: bold;
        }}
        @keyframes blinker {{
            50% {{ opacity: 0; }}
        }}
        </style>
        <div class="blinking">{text}</div>
        """,
        unsafe_allow_html=True
    )

# Main app structure
def main():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url('https://t4.ftcdn.net/jpg/02/51/52/07/360_F_251520703_7oFW1TM6bNJMLs4QIS0ZUJF4utkXAuU7.jpg');
            background-size: cover;
        }
        </style>
        """ ,unsafe_allow_html=True)
    st.sidebar.title("Navigation")
    menu_options = ["Home", "Login", "Signup", "Your Caretakers", "Daily Reminders", "Health Monitor", "Safety Monitor","Connect Device"]
    choice = st.sidebar.selectbox("Menu", menu_options)

    if choice == "Home":
        show_home()
    elif choice == "Login":
        show_login()
    elif choice == "Signup":
        show_signup()
    elif choice == "Your Caretakers":
        show_add_caretaker()
    elif choice == "Daily Reminders":
        show_daily_reminder()
    elif choice == "Health Monitor":
        show_health_monitor()
    elif choice == "Safety Monitor":
        show_safety_monitor()
    elif choice=="Connect Device":
        connect_device()

def show_home():
    st.title("Welcome! 🙏")
    st.subheader("Hope you're doing well today")
    st.text("Please use the navigation bar for any kind of help 😊")
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to add caretakers.")
        return

def show_login():
    st.title("🔐 Login")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user" not in st.session_state:
        st.session_state.user = {}

    if st.session_state.logged_in:
        st.success(f"🔓 Already logged in as {st.session_state.user.get('name', 'User')}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = {}
            st.success("🚪 Logged out successfully.")
        return

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = users_collection.find_one({"email": email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid credentials.")

def show_signup():
    st.title("📝 Sign Up")
    name = st.text_input("Full Name")
    age = st.number_input("Age", 0, 120)
    email = st.text_input("Email")
    contact = st.text_input("Contact Number")
    city = st.text_input("City")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if users_collection.find_one({"email": email}):
            st.warning("User already exists.")
        else:
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            users_collection.insert_one({
                "name": name, "age": age, "email": email,
                "contact_number": contact, "city": city, "password": hashed_pw
            })
            st.success("🎉 Signup successful. Please login.")


def show_add_caretaker():
    st.title("🤝 Add Caretaker")

    if not st.session_state.get("logged_in"):
        st.warning("Please log in to add caretakers.")
        return

    user_email = st.session_state.user["email"]

    st.subheader("➕ Add New Caretaker")
    caretaker_name = st.text_input("Caretaker Name")
    caretaker_contact = st.text_input("Contact Number")
    relation = st.text_input("Relationship")

    if st.button("Add Caretaker"):
        if caretaker_name and caretaker_contact and relation:
            caretaker = {
                "user_email": user_email,
                "name": caretaker_name,
                "contact": caretaker_contact,
                "relation": relation
            }
            caretakers_collection.insert_one(caretaker)
            st.success("✅ Caretaker added successfully!")
        else:
            st.warning("Please fill all fields to add a caretaker.")

    st.markdown("---")
    st.subheader("📋 Your Caretakers")
    caretakers = caretakers_collection.find({"user_email": user_email})

    for ct in caretakers:
        st.markdown(f"""
        **Name:** {ct['name']}  
        **Contact:** {ct['contact']}  
        **Relation:** {ct['relation']}
        """)
        if st.button(f"🗑️ Delete {ct['name']}", key=str(ct["_id"])):
            caretakers_collection.delete_one({"_id": ct["_id"]})
            st.success(f"Deleted caretaker: {ct['name']}")
            st.rerun()


def show_daily_reminder():
    st.title("📅 Daily Reminder Dashboard")

    if not st.session_state.get("logged_in"):
        st.warning("Please log in to manage reminders.")
        return

    user_email = st.session_state.user["email"]

    st.subheader("➕ Add New Reminder")
    reminder_type = st.selectbox("Reminder Type", ["Medication", "Exercise", "Meal", "Appointment", "Other"])
    message = st.text_input("Reminder Message")
    reminder_date = st.date_input("Set Date", datetime.now().date())
    reminder_time = st.time_input("Set Time")

    if st.button("Add Reminder"):
        if message:
            timestamp = datetime.combine(reminder_date, reminder_time)
            reminder = {
                "device_id": user_email,
                "reminder_type": reminder_type,
                "timestamp": timestamp,
                "message": message,
                "reminder_sent": "No",
                "acknowledged": "No"
            }
            reminders_collection.insert_one(reminder)
            st.success("✅ Reminder added successfully.")
        else:
            st.warning("Please enter a reminder message.")

    st.markdown("---")
    st.subheader("🔍 Your Reminders")
    selected_date = st.date_input("Select Date", datetime.now().date())

    reminders = list(reminders_collection.find({"device_id": user_email}))
    filtered = [r for r in reminders if r["timestamp"].date() == selected_date]

    if not filtered:
        st.info("No reminders for selected date.")
    else:
        for r in filtered:
            st.markdown(f"### ⏰ {r['reminder_type']}")
            st.markdown(f"**Time:** {r['timestamp'].strftime('%I:%M %p')}")
            st.markdown(f"**Message:** {r['message']}")
            st.markdown(f"**Acknowledged:** {r['acknowledged']}")
            if r["acknowledged"] == "No":
                if st.button(f"Acknowledge {r['_id']}", key=str(r["_id"])):
                    reminders_collection.update_one({"_id": r["_id"]}, {"$set": {"acknowledged": "Yes"}})
                    st.success("✅ Reminder acknowledged.")
            st.markdown("---")

def show_health_monitor():
    st.title("🩺 Health Monitor")
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to add caretakers.")
        return
    knn_model, lr_model, svm_model = health_monitor_models()

    st.subheader("Enter Health Details")
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=0)
    bp_systolic = st.number_input("Blood Pressure - Systolic (mmHg)", min_value=0)
    bp_diastolic = st.number_input("Blood Pressure - Diastolic (mmHg)", min_value=0)
    oxygen = st.number_input("Oxygen Level (SpO2)", min_value=0)
    glucose = st.number_input("Glucose Level", min_value=0)

    if st.button("Predict Health Status"):
        input_data = np.array([[heart_rate, bp_systolic, bp_diastolic, oxygen, glucose]])
        votes = knn_model.predict(input_data)[0] + lr_model.predict(input_data)[0] + svm_model.predict(input_data)[0]
        if votes >= 2:
            blinking_alert("🔴 Final Decision (Majority Vote): ALERT ⚠️", "red")
            speak_alert()
        else:
            blinking_alert("🟢 Final Decision (Majority Vote): SAFE ✅", "green")

def show_safety_monitor():
    st.title("🛡️ Safety Monitor")
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to add caretakers.")
        return
    knn_model, lr_model, svm_model = safety_monitor_models()

    movement = st.selectbox("Movement Type", ["No Movement", "Sitting", "Walking"])
    fall = st.selectbox("Fall Detected?", ["No", "Yes"])
    impact = st.selectbox("Impact Level", ["Negligible", "Low", "Medium"])

    if st.button("Check Safety"):
        input_data = [
            1 if movement == "No Movement" else 0,
            1 if movement == "Sitting" else 0,
            1 if movement == "Walking" else 0,
            1 if fall == "Yes" else 0,
            1 if impact == "Low" else 0,
            1 if impact == "Medium" else 0,
            1 if impact == "Negligible" else 0
        ]
        input_np = np.array([input_data])
        votes = [knn_model.predict(input_np)[0], lr_model.predict(input_np)[0], svm_model.predict(input_np)[0]]
        final = 1 if votes.count(1) > 1 else 0
        if final:
            blinking_alert("🔴 Final Decision (Majority Vote): ALERT ⚠️", "red")
            speak_alert()
        else:
            blinking_alert("🟢 Final Decision (Majority Vote): SAFE ✅", "green")


#To work on.....
async def scan():
    devices = await BleakScanner.discover()
    st.subheader("Available devices are:")
    for d in devices:
        st.write(f"{d.name} - {d.address}")
def connect_device():
    st.title("⌚ Connect Device")
    if not st.session_state.get("logged_in"):
        st.warning("Please log in to add caretakers.")
        return
    asyncio.run(scan())


if __name__ == "__main__":
    st.set_page_config(page_title="Healthcare System", page_icon="🏥", layout="wide")
    main()
