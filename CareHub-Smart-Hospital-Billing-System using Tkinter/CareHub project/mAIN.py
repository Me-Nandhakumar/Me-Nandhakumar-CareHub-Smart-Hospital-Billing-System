import pymysql
import pywhatkit as pk
import pyautogui as pg
import time
import qrcode

# ================= DATABASE CONNECTION ==================
def get_connection():
    return pymysql.connect(
        host="localhost",
        port=3306,
        user="root",
        password="nandhu@1112",
        database="hospital"
    )

# ================= CREATE TABLE ==================
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    age INT,
    gender VARCHAR(15),
    weight INT,
    contact VARCHAR(15),
    symptoms TEXT,
    medicines TEXT,
    total_amount INT,
    payment_mode VARCHAR(20)
)
""")
conn.commit()
cursor.close()
conn.close()

print("----------------------- CareHub🏥 --------------------------\n")
print("📌Hospital Rules :")
rules = [
    "Patient Admission : Patients must be registered with valid details before admission.",
    "Visiting Hours Morning: 10:00 AM – 12:00 PM-Evening: 4:00 PM – 7:00 PM.",
    "Emergency Services: 24/7 emergency ward and ambulance service available.",
    "Billing & Payments: All bills must be cleared at the time of discharge."
]
for i in rules:
    print(i)
print("------------------------------------------------------------------------------")
print()
# ================= ADMIN LOGIN ==================
def admin_login():
    admin_user = "admin"
    admin_pass = "1234"

    print("-------- ADMIN LOGIN ---------")
    username = input("Enter Admin Username : ")
    password = input("Enter Admin Password : ")

    if username == admin_user and password == admin_pass:
        print("✅ Admin Login Successful!")
        return True
    else:
        print("❌ Invalid Username or Password!")
        return admin_login()



# ================= MEDICINES DATA ==================
medicines = {
    "fever": [("Paracetamol", 20), ("Ibuprofen", 30)],
    "cold": [("Cetirizine", 15), ("Cough Syrup", 50)],
    "stomach pain": [("Antacid", 25), ("Drotaverine", 40)],
    "headache": [("Paracetamol", 20), ("Aspirin", 35)],
    "allergy": [("Loratadine", 45), ("Cetirizine", 15)],
    "diabetes": [("Metformin", 60), ("Insulin", 150)],
    "blood pressure": [("Amlodipine", 55), ("Losartan", 70)],
    "asthma": [("Inhaler", 120), ("Montelukast", 90)],
    "covid": [("Paracetamol", 20), ("Vitamin C", 25), ("Zinc", 30)],
    "injury": [("Painkiller", 50), ("Antiseptic Cream", 35)]
}

# ================= SHOW SYMPTOMS ==================
def show_symptoms():
    print("\n🩺 AVAILABLE SYMPTOMS IN SYSTEM:")
    print("-"*45)
    for s in medicines.keys():
        print("➡️", s.capitalize())
    print("-"*45)

# ================= SAVE PATIENT ==================
def save_patient_to_db(name, age, gender, weight, contact, symptoms, medicines_list, total, payment_mode="Cash"):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO patients (name, age, gender, weight, contact, symptoms, medicines, total_amount, payment_mode)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            name, age, gender, weight, contact,
            ", ".join(symptoms),
            ", ".join([med for med, price in medicines_list]),
            total,
            payment_mode
        ))
        conn.commit()
        cursor.close()
        conn.close()
        print("💾 Patient record saved in database successfully!")
    except Exception as e:
        print("❌ Database Error:", e)

def search_patient():
    query = input("Enter Patient Name or Contact to Search: ").strip()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE name=%s OR contact=%s", (query, query))
    results = cursor.fetchall()
    if results:
        for row in results:
            print(row)
    else:
        print("❌ No patient found!")
    cursor.close()
    conn.close()


# ================= GENERATE BILL ==================
def generate_bill(patient_name, age, gender, weight, contact, symptoms, payment_mode, whatsapp_no=None):
    total = 0
    items = []

    for s in symptoms:
        if s in medicines:
            for med, price in medicines[s]:
                items.append((med, price))
                total += price

    # Bill text
    bill_text = "\n" + "="*45 + "\n"
    bill_text += "🏥 CareHub Multispeciality Hospital\n"
    bill_text += "-"*45 + "\n"
    bill_text += f"Patient Name : {patient_name}\n"
    bill_text += f"Age          : {age}\n"
    bill_text += f"Gender       : {gender}\n"
    bill_text += f"Weight       : {weight} kg\n"
    bill_text += f"Contact No   : {contact}\n"
    bill_text += f"Symptoms     : {', '.join(symptoms)}\n"
    bill_text += "-"*45 + "\n"
    bill_text += "Medicines Prescribed :\n"
    for med, price in items:
        bill_text += f"➡ {med:15} - ₹{price}\n"
    bill_text += "-"*45 + "\n"
    bill_text += f"✅ Total Bill Amount : ₹{total}\n"
    bill_text += f"💳 Payment Mode      : {payment_mode}\n"
    bill_text += "="*45

    # Print Bill
    print(bill_text)

    # Save in Database
    save_patient_to_db(patient_name, age, gender, weight, contact, symptoms, items, total, payment_mode)

    # QR Code for GPay
    if payment_mode.lower() == "gpay":
        upi_id = "nandhakumar.s.jnandhu-1@okhdfcbank"
        data = f"upi://pay?pa={upi_id}&pn=CareHub&am={total}&cu=INR"
        qr = qrcode.make(data)
        qr.save("gpay_qr.png")
        qr.show()
        print("📲 Scan QR Code to pay via GPay")

    # Send WhatsApp Message
    if whatsapp_no:
        print("\n📲 Sending bill via WhatsApp...")
        pk.sendwhatmsg_instantly(whatsapp_no, bill_text, wait_time=10, tab_close=False)
        time.sleep(5)
        pg.press("enter")
        print("✅ Bill sent successfully on WhatsApp!")
#Add Patient & Generate Bill
def add_patient():
    show_symptoms()
    print("\n📝 ENTER PATIENT DETAILS")
    p_name = input("Enter Patient Name : ")
    p_age = int(input("Enter Age : "))

    # Gender validation
    p_gender = input("ENTER YOUR GENDER (male/female): ").strip().lower()
    while p_gender not in ["male", "female"]:
        print("❌ Invalid gender, please enter 'male' or 'female'.")
        p_gender = input("ENTER YOUR GENDER (male/female): ").strip().lower()

    p_weight = int(input("Enter Weight (kg): "))

    # Contact validation
    p_contact = input("Enter Contact No (10 digits): ")
    while not (p_contact.isdigit() and len(p_contact) == 10):
        print("❌ Invalid contact number. Enter 10 digits.")
        p_contact = input("Enter Contact No (10 digits): ")
    whatsapp = "+91" + p_contact

    # Symptoms validation
    symptoms = input("Enter Symptoms (comma separated): ").lower().split(",")
    symptoms = [s.strip() for s in symptoms if s.strip() in medicines]
    while not symptoms:
        print("❌ No valid symptoms entered. Try again.")
        symptoms = input("Enter Symptoms (comma separated): ").lower().split(",")
        symptoms = [s.strip() for s in symptoms if s.strip() in medicines]

    # Payment option
    print("\n💳 Payment Options: 1. Cash  2. GPay")
    choice = input("Choose Payment Mode (1/2): ").strip()
    payment_mode = "GPay" if choice == "2" else "Cash"
    # Generate Bill + Save in DB + Send WhatsApp
    generate_bill(p_name, p_age, p_gender, p_weight, p_contact, symptoms, payment_mode, whatsapp)

# ================= MAIN MENU =================
admin_login()
while True:
    print("\n--------🏥 CareHub Menu--------")
    print("1. Add Patient & Generate Bill")
    print("2. Search Patient")
    print("3. Exit")
    choice = input("Enter your choice: ").strip()

    if choice == "1":
        add_patient()
    elif choice == "2":
        search_patient()
    elif choice == "3":
        print("👋 Exiting CareHub. Have a nice day!")
        break
    else:
        print("❌ Invalid choice!")

