-- =====================================================================
-- 🏥 CareHub Multispeciality Hospital - MySQL Workbench Database Script
-- Database: hospital
-- =====================================================================

CREATE DATABASE IF NOT EXISTS hospital;
USE hospital;

-- ================= 1. PATIENTS TABLE =================
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(15) NOT NULL,
    weight INT NOT NULL,
    contact VARCHAR(15) NOT NULL,
    symptoms TEXT NOT NULL,
    medicines TEXT NOT NULL,
    total_amount INT NOT NULL,
    payment_mode VARCHAR(20) NOT NULL DEFAULT 'Cash',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================= 2. APPOINTMENTS TABLE =================
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_name VARCHAR(100) NOT NULL,
    appoint_date DATE NOT NULL,
    appoint_time VARCHAR(20) NOT NULL,
    doctor VARCHAR(100) NOT NULL,
    contact VARCHAR(15),
    status VARCHAR(20) DEFAULT 'Scheduled',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================= 3. DOCTORS TABLE =================
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    available_days VARCHAR(100) DEFAULT 'Mon-Sat',
    room_no VARCHAR(20) DEFAULT 'Room 101'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ================= 4. SEED DOCTORS DATA =================
INSERT IGNORE INTO doctors (id, name, specialization, available_days, room_no) VALUES
(1, 'Dr. Rajesh Sharma', 'General Physician', 'Mon-Sat', 'Cabin A-101'),
(2, 'Dr. Ananya Iyer', 'Cardiologist', 'Mon-Fri', 'Cabin B-204'),
(3, 'Dr. Vikram Patil', 'Pediatrician', 'Tue-Sun', 'Cabin A-105'),
(4, 'Dr. Priya Menon', 'Dermatologist & Allergist', 'Mon-Sat', 'Cabin C-302'),
(5, 'Dr. Suresh Kumar', 'Orthopedic Surgeon', 'Mon-Fri', 'Cabin D-401');

-- ================= 5. USEFUL VERIFICATION QUERIES =================
-- View all registered patients:
-- SELECT * FROM patients ORDER BY id DESC;

-- View all scheduled appointments:
-- SELECT * FROM appointments ORDER BY appoint_date ASC, appoint_time ASC;

-- View hospital revenue summary:
-- SELECT COUNT(*) AS total_patients, SUM(total_amount) AS total_revenue FROM patients;
