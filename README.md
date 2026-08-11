# 🏥 CareHub Multispeciality Hospital Management System

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange?logo=mysql)
![License](https://img.shields.io/badge/License-MIT-green)

CareHub is a modern, responsive full-stack **Hospital Management Web Application** built using **Flask** and **MySQL**. It streamlines clinical workflows with automated symptom-to-medicine prescriptions, real-time pharmacy billing calculation, dynamic UPI QR code payments, one-click WhatsApp digital receipt dispatch, and appointment scheduling.

---

## ✨ Key Highlights
- 🩺 **Smart Prescription Engine:** Interactive multi-select symptom pills that automatically map clinical conditions to prescribed medications and prices in real-time.
- 💳 **Dynamic UPI / GPay QR Generation:** Scannable payment QR code generated instantly with the exact patient invoice amount.
- 📲 **WhatsApp Invoice Dispatch:** One-click receipt delivery directly to the patient's WhatsApp without third-party desktop dependencies.
- 📅 **Doctor Appointment Queue:** Consultation booking with date filters (`All`, `Today`, `Upcoming`) and live status tracking.
- 🔍 **Medical History Search:** Instant lookup by Patient Name, 10-Digit Mobile, or Patient ID.
- 🗄️ **Dual Database Architecture:** Integrated with MySQL (via MySQL Workbench) with an automatic zero-config SQLite fallback.

---

## 🚀 Quickstart
```bash
# Clone the repository
git clone https://github.com/your-username/carehub-hospital-system.git
cd carehub-hospital-system

# Install dependencies
pip install -r requirements.txt

# Run the Flask app
python app.py
