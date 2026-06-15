import pymysql
import tkinter as t
from tkinter import messagebox,Tk
from tkinter import ttk
from PIL import Image, ImageTk
import qrcode
import pywhatkit as pk
import pyautogui as pg
import time
import datetime

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
        messagebox.showinfo("Success", "Patient record saved successfully!")
    except Exception as e:
        messagebox.showerror("Database Error", str(e))

# ================= BILL GENERATION ==================
def generate_bill(name, age, gender, weight, contact, symptoms, payment_mode):
    total = 0
    items = []

    for s in symptoms:
        if s in medicines:
            for med, price in medicines[s]:
                items.append((med, price))
                total += price

    bill_text = "\n" + "="*45 + "\n"
    bill_text += "🏥 CareHub Multispeciality Hospital\n"
    bill_text += "-"*45 + "\n"
    bill_text += f"Patient Name : {name}\n"
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

    # Save to DB
    save_patient_to_db(name, age, gender, weight, contact, symptoms, items, total, payment_mode)

    # Show bill
    messagebox.showinfo("Bill Generated", bill_text)


    # WhatsApp automation (send bill text)
    try:
        send_whatsapp = messagebox.askyesno("Send WhatsApp", "Do you want to send this bill via WhatsApp?")
        if send_whatsapp:
            phone_no = "+91" + contact
            pk.sendwhatmsg_instantly(phone_no, bill_text, wait_time=10, tab_close=False)
            time.sleep(10)
            pg.press("enter")
            messagebox.showinfo("Success", "Bill sent via WhatsApp!")
    except Exception as e:
        messagebox.showerror("WhatsApp Error", str(e))

    # If GPay, generate QR
    if payment_mode.lower() == "gpay":
        upi_id = "nandhakumar.s.jnandhu-1@okhdfcbank"
        data = f"upi://pay?pa={upi_id}&pn=CareHub&am={total}&cu=INR"
        qr = qrcode.make(data)
        qr.show()

