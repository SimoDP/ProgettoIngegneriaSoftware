import os
import sys

# Ensure app package is in Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.database.DatabaseManager import DatabaseManager
from app.services.AuthService import AuthService
from app.services.PatientService import PatientService
from app.services.TherapyService import TherapyService
from app.services.MedicalRecordService import MedicalRecordService
from app.services.MeasurementService import MeasurementService
from app.models.User import User

def seed_database(db_path: str = None):
    """
    Initializes the database and seeds it with default users:
    - 1 Administrator (Default setup so system is not locked)
    - 1 Diabetologist Doctor
    - 1 Diabetic Patient associated with the Doctor
    - Initial baseline clinical record, therapy, and readings
    """
    print("--- Inizializzazione e Popolamento Database TeleDiabete ---")

    if db_path is None:
        db_path = os.path.join(current_dir, 'app', 'database', 'telemedicine.db')

    db_manager = DatabaseManager(db_path)
    db_manager.init_db()

    auth_service = AuthService()
    patient_service = PatientService()
    therapy_service = TherapyService()
    record_service = MedicalRecordService()
    measurement_service = MeasurementService()

    # 1. Create Default Admin User
    admin_email = "admin@telemedicina.it"
    existing_admin = auth_service.user_dao.get_by_email(admin_email)
    if not existing_admin:
        admin_user = auth_service.register_user(
            email=admin_email,
            raw_password="admin123",
            first_name="Responsabile",
            last_name="Amministratore",
            role=User.ROLE_ADMIN
        )
        print(f"[OK] Creato Utente Amministratore: {admin_user.email} (Password: admin123)")
    else:
        admin_user = existing_admin
        print(f"[INFO] Utente Amministratore già esistente: {admin_user.email}")

    # 2. Create Default Doctor
    doctor_email = "dott.mario.rossi@ospedale.it"
    existing_doctor = auth_service.user_dao.get_by_email(doctor_email)
    if not existing_doctor:
        doctor_user = auth_service.register_user(
            email=doctor_email,
            raw_password="dottore123",
            first_name="Mario",
            last_name="Rossi",
            role=User.ROLE_DOCTOR
        )
        print(f"[OK] Creato Utente Medico: {doctor_user.email} (Password: dottore123)")
    else:
        doctor_user = existing_doctor
        print(f"[INFO] Utente Medico già esistente: {doctor_user.email}")

    # 3. Create Default Patient associated with Doctor
    patient_email = "giuseppe.verdi@email.it"
    existing_patient_user = auth_service.user_dao.get_by_email(patient_email)
    if not existing_patient_user:
        patient = patient_service.register_patient(
            email=patient_email,
            password="paziente123",
            first_name="Giuseppe",
            last_name="Verdi",
            doctor_id=doctor_user.id,
            date_of_birth="1955-06-20",
            gender="M"
        )
        print(f"[OK] Creato Utente Paziente: {patient_email} (Password: paziente123) associato a Dr. {doctor_user.full_name}")

        # 4. Create Initial Medical Record (FR7)
        record_service.update_patient_record(
            doctor_id=doctor_user.id,
            patient_id=patient.user_id,
            is_smoker=False,
            has_alcohol_issues=False,
            has_hypertension=True,
            has_obesity=True
        )
        print("[OK] Inizializzato Fascicolo Clinico (Fattori di rischio: Ipertensione e Obesità)")

        # 5. Prescribe Initial Therapy (FR5 / UC2)
        th_id = therapy_service.save_therapy(
            patient_id=patient.user_id,
            doctor_id=doctor_user.id,
            drug_name="Metformina",
            daily_doses=2,
            quantity_per_dose=500.0,
            instructions="Una compressa dopo colazione e una dopo cena",
            start_date="2026-09-01"
        )
        print("[OK] Prescritta Terapia Iniziale: Metformina 500mg (2 volte al giorno)")

        # 6. Add a Clinical Event (FR3.2 / UC6)
        record_service.add_clinical_event(
            patient_id=patient.user_id,
            event_type="SYMPTOM",
            description="Leggera spossatezza al risveglio",
            start_date="2026-09-15"
        )
        print("[OK] Inserito Sintomo Iniziale: Spossatezza al risveglio")

        # 7. Add Baseline Measurements (FR3.1 / UC1)
        measurement_service.record_measurement(
            patient_id=patient.user_id,
            glucose_level=110,
            reading_datetime="2026-09-17 08:00:00",
            meal_context="BEFORE_MEAL"
        )
        measurement_service.record_measurement(
            patient_id=patient.user_id,
            glucose_level=155,
            reading_datetime="2026-09-17 14:00:00",
            meal_context="AFTER_MEAL"
        )
        print("[OK] Inserite Misurazioni Glicemiche di base")
    else:
        print(f"[INFO] Utente Paziente già esistente: {patient_email}")

    print("\n--- Setup Completato con Successo! ---")
    print("Credenziali predefinite create:")
    print("1. AMMINISTRATORE -> Email: admin@telemedicina.it | Password: admin123")
    print("2. MEDICO         -> Email: dott.mario.rossi@ospedale.it | Password: dottore123")
    print("3. PAZIENTE       -> Email: giuseppe.verdi@email.it | Password: paziente123")

if __name__ == '__main__':
    seed_database()
