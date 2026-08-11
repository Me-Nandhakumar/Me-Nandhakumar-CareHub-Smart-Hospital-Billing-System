import io
import base64
import urllib.parse
import datetime
import qrcode
from functools import wraps
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session, jsonify, abort
)
from config import Config
from database import init_db, execute_query, ACTIVE_DB_TYPE

app = Flask(__name__)
app.config.from_object(Config)

# ================= MEDICINES CATALOG ==================
MEDICINES_CATALOG = {
    "fever": [("Paracetamol 650mg", 20), ("Ibuprofen 400mg", 30)],
    "cold": [("Cetirizine 10mg", 15), ("Cough Syrup (100ml)", 50)],
    "stomach pain": [("Antacid Gel", 25), ("Drotaverine 40mg", 40)],
    "headache": [("Paracetamol 500mg", 20), ("Aspirin 300mg", 35)],
    "allergy": [("Loratadine 10mg", 45), ("Cetirizine 10mg", 15)],
    "diabetes": [("Metformin 500mg", 60), ("Insulin Regular", 150)],
    "blood pressure": [("Amlodipine 5mg", 55), ("Losartan 50mg", 70)],
    "asthma": [("Inhaler (Salbutamol)", 120), ("Montelukast 10mg", 90)],
    "covid": [("Paracetamol 650mg", 20), ("Vitamin C 500mg", 25), ("Zinc 50mg", 30)],
    "injury": [("Painkiller (Diclofenac)", 50), ("Antiseptic Cream", 35)]
}

# ================= AUTH DECORATOR ==================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash("Please log in to access the system.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ================= TEMPLATE CONTEXT ==================
@app.context_processor
def inject_global_vars():
    return {
        'hospital_name': Config.HOSPITAL_NAME,
        'hospital_phone': Config.HOSPITAL_PHONE,
        'hospital_address': Config.HOSPITAL_ADDRESS,
        'current_year': datetime.datetime.now().year,
        'db_backend': ACTIVE_DB_TYPE
    }

# ================= AUTH ROUTES ==================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        # Default Admin Credentials
        if username == 'admin' and password == '1234':
            session['logged_in'] = True
            session['username'] = username
            session['role'] = 'Administrator'
            flash("Welcome back, Administrator!", "success")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for('login'))

# ================= DASHBOARD ==================
@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    # Metrics
    total_patients_res = execute_query("SELECT COUNT(*) as count FROM patients", fetchone=True)
    total_patients = total_patients_res['count'] if total_patients_res else 0
    
    revenue_res = execute_query("SELECT SUM(total_amount) as total FROM patients", fetchone=True)
    total_revenue = revenue_res['total'] if revenue_res and revenue_res['total'] else 0
    
    today_appts_res = execute_query("SELECT COUNT(*) as count FROM appointments WHERE appoint_date = %s", (today_str,), fetchone=True)
    today_appointments = today_appts_res['count'] if today_appts_res else 0
    
    total_appts_res = execute_query("SELECT COUNT(*) as count FROM appointments", fetchone=True)
    total_appointments = total_appts_res['count'] if total_appts_res else 0
    
    doctors_res = execute_query("SELECT COUNT(*) as count FROM doctors", fetchone=True)
    total_doctors = doctors_res['count'] if doctors_res else 0
    
    # Recent Patients
    recent_patients = execute_query(
        "SELECT * FROM patients ORDER BY id DESC LIMIT 5",
        fetchall=True
    ) or []
    
    # Today's & Upcoming Appointments
    upcoming_appointments = execute_query(
        "SELECT * FROM appointments WHERE appoint_date >= %s ORDER BY appoint_date ASC, appoint_time ASC LIMIT 5",
        (today_str,),
        fetchall=True
    ) or []
    
    # Symptoms frequency calculation for analytics
    all_patients = execute_query("SELECT symptoms FROM patients", fetchall=True) or []
    symptom_counts = {}
    for p in all_patients:
        if p.get('symptoms'):
            for s in [s.strip().lower() for s in p['symptoms'].split(',') if s.strip()]:
                symptom_counts[s] = symptom_counts.get(s, 0) + 1

    return render_template(
        'dashboard.html',
        total_patients=total_patients,
        total_revenue=total_revenue,
        today_appointments=today_appointments,
        total_appointments=total_appointments,
        total_doctors=total_doctors,
        recent_patients=recent_patients,
        upcoming_appointments=upcoming_appointments,
        symptom_counts=symptom_counts
    )