# ================== ADD PATIENT FORM ==================
def open_add_patient():
    add_win = t.Toplevel(main)
    add_win.title("Add Patient")
    add_win.geometry("1920x1080")

    # ✅ Background image (full screen)
    bg_img = Image.open("patient_bg.png")
    bg_img = bg_img.resize((1920, 1080))   # resize to full screen
    bg_photo = ImageTk.PhotoImage(bg_img)

    bg_label = t.Label(add_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # stretch full screen

    # Title
    t.Label(add_win, text="Add Patient", font=("Arial bold", 28), fg="black").pack(pady=15)

    # Form entries
    labels = ["Name", "Age", "Gender (male/female)", "Weight", "Contact (10 digits)",
              "Symptoms (comma separated)", "Payment Mode (Cash/GPay)"]
    entries = {}

    for lbl in labels:
        t.Label(add_win, text=lbl, font=("Arial", 16), fg="black").pack(pady=8)  # Removed bg="white"
        ent = t.Entry(add_win, font=("Arial", 14), width=40)
        ent.pack(pady=5)
        entries[lbl] = ent

    # Submit function
    def submit_patient():
        try:
            name = entries["Name"].get().strip()
            age = int(entries["Age"].get().strip())
            gender = entries["Gender (male/female)"].get().strip().lower()
            weight = int(entries["Weight"].get().strip())
            contact = entries["Contact (10 digits)"].get().strip()
            symptoms = [s.strip() for s in entries["Symptoms (comma separated)"].get().lower().split(",") if s.strip() in medicines]
            payment_mode = entries["Payment Mode (Cash/GPay)"].get().strip()

            if not (name and gender and contact and symptoms):
                messagebox.showerror("Input Error", "Fill all required fields properly")
                return
            if len(contact) != 10 or not contact.isdigit():
                messagebox.showerror("Input Error", "Invalid contact number")
                return
            if gender not in ["male", "female"]:
                messagebox.showerror("Input Error", "Gender must be male/female")
                return

            generate_bill(name, age, gender, weight, contact, symptoms, payment_mode)
            add_win.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Submit button
    t.Button(add_win, text="Submit", font=("Arial bold", 16),
             bg="#1E88E5", fg="white", command=submit_patient).pack(pady=25)


# ================== APPOINTMENT SCHEDULER =================
def open_appointment_window():
    ap_win = t.Toplevel(main)
    ap_win.title("Appointments")
    ap_win.geometry("1920x1080")
    ap_win.configure(bg="#f2f2f2")

    # ===== MAIN FRAME CENTERED =====
    main_frame = t.Frame(ap_win, bg="white", bd=3, relief="groove")
    main_frame.place(relx=0.5, rely=0.5, anchor="center", width=1000, height=700)

    t.Label(main_frame, text="🩺 Appointment Scheduling System",
            font=("Arial Bold", 24), bg="white", fg="#1E88E5").pack(pady=15)

    # ===== INPUT SECTION =====
    input_frame = t.LabelFrame(main_frame, text="Book Appointment", font=("Arial", 12, "bold"),
                               bg="white", padx=10, pady=10)
    input_frame.pack(fill="x", padx=20, pady=10)

    labels = ["Patient Name", "Doctor", "Date (YYYY-MM-DD)", "Time (include AM or PM)"]
    entries = []

    for i, label in enumerate(labels):
        t.Label(input_frame, text=label, bg="white", font=("Arial", 11)).grid(row=i, column=0, padx=10, pady=8, sticky="e")
        ent = t.Entry(input_frame, width=40, font=("Arial", 11))
        ent.grid(row=i, column=1, padx=10, pady=8)
        entries.append(ent)

    name_ent, doctor_ent, date_ent, time_ent = entries

    # ===== ADD APPOINTMENT FUNCTION =====
    def add_appointment():
        patient_name = name_ent.get().strip()
        doctor = doctor_ent.get().strip()
        date_str = date_ent.get().strip()
        time_slot = time_ent.get().strip()

        if not (patient_name and doctor and date_str and time_slot):
            messagebox.showerror("Input Error", "Please fill all fields!")
            return

        try:
            dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            messagebox.showerror("Date Error", "Date must be in YYYY-MM-DD format!")
            return

        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO appointments (patient_name, appoint_date, appoint_time, doctor)
                    VALUES (%s, %s, %s, %s)
                """, (patient_name, dt, time_slot, doctor))
            conn.commit()
            messagebox.showinfo("Success", "✅ Appointment booked successfully!")
            for e in entries:
                e.delete(0, t.END)
            refresh_appointments()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            try:
                conn.close()
            except:
                pass

    t.Button(input_frame, text="Book Appointment", bg="#43A047", fg="white",
             font=("Arial", 12, "bold"), width=20, command=add_appointment).grid(row=4, column=0, columnspan=2, pady=10)

    # ===== TABLE SECTION =====
    tv_frame = t.LabelFrame(main_frame, text="Booked Appointments", font=("Arial", 12, "bold"),
                            bg="white", padx=10, pady=10)
    tv_frame.pack(fill="both", expand=True, padx=20, pady=10)

    cols = ("id", "name", "date", "time", "doctor")
    tree = ttk.Treeview(tv_frame, columns=cols, show="headings", height=10)

    for c in cols:
        tree.heading(c, text=c.title())
        tree.column(c, anchor="center", width=180)
    tree.pack(fill="both", expand=True, side="left")

    scrollbar = ttk.Scrollbar(tv_frame, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # ===== REFRESH FUNCTION =====
    def refresh_appointments():
        for row in tree.get_children():
            tree.delete(row)
        try:
            conn = get_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, patient_name, appoint_date, appoint_time, doctor FROM appointments ORDER BY appoint_date DESC, appoint_time DESC")
                for r in cursor.fetchall():
                    tree.insert("", t.END, values=r)
        except Exception as e:
            messagebox.showerror("Database Error", str(e))
        finally:
            try:
                conn.close()
            except:
                pass

    # ===== DELETE FUNCTION =====
    def delete_selected():
        sel = tree.selection()
        if not sel:
            messagebox.showerror("Selection Error", "Select an appointment to delete!")
            return
        item = tree.item(sel[0])
        appt_id = item["values"][0]
        if messagebox.askyesno("Confirm", "Delete selected appointment?"):
            try:
                conn = get_connection()
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM appointments WHERE id=%s", (appt_id,))
                conn.commit()
                refresh_appointments()
                messagebox.showinfo("Deleted", "🗑️ Appointment deleted successfully!")
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
            finally:
                try:
                    conn.close()
                except:
                    pass

    t.Button(main_frame, text="Delete Selected Appointment", bg="#E53935", fg="white",
             font=("Arial", 12, "bold"), width=25, command=delete_selected).pack(pady=8)

    refresh_appointments()

# ================== SEARCH PATIENT ==================
def open_search_patient():
    search_win = t.Toplevel(main)
    search_win.title("Search Patient")
    search_win.geometry("1920x1080")
    #bg image
    bg_img = Image.open("bg_search.jpg")
    bg_img = bg_img.resize((1920, 1080))
    bg_photo = ImageTk.PhotoImage(bg_img)

    bg_label = t.Label(search_win, image=bg_photo)
    bg_label.image = bg_photo
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    t.Label(search_win, text="🔍Search Patient", font=("Arial bold", 22),bg="#975935",fg="white").pack(pady=20)
    t.Label(search_win, text="Enter Name or Contact:", font=("Arial", 14),bg="#975935",fg="white").pack(pady=20)
    search_entry = t.Entry(search_win, font=("Arial", 14), width=25)
    search_entry.pack(pady=10)

    result_box = t.Text(search_win, font=("Arial", 12), height=15, width=60)
    result_box.pack(pady=20)

    def do_search():
        query = search_entry.get().strip()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE name=%s OR contact=%s", (query, query))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        result_box.delete("1.0", t.END)
        if results:
            for row in results:
                result_box.insert(t.END, str(row) + "\n")
        else:
            result_box.insert(t.END, "❌ No patient found!")

    t.Button(search_win, text="Search", font=("Arial bold", 14),bg="#1E88E5", fg="white", command=do_search).pack(pady=10)

# ================= LOGIN FUNCTION ==================
def login():
    admin_user = "admin"
    admin_pass = "1234"

    username = lg_user.get().strip()
    password = lg_pass.get().strip()

    if not username or not password:
        messagebox.showerror("Field Error", "Fill All the Inputs")
        return

    if username == admin_user and password == admin_pass:
        messagebox.showinfo("Login", "Login Successful !!")
        dg.tkraise()
    else:
        messagebox.showerror("Login Error", "Invalid User")

# ================= MAIN UI ==================
main = t.Tk()
main.title("🏥 CareHub Hospital System")
main.geometry("1920x1080")

container = t.Frame(main)
lg = t.Frame(container)
dg = t.Frame(container)

for page in (lg, dg):
    page.place(x=0, y=0, relwidth=1, relheight=1)


# login page
bg_img = Image.open("bg_login.jpg")
bg_img = bg_img.resize((1920, 1080))
bg_photo = ImageTk.PhotoImage(bg_img)

bg_label = t.Label(lg, image=bg_photo)
bg_label.image = bg_photo
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

t.Label(lg, text="Login Form", font=("Arial bold", 25),bg="#ffffff").place(relx=0.5, y=80, anchor="center")
t.Label(lg, text="User", font=("Arial bold", 18),bg="#ffffff").place(relx=0.4, rely=0.3, anchor="e")
lg_user = t.Entry(lg, font=("Arial", 18), bg="white", width=18)
lg_user.place(relx=0.5, rely=0.3, anchor="w")
t.Label(lg, text="Password", font=("Arial bold", 18),bg="#ffffff").place(relx=0.4, rely=0.4, anchor="e")
lg_pass = t.Entry(lg, font=("Arial", 18), bg="white", show="*", width=18)
lg_pass.place(relx=0.5, rely=0.4, anchor="w")
t.Button(lg, text="Login", font=("Arial bold", 18), command=login).place(relx=0.5, rely=0.5, anchor="center")


# dashboard page
bg_img = Image.open("dg_page.jpg")
bg_img = bg_img.resize((1920, 1080))
bg_photo = ImageTk.PhotoImage(bg_img)

bg_label = t.Label(dg, image=bg_photo)
bg_label.image = bg_photo
bg_label.place(x=0, y=0, relwidth=1, relheight=1)
t.Label(dg, text="🏥 CareHub Dashboard", font=("Arial bold", 25), bg="#fae3b9").place(relx=0.5, rely=0.1, anchor="center")
t.Button(dg, text="Add Patient & Generate Bill", font=("Arial bold", 18),bg="#ffffb7", command=open_add_patient).place(relx=0.5, rely=0.3, anchor="center")
t.Button(dg, text="Appointments", font=("Arial bold", 16),bg="#ffffb7", command=open_appointment_window).place(relx=0.5, rely=0.4, anchor="center")
t.Button(dg, text="Search Patient", font=("Arial bold", 18),bg="#ffffb7", command=open_search_patient).place(relx=0.5, rely=0.5, anchor="center")
t.Button(dg, text="Exit", font=("Arial bold", 18),bg="#ffffb7",command=main.quit).place(relx=0.5, rely=0.6, anchor="center")

lg.tkraise()
container.pack(fill="both", expand=True)

main.mainloop()