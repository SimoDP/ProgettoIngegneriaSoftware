-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- 1. Base table for all users (Authentication & Authorization)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role INTEGER NOT NULL CHECK (role IN (0, 1, 2)), -- 0: Patient, 1: Doctor, 2: Admin
    is_active BOOLEAN DEFAULT 1
);

-- 2. Patient specific demographic and doctor association
CREATE TABLE IF NOT EXISTS patients (
    user_id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    date_of_birth DATE,
    gender CHAR(1) CHECK (gender IN ('M', 'F', 'O')),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

-- 3. Patient Medical Record (FR7: Risk factors, comorbidities)
CREATE TABLE IF NOT EXISTS medical_records (
    patient_id INTEGER PRIMARY KEY,
    is_smoker BOOLEAN DEFAULT 0,
    has_alcohol_issues BOOLEAN DEFAULT 0,
    has_hypertension BOOLEAN DEFAULT 0,
    has_obesity BOOLEAN DEFAULT 0,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

-- 4. Clinical Events (FR3.2: Symptoms, pathologies, concomitant therapies)
CREATE TABLE IF NOT EXISTS clinical_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    event_type VARCHAR(20) NOT NULL CHECK (event_type IN ('SYMPTOM', 'PATHOLOGY', 'OTHER_DRUG')),
    description TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

-- 5. Prescribed Therapies (FR5)
CREATE TABLE IF NOT EXISTS therapies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    drug_name VARCHAR(100) NOT NULL,
    daily_doses INTEGER NOT NULL CHECK (daily_doses > 0),
    quantity_per_dose REAL NOT NULL CHECK (quantity_per_dose > 0),
    instructions VARCHAR(255),
    is_active BOOLEAN DEFAULT 1,
    start_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE,
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);

-- 6. Glycemic Readings (FR3.1)
CREATE TABLE IF NOT EXISTS glycemic_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    glucose_level INTEGER NOT NULL CHECK (glucose_level > 0),
    reading_datetime DATETIME NOT NULL,
    meal_context VARCHAR(20) NOT NULL CHECK (meal_context IN ('BEFORE_MEAL', 'AFTER_MEAL')),
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

-- 7. Medication Intakes by Patient (FR4 & FR6 consistency check)
CREATE TABLE IF NOT EXISTS medication_intakes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    therapy_id INTEGER, -- Nullable if taken drug is not in current therapy
    drug_name VARCHAR(100) NOT NULL,
    intake_datetime DATETIME NOT NULL,
    quantity_taken REAL NOT NULL CHECK (quantity_taken > 0),
    is_consistent BOOLEAN DEFAULT 1,
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE,
    FOREIGN KEY(therapy_id) REFERENCES therapies(id) ON DELETE SET NULL
);

-- 8. Clinical Alerts (FR10, FR13)
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('WARNING', 'CRITICAL')),
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(doctor_id) REFERENCES users(id),
    FOREIGN KEY(patient_id) REFERENCES patients(user_id) ON DELETE CASCADE
);

-- 9. Internal Messages / Communications (FR11)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL,
    receiver_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(sender_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY(receiver_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 10. Audit Log for Doctor Operations (FR12 / NFR2: strictly append-only)
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    patient_id INTEGER,
    details TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(doctor_id) REFERENCES users(id)
);
