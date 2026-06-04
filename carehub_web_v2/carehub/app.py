from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql
import qrcode
import io
import base64
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = "carehub_secret_2024"

# ============ DB CONFIG ============
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "nandhu@1112"),
    "database": os.environ.get("DB_NAME", "hospital")
}

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "1234")

MEDICINES = {
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

UPI_ID = "nandhakumar.s.jnandhu-1@okhdfcbank"
HOSPITAL_NAME = "CareHub Multispeciality Hospital"


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def init_db():
    try:
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
                payment_mode VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_name VARCHAR(100),
                contact VARCHAR(15),
                doctor VARCHAR(100),
                department VARCHAR(100),
                appt_date DATE,
                appt_time VARCHAR(20),
                reason TEXT,
                status VARCHAR(20) DEFAULT 'Scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("DB init error:", e)


def build_whatsapp_link(contact, message):
    """Build a wa.me link — opens WhatsApp with pre-filled message."""
    number = contact.strip().replace(" ", "").replace("-", "")
    if not number.startswith("+"):
        number = "+91" + number
    encoded = urllib.parse.quote(message)
    return f"https://wa.me/{number}?text={encoded}"


def build_bill_text(name, age, gender, weight, contact, symptoms, items, total, payment_mode, patient_id):
    lines = [
        f"🏥 *{HOSPITAL_NAME}*",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"*Patient Bill — #{patient_id}*",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"👤 Name    : {name}",
        f"🎂 Age     : {age} years",
        f"⚧  Gender  : {gender.title()}",
        f"⚖️  Weight  : {weight} kg",
        f"📞 Contact : {contact}",
        f"🩺 Symptoms: {', '.join(symptoms).title()}",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"💊 *Medicines Prescribed:*",
    ]
    for med, price in items:
        lines.append(f"  ➡ {med} — ₹{price}")
    lines += [
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"✅ *Total Amount : ₹{total}*",
        f"💳 Payment Mode : {payment_mode}",
        f"━━━━━━━━━━━━━━━━━━━━━━━",
        f"Thank you for choosing {HOSPITAL_NAME}! 💙",
        f"Get well soon! 🙏"
    ]
    return "\n".join(lines)


# ============ AUTH ============
@app.route("/")
def index():
    return redirect(url_for("dashboard") if "admin" in session else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == ADMIN_USER and request.form.get("password") == ADMIN_PASS:
            session["admin"] = True
            return redirect(url_for("dashboard"))
        flash("Invalid username or password!", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))


# ============ DASHBOARD ============
@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        total = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(total_amount) FROM patients")
        revenue = cursor.fetchone()[0] or 0
        cursor.execute("SELECT COUNT(*) FROM patients WHERE payment_mode='GPay'")
        gpay = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM appointments WHERE status='Scheduled'")
        appt_count = cursor.fetchone()[0]
        cursor.execute("SELECT * FROM patients ORDER BY id DESC LIMIT 5")
        recent = cursor.fetchall()
        cursor.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT 5")
        recent_appts = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("dashboard.html", total=total, revenue=revenue,
                               gpay=gpay, appt_count=appt_count,
                               recent=recent, recent_appts=recent_appts)
    except Exception as e:
        return render_template("dashboard.html", total=0, revenue=0, gpay=0,
                               appt_count=0, recent=[], recent_appts=[], error=str(e))


# ============ PATIENTS ============
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if "admin" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        name = request.form["name"]
        age = int(request.form["age"])
        gender = request.form["gender"]
        weight = int(request.form["weight"])
        contact = request.form["contact"]
        symptoms = [s.strip() for s in request.form.getlist("symptoms")]
        payment_mode = request.form["payment_mode"]

        items, total = [], 0
        for s in symptoms:
            if s in MEDICINES:
                for med, price in MEDICINES[s]:
                    items.append((med, price))
                    total += price

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO patients (name, age, gender, weight, contact, symptoms, medicines, total_amount, payment_mode)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (name, age, gender, weight, contact,
                  ", ".join(symptoms), ", ".join([m for m, _ in items]), total, payment_mode))
            conn.commit()
            patient_id = cursor.lastrowid
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f"Database Error: {e}", "error")
            return redirect(url_for("add_patient"))

        qr_b64 = None
        if payment_mode == "GPay":
            upi_data = f"upi://pay?pa={UPI_ID}&pn=CareHub&am={total}&cu=INR"
            img = qrcode.make(upi_data)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            qr_b64 = base64.b64encode(buf.getvalue()).decode()

        # Build WhatsApp link
        bill_text = build_bill_text(name, age, gender, weight, contact, symptoms, items, total, payment_mode, patient_id)
        wa_link = build_whatsapp_link(contact, bill_text)

        return render_template("bill.html",
            name=name, age=age, gender=gender, weight=weight,
            contact=contact, symptoms=symptoms, items=items,
            total=total, payment_mode=payment_mode,
            qr_b64=qr_b64, patient_id=patient_id, wa_link=wa_link)

    return render_template("add_patient.html", symptoms=list(MEDICINES.keys()))


