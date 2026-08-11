# 🏥 CareHub Multispeciality Hospital - Web Application

A modern, responsive Flask web application for hospital clinical management, patient intake, automated prescription billing, UPI QR code payments, WhatsApp invoice dispatch, and appointment scheduling.

---

## 🌟 Key Features

1. **Dashboard & Analytics:**
   - Real-time KPI counters: Total Patients, Total Billing (₹), Today's Appointments, and Active Doctors.
   - Quick action shortcuts, recent patients overview, and symptom frequency distribution.

2. **Patient Intake & Smart Billing:**
   - Interactive symptom selector (Fever, Cold, Stomach Pain, Headache, Allergy, Diabetes, Blood Pressure, Asthma, Covid, Injury).
   - Real-time client-side calculation: dynamically shows prescribed medicines and prices as symptoms are selected.
   - Doctor consultation fee addition and multiple payment modes (Cash, GPay / UPI, Card, Net Banking).

3. **Official Invoices & Payments:**
   - Clean, professional, printable hospital invoice layout.
   - **Dynamic UPI / GPay QR Code:** Generates an instant scannable UPI payment QR code with the exact bill amount.
   - **WhatsApp Sharing:** One-click WhatsApp link (`wa.me`) formatted with hospital letterhead, prescribed medicines, and billing breakdown.

4. **Appointment Management:**
   - Schedule consultations with specialist doctors, dates, and time slots.
   - Filter queues by **All**, **Today's Queue**, or **Upcoming**.
   - Live status toggling (Scheduled, Completed, Cancelled) and record deletion.

5. **Patient Records Search:**
   - Real-time search by Patient Name, 10-Digit Mobile Number, or Patient ID.
   - View complete past clinical history, symptoms, medicines, and instant invoice reprinting.

6. **Dual Database Engine:**
   - Automatically connects to **MySQL** (`localhost:3306`, user: `root`, password: `nandhu@1112`, database: `hospital`).
   - If MySQL is not running locally, seamlessly falls back to a persistent **SQLite** database (`carehub.db`) with zero manual setup required.

---

## 🚀 How to Run

### 1. Navigate to the project directory:
```bash
cd C:\Users\nandh\.gemini\antigravity\scratch\carehub_webapp
```

### 2. Install dependencies (if not already installed):
```bash
pip install -r requirements.txt
```

### 3. Start the Flask application:
```bash
python app.py
```

### 4. Open in your browser:
Visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔐 Default Login Credentials
- **Username:** `admin`
- **Password:** `1234`

---

## 📂 Project Structure
```
carehub_webapp/
├── app.py                   # Main Flask application & routes
├── config.py                # Database and hospital configuration
├── database.py              # Unified MySQL/SQLite database engine
├── test_app.py              # Test suite
├── requirements.txt         # Dependencies
├── static/
│   ├── css/
│   │   └── style.css        # Modern design system & responsive styling
│   └── js/
│       └── main.js          # Live bill calculation, symptom tagger, UI scripts
└── templates/
    ├── base.html            # Master layout with navbar & alerts
    ├── login.html           # Staff portal login
    ├── dashboard.html       # Analytics dashboard & quick actions
    ├── add_patient.html     # Patient registration & live bill generator
    ├── bill_view.html       # Printable invoice with UPI QR & WhatsApp share
    ├── appointments.html    # Appointment scheduling & queue management
    └── search_patient.html  # Instant patient search & medical history
```