# ================= ADD PATIENT & LIVE BILLING ==================
@app.route('/patient/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            age = int(request.form.get('age', 0))
            gender = request.form.get('gender', '').strip().lower()
            weight = int(request.form.get('weight', 0))
            contact = request.form.get('contact', '').strip()
            payment_mode = request.form.get('payment_mode', 'Cash').strip()
            
            # Selected symptoms list from checkboxes or comma-separated input
            symptoms_list = request.form.getlist('symptoms')
            if not symptoms_list:
                custom_symptoms = request.form.get('custom_symptoms', '')
                if custom_symptoms:
                    symptoms_list = [s.strip().lower() for s in custom_symptoms.split(',') if s.strip()]
            
            if not (name and gender and contact and symptoms_list):
                flash("Please fill in all mandatory fields correctly.", "danger")
                return redirect(url_for('add_patient'))
                
            if len(contact) < 10 or not contact.isdigit():
                flash("Please enter a valid 10-digit contact phone number.", "danger")
                return redirect(url_for('add_patient'))
                
            if gender not in ['male', 'female', 'other']:
                flash("Please specify gender as Male, Female, or Other.", "danger")
                return redirect(url_for('add_patient'))

            # Compute Prescribed Medicines and Total Price
            prescribed_meds = []
            total_amount = 0
            
            for s in symptoms_list:
                s_clean = s.strip().lower()
                if s_clean in MEDICINES_CATALOG:
                    for med_name, price in MEDICINES_CATALOG[s_clean]:
                        prescribed_meds.append(med_name)
                        total_amount += price

            # Allow consultation fee addition if configured
            consultation_fee = int(request.form.get('consultation_fee', 0) or 0)
            total_amount += consultation_fee

            symptoms_str = ", ".join(symptoms_list)
            medicines_str = ", ".join(prescribed_meds) if prescribed_meds else "General Health Consultation"

            patient_id = execute_query(
                """
                INSERT INTO patients (name, age, gender, weight, contact, symptoms, medicines, total_amount, payment_mode)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (name, age, gender.capitalize(), weight, contact, symptoms_str, medicines_str, total_amount, payment_mode),
                commit=True
            )
            
            flash(f"Patient '{name}' registered successfully! Invoice generated.", "success")
            return redirect(url_for('view_bill', patient_id=patient_id))
            
        except Exception as e:
            flash(f"Error processing patient registration: {str(e)}", "danger")
            return redirect(url_for('add_patient'))

    return render_template('add_patient.html', catalog=MEDICINES_CATALOG)

# ================= BILL / INVOICE VIEW ==================
@app.route('/patient/bill/<int:patient_id>')
@login_required
def view_bill(patient_id):
    patient = execute_query("SELECT * FROM patients WHERE id = %s", (patient_id,), fetchone=True)
    if not patient:
        flash("Invoice / Patient record not found.", "danger")
        return redirect(url_for('dashboard'))

    # Parse items
    symptoms = [s.strip() for s in patient['symptoms'].split(',') if s.strip()]
    
    # Reconstruct itemized prices
    bill_items = []
    calculated_subtotal = 0
    
    for s in symptoms:
        s_lower = s.lower()
        if s_lower in MEDICINES_CATALOG:
            for med, price in MEDICINES_CATALOG[s_lower]:
                bill_items.append({"name": med, "indication": s.title(), "price": price})
                calculated_subtotal += price

    # In case of difference (consultation fee or custom meds)
    diff = patient['total_amount'] - calculated_subtotal
    if diff > 0:
        bill_items.append({"name": "Doctor Consultation & Service Fee", "indication": "Consultation", "price": diff})

    # Generate UPI QR Code Base64
    upi_id = Config.UPI_ID
    total_amount = patient['total_amount']
    upi_url = f"upi://pay?pa={upi_id}&pn=CareHub%20Hospital&am={total_amount}&cu=INR"
    
    qr_img = qrcode.make(upi_url)
    buffered = io.BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # WhatsApp Share Text
    whatsapp_text = (
        f"*🏥 {Config.HOSPITAL_NAME}*\n"
        f"-----------------------------------------\n"
        f"📄 *Invoice / Medical Summary*\n"
        f"-----------------------------------------\n"
        f"👤 *Patient Name:* {patient['name']}\n"
        f"🎂 *Age/Gender:* {patient['age']} Yrs / {patient['gender']}\n"
        f"⚖️ *Weight:* {patient['weight']} kg\n"
        f"📞 *Contact:* {patient['contact']}\n"
        f"🩺 *Symptoms:* {patient['symptoms']}\n"
        f"-----------------------------------------\n"
        f"💊 *Prescribed Medicines:*\n"
    )
    for item in bill_items:
        whatsapp_text += f"• {item['name']} - ₹{item['price']}\n"
        
    whatsapp_text += (
        f"-----------------------------------------\n"
        f"💰 *Total Amount:* ₹{patient['total_amount']}\n"
        f"💳 *Payment Mode:* {patient['payment_mode']}\n"
        f"-----------------------------------------\n"
        f"🙏 *Wishing you a speedy recovery!*"
    )
    
    encoded_whatsapp_text = urllib.parse.quote(whatsapp_text)
    whatsapp_url = f"https://wa.me/91{patient['contact']}?text={encoded_whatsapp_text}"

    return render_template(
        'bill_view.html',
        patient=patient,
        bill_items=bill_items,
        qr_base64=qr_base64,
        whatsapp_url=whatsapp_url,
        upi_id=upi_id
    )

# ================= APPOINTMENTS ==================
@app.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    if request.method == 'POST':
        patient_name = request.form.get('patient_name', '').strip()
        doctor = request.form.get('doctor', '').strip()
        date_str = request.form.get('appoint_date', '').strip()
        time_slot = request.form.get('appoint_time', '').strip()
        contact = request.form.get('contact', '').strip()
        notes = request.form.get('notes', '').strip()

        if not (patient_name and doctor and date_str and time_slot):
            flash("Please fill in all mandatory appointment details.", "danger")
            return redirect(url_for('appointments'))

        try:
            # Validate date
            datetime.datetime.strptime(date_str, "%Y-%m-%d")
            
            execute_query(
                """
                INSERT INTO appointments (patient_name, appoint_date, appoint_time, doctor, contact, notes, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled')
                """,
                (patient_name, date_str, time_slot, doctor, contact, notes),
                commit=True
            )
            flash(f"Appointment scheduled successfully for {patient_name} with {doctor}!", "success")
            return redirect(url_for('appointments'))
        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "danger")
        except Exception as e:
            flash(f"Error booking appointment: {str(e)}", "danger")

    # Fetch filters
    filter_date = request.args.get('filter', 'all')
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    
    if filter_date == 'today':
        appts = execute_query(
            "SELECT * FROM appointments WHERE appoint_date = %s ORDER BY appoint_time ASC",
            (today_str,),
            fetchall=True
        ) or []
    elif filter_date == 'upcoming':
        appts = execute_query(
            "SELECT * FROM appointments WHERE appoint_date >= %s ORDER BY appoint_date ASC, appoint_time ASC",
            (today_str,),
            fetchall=True
        ) or []
    else:
        appts = execute_query(
            "SELECT * FROM appointments ORDER BY appoint_date DESC, appoint_time DESC",
            fetchall=True
        ) or []

    doctors = execute_query("SELECT * FROM doctors ORDER BY name ASC", fetchall=True) or []

    return render_template(
        'appointments.html',
        appointments=appts,
        doctors=doctors,
        current_filter=filter_date,
        today_str=today_str
    )

@app.route('/appointments/<int:appt_id>/status', methods=['POST'])
@login_required
def update_appointment_status(appt_id):
    new_status = request.form.get('status', 'Scheduled')
    execute_query(
        "UPDATE appointments SET status = %s WHERE id = %s",
        (new_status, appt_id),
        commit=True
    )
    flash("Appointment status updated.", "info")
    return redirect(url_for('appointments'))

@app.route('/appointments/<int:appt_id>/delete', methods=['POST'])
@login_required
def delete_appointment(appt_id):
    execute_query("DELETE FROM appointments WHERE id = %s", (appt_id,), commit=True)
    flash("Appointment deleted successfully.", "success")
    return redirect(url_for('appointments'))

# ================= SEARCH PATIENT ==================
@app.route('/search')
@login_required
def search_patient():
    query = request.args.get('q', '').strip()
    results = []
    
    if query:
        # Search by ID or Name or Contact
        if query.isdigit():
            results = execute_query(
                "SELECT * FROM patients WHERE id = %s OR contact LIKE %s ORDER BY id DESC",
                (int(query), f"%{query}%"),
                fetchall=True
            ) or []
        else:
            results = execute_query(
                "SELECT * FROM patients WHERE name LIKE %s OR contact LIKE %s OR symptoms LIKE %s ORDER BY id DESC",
                (f"%{query}%", f"%{query}%", f"%{query}%"),
                fetchall=True
            ) or []

    return render_template('search_patient.html', query=query, results=results)

# ================= API ENDPOINTS ==================
@app.route('/api/medicines')
def api_medicines():
    return jsonify(MEDICINES_CATALOG)

# ================= INITIALIZE & RUN ==================
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