@app.route("/patients")
def patients():
    if "admin" not in session:
        return redirect(url_for("login"))
    query = request.args.get("q", "").strip()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if query:
            cursor.execute("SELECT * FROM patients WHERE name LIKE %s OR contact LIKE %s ORDER BY id DESC",
                           (f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("SELECT * FROM patients ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        rows = []
        flash(str(e), "error")
    return render_template("patients.html", rows=rows, query=query)


@app.route("/patient/<int:pid>")
def patient_detail(pid):
    if "admin" not in session:
        return redirect(url_for("login"))
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id=%s", (pid,))
        p = cursor.fetchone()
        cursor.close()
        conn.close()
    except:
        p = None
    if not p:
        flash("Patient not found", "error")
        return redirect(url_for("patients"))

    qr_b64 = None
    if p[9] == "GPay":
        upi_data = f"upi://pay?pa={UPI_ID}&pn=CareHub&am={p[8]}&cu=INR"
        img = qrcode.make(upi_data)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

    # Rebuild items list for WhatsApp
    symptoms = [s.strip() for s in p[6].split(",")]
    items = []
    for s in symptoms:
        if s in MEDICINES:
            for med, price in MEDICINES[s]:
                items.append((med, price))

    bill_text = build_bill_text(p[1], p[2], p[3] or "", p[4], p[5],
                                symptoms, items, p[8], p[9], p[0])
    wa_link = build_whatsapp_link(p[5], bill_text)

    return render_template("patient_detail.html", p=p, qr_b64=qr_b64, wa_link=wa_link)


# ============ APPOINTMENTS ============
DOCTORS = [
    ("Dr. Ramesh Kumar", "General Medicine"),
    ("Dr. Priya Sharma", "Cardiology"),
    ("Dr. Anil Verma", "Orthopedics"),
    ("Dr. Sunitha Rajan", "Gynecology"),
    ("Dr. Karthik M", "Neurology"),
    ("Dr. Divya Nair", "Pediatrics"),
    ("Dr. Suresh Babu", "Dermatology"),
    ("Dr. Meena Iyer", "ENT"),
]

@app.route("/appointments", methods=["GET"])
def appointments():
    if "admin" not in session:
        return redirect(url_for("login"))
    status_filter = request.args.get("status", "")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if status_filter:
            cursor.execute("SELECT * FROM appointments WHERE status=%s ORDER BY appt_date, appt_time", (status_filter,))
        else:
            cursor.execute("SELECT * FROM appointments ORDER BY appt_date DESC, appt_time")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        rows = []
        flash(str(e), "error")
    return render_template("appointments.html", rows=rows, status_filter=status_filter)


@app.route("/appointments/add", methods=["GET", "POST"])
def add_appointment():
    if "admin" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        patient_name = request.form["patient_name"]
        contact = request.form["contact"]
        doctor = request.form["doctor"]
        department = request.form["department"]
        appt_date = request.form["appt_date"]
        appt_time = request.form["appt_time"]
        reason = request.form.get("reason", "")

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO appointments (patient_name, contact, doctor, department, appt_date, appt_time, reason)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (patient_name, contact, doctor, department, appt_date, appt_time, reason))
            conn.commit()
            appt_id = cursor.lastrowid
            cursor.close()
            conn.close()
        except Exception as e:
            flash(f"Error: {e}", "error")
            return redirect(url_for("add_appointment"))

        # WhatsApp confirmation message
        msg = (
            f"🏥 *{HOSPITAL_NAME}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"*Appointment Confirmation — #{appt_id}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 Patient : {patient_name}\n"
            f"👨‍⚕️ Doctor  : {doctor}\n"
            f"🏷️  Dept    : {department}\n"
            f"📅 Date    : {appt_date}\n"
            f"⏰ Time    : {appt_time}\n"
            f"📝 Reason  : {reason or 'General Checkup'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"Please arrive 10 minutes early. 🙏\n"
            f"CareHub Hospital | 24/7 Emergency: 1800-XXX-XXXX"
        )
        wa_link = build_whatsapp_link(contact, msg)
        flash("✅ Appointment booked successfully!", "success")
        return render_template("appt_confirm.html",
            appt_id=appt_id, patient_name=patient_name, doctor=doctor,
            department=department, appt_date=appt_date, appt_time=appt_time,
            reason=reason, contact=contact, wa_link=wa_link)

    return render_template("add_appointment.html", doctors=DOCTORS)


@app.route("/appointments/status/<int:aid>/<string:status>")
def update_appt_status(aid, status):
    if "admin" not in session:
        return redirect(url_for("login"))
    if status in ["Scheduled", "Completed", "Cancelled"]:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE appointments SET status=%s WHERE id=%s", (status, aid))
            conn.commit()
            cursor.close()
            conn.close()
            flash(f"Appointment #{aid} marked as {status}", "success")
        except Exception as e:
            flash(str(e), "error")
    return redirect(url_for("appointments"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
