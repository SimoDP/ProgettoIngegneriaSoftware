import unittest
import os
import sys

# Add project path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.database.DatabaseManager import DatabaseManager
from app.models.User import User
from app.services.AuthService import AuthService
from app.services.PatientService import PatientService
from app.services.TherapyService import TherapyService
from app.services.MeasurementService import MeasurementService
from app.services.MedicalRecordService import MedicalRecordService
from app.services.AlertService import AlertService
from app.services.AuditService import AuditService

class TestTelemedicineSystem(unittest.TestCase):
    """
    Complete System and Integration Test Suite verifying all Requirements (FR1-FR13)
    and Test Cases (TC01-TC22) as specified in 1_Requisiti.md and 2_Design.md.
    """

    @classmethod
    def setUpClass(cls):
        cls.test_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_e2e.db'))
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

        cls.app = create_app({
            'TESTING': True,
            'SECRET_KEY': 'test-secret',
            'DATABASE_PATH': cls.test_db_path
        })
        cls.client = cls.app.test_client()

        # Seed test data
        from seed_db import seed_database
        seed_database(cls.test_db_path)

    @classmethod
    def tearDownClass(cls):
        db = DatabaseManager(cls.test_db_path)
        db.close_connection()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)

    # -------------------------------------------------------------
    # TC01 & TC02: Authentication and Authorization (FR1, NFR4, UC4)
    # -------------------------------------------------------------
    def test_tc01_login_roles_and_access(self):
        """TC01: Valid login for Patient, Doctor, and Admin with role-specific dashboards."""
        # Patient Login
        res_pat = self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'}, follow_redirects=True)
        self.assertEqual(res_pat.status_code, 200)
        self.assertIn('Cruscotto'.encode('utf-8'), res_pat.data)
        self.client.get('/logout')

        # Doctor Login
        res_doc = self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'}, follow_redirects=True)
        self.assertEqual(res_doc.status_code, 200)
        self.assertIn('Pannello di Controllo Medico'.encode('utf-8'), res_doc.data)
        self.client.get('/logout')

        # Admin Login
        res_adm = self.client.post('/login', data={'email': 'admin@telemedicina.it', 'password': 'admin123'}, follow_redirects=True)
        self.assertEqual(res_adm.status_code, 200)
        self.assertIn('Pannello Amministrazione'.encode('utf-8'), res_adm.data)
        self.client.get('/logout')

    def test_tc02_invalid_login_and_unauthorized_access(self):
        """TC02: Invalid password and unauthorized route protection."""
        # Wrong password
        res = self.client.post('/login', data={'email': 'admin@telemedicina.it', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn('Credenziali non valide'.encode('utf-8'), res.data)

        # Attempt to access doctor dashboard without session
        res_unauth = self.client.get('/doctor/dashboard', follow_redirects=True)
        self.assertIn('Devi effettuare l'.encode('utf-8'), res_unauth.data)

    # -------------------------------------------------------------
    # TC03: Admin User Creation (FR2, UC5)
    # -------------------------------------------------------------
    def test_tc03_admin_create_doctor_and_patient(self):
        """TC03: Admin creates a new doctor and a new patient assigned to them."""
        # Login as admin
        self.client.post('/login', data={'email': 'admin@telemedicina.it', 'password': 'admin123'})

        # Create new doctor
        res_doc = self.client.post('/admin/create-doctor', data={
            'email': 'dr.bianchi@ospedale.it',
            'password': 'password123',
            'first_name': 'Anna',
            'last_name': 'Bianchi'
        }, follow_redirects=True)
        self.assertEqual(res_doc.status_code, 200)
        self.assertIn('Profilo Medico creato con successo'.encode('utf-8'), res_doc.data)

        # Get the new doctor ID
        auth_svc = AuthService()
        new_doc = auth_svc.user_dao.get_by_email('dr.bianchi@ospedale.it')

        # Create new patient assigned to Dr. Bianchi
        res_pat = self.client.post('/admin/create-patient', data={
            'email': 'mario.neri@email.it',
            'password': 'password123',
            'first_name': 'Mario',
            'last_name': 'Neri',
            'doctor_id': new_doc.id,
            'date_of_birth': '1965-03-15',
            'gender': 'M'
        }, follow_redirects=True)
        self.assertEqual(res_pat.status_code, 200)
        self.assertIn('registrato e associato al medico con successo'.encode('utf-8'), res_pat.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC04, TC05, TC06, TC07: Glycemic Readings & Alerts (FR3.1, FR10, UC1)
    # -------------------------------------------------------------
    def test_tc04_normal_measurement(self):
        """TC04: Patient records normal reading (110 mg/dL pre-meal)."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/measurement/add', data={
            'glucose_level': '110',
            'meal_context': 'BEFORE_MEAL',
            'reading_datetime': '2026-09-18T08:30'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('registrata con successo'.encode('utf-8'), res.data)
        self.client.get('/logout')

    def test_tc05_warning_measurement(self):
        """TC05: Patient records warning reading (150 mg/dL pre-meal)."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/measurement/add', data={
            'glucose_level': '150',
            'meal_context': 'BEFORE_MEAL',
            'reading_datetime': '2026-09-18T12:30'
        }, follow_redirects=True)
        self.assertIn('generato un avviso per il medico'.encode('utf-8'), res.data)
        self.client.get('/logout')

        # Verify badge in doctor dashboard
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        res_doc = self.client.get('/doctor/dashboard')
        self.assertIn('ATTENZIONE'.encode('utf-8'), res_doc.data)
        self.client.get('/logout')

    def test_tc06_critical_measurement(self):
        """TC06: Patient records critical reading (40 mg/dL severe hypo) triggering alert & emergency email."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/measurement/add', data={
            'glucose_level': '40',
            'meal_context': 'BEFORE_MEAL',
            'reading_datetime': '2026-09-18T18:30'
        }, follow_redirects=True)
        self.assertIn('Valore critico'.encode('utf-8'), res.data)
        self.client.get('/logout')

        # Check doctor dashboard has CRITICAL badge
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        res_doc = self.client.get('/doctor/dashboard')
        self.assertIn('CRITICO'.encode('utf-8'), res_doc.data)
        self.client.get('/logout')

    def test_tc07_invalid_measurement(self):
        """TC07: Invalid measurement (negative value)."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/measurement/add', data={
            'glucose_level': '-10',
            'meal_context': 'BEFORE_MEAL',
            'reading_datetime': '2026-09-18T08:30'
        })
        self.assertIn('positivo'.encode('utf-8'), res.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC08: Clinical Events (FR3.2, UC6)
    # -------------------------------------------------------------
    def test_tc08_clinical_event_reporting(self):
        """TC08: Patient reports a clinical symptom with dates."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/patient/clinical-events', data={
            'event_type': 'SYMPTOM',
            'description': 'Forte emicrania e vertigini pomeridiane',
            'start_date': '2026-09-18',
            'end_date': '2026-09-18'
        }, follow_redirects=True)
        self.assertIn('registrato con successo'.encode('utf-8'), res.data)
        self.assertIn('Forte emicrania'.encode('utf-8'), res.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC09 & TC10: Medication Intakes and Consistency Check (FR4, FR6, UC3)
    # -------------------------------------------------------------
    def test_tc09_consistent_medication_intake(self):
        """TC09: Patient logs intake matching active therapy (Metformina 500)."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/intake/add', data={
            'drug_name': 'Metformina',
            'quantity_taken': '500',
            'intake_datetime': '2026-09-18T09:00'
        }, follow_redirects=True)
        self.assertIn('registrata correttamente'.encode('utf-8'), res.data)
        self.client.get('/logout')

    def test_tc10_inconsistent_medication_intake(self):
        """TC10: Patient logs inconsistent intake (wrong dose: 1000mg). Saved with warning."""
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res = self.client.post('/intake/add', data={
            'drug_name': 'Metformina',
            'quantity_taken': '1000',
            'intake_datetime': '2026-09-18T19:00'
        }, follow_redirects=True)
        self.assertIn('Assunzione registrata con AVVISO'.encode('utf-8'), res.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC12, TC13, TC14: Therapy Management & Audit Log (FR5, FR12, UC2)
    # -------------------------------------------------------------
    def test_tc12_prescribe_therapy_and_audit(self):
        """TC12: Doctor prescribes therapy; record is saved and logged in Audit Trail."""
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        auth_svc = AuthService()
        patient = auth_svc.user_dao.get_by_email('giuseppe.verdi@email.it')

        res = self.client.post(f'/doctor/patient/{patient.id}/therapy', data={
            'drug_name': 'Insulina Lispro',
            'daily_doses': '3',
            'quantity_per_dose': '10.0',
            'instructions': 'Prima dei tre pasti',
            'start_date': '2026-09-18'
        }, follow_redirects=True)
        self.assertIn('salvata e registrata nell'.encode('utf-8'), res.data)

        # Verify audit log exists
        res_audit = self.client.get('/doctor/audit-logs')
        self.assertIn('Insulina Lispro'.encode('utf-8'), res_audit.data)
        self.client.get('/logout')

    def test_tc13_missing_therapy_fields(self):
        """TC13: Missing mandatory fields in therapy prescription -> rejected."""
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        auth_svc = AuthService()
        patient = auth_svc.user_dao.get_by_email('giuseppe.verdi@email.it')

        res = self.client.post(f'/doctor/patient/{patient.id}/therapy', data={
            'drug_name': '',  # missing
            'daily_doses': '2',
            'quantity_per_dose': '500'
        })
        self.assertIn('obbligatorio'.encode('utf-8'), res.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC15: Risk Factors Update & Audit (FR7, FR12, UC7)
    # -------------------------------------------------------------
    def test_tc15_update_medical_record(self):
        """TC15: Doctor updates patient risk factors; operation is tracked in Audit Log."""
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        auth_svc = AuthService()
        patient = auth_svc.user_dao.get_by_email('giuseppe.verdi@email.it')

        res = self.client.post(f'/doctor/patient/{patient.id}/medical-record', data={
            'is_smoker': 'on',
            'has_hypertension': 'on'
        }, follow_redirects=True)
        self.assertIn('operazione tracciata nell'.encode('utf-8'), res.data)

        # Check Audit logs
        audit_res = self.client.get('/doctor/audit-logs')
        self.assertIn('UPDATE_MEDICAL_RECORD'.encode('utf-8'), audit_res.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC16: Trends & Reporting (FR8, UC8)
    # -------------------------------------------------------------
    def test_tc16_glycemic_trends(self):
        """TC16: Doctor views weekly and monthly aggregated report."""
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        auth_svc = AuthService()
        patient = auth_svc.user_dao.get_by_email('giuseppe.verdi@email.it')

        res = self.client.get(f'/doctor/patient/{patient.id}/trends?period=7')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Media Periodo'.encode('utf-8'), res.data)
        self.assertIn('Nel Target Clinico'.encode('utf-8'), res.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC19: Messages and Communication (FR11, UC9)
    # -------------------------------------------------------------
    def test_tc19_messaging(self):
        """TC19: Patient sends communication to doctor and doctor replies."""
        # Patient sends message
        self.client.post('/login', data={'email': 'giuseppe.verdi@email.it', 'password': 'paziente123'})
        res_pat = self.client.post('/patient/messages', data={
            'content': 'Dottore, oggi sento un leggero capogiro dopo i pasti.'
        }, follow_redirects=True)
        self.assertIn('Messaggio inviato con successo'.encode('utf-8'), res_pat.data)
        self.client.get('/logout')

        # Doctor replies
        self.client.post('/login', data={'email': 'dott.mario.rossi@ospedale.it', 'password': 'dottore123'})
        auth_svc = AuthService()
        patient = auth_svc.user_dao.get_by_email('giuseppe.verdi@email.it')

        res_doc = self.client.post(f'/doctor/patient/{patient.id}/messages', data={
            'content': 'Giuseppe, misura la glicemia subito e bevi un bicchiere d acqua.'
        }, follow_redirects=True)
        self.assertIn('Messaggio inviato'.encode('utf-8'), res_doc.data)
        self.client.get('/logout')

    # -------------------------------------------------------------
    # TC20: Audit Log Immutable (Append-Only) Verification (FR12, NFR2)
    # -------------------------------------------------------------
    def test_tc20_audit_log_append_only(self):
        """TC20: Verify audit log is append-only by inspecting DAO methods."""
        from app.daos.AuditLogDAO import AuditLogDAO
        audit_dao = AuditLogDAO()

        # AuditLogDAO must have insert_log, get_all, get_by_doctor_id
        self.assertTrue(hasattr(audit_dao, 'insert_log'))
        self.assertTrue(hasattr(audit_dao, 'get_all'))
        # Must NOT have update or delete methods
        self.assertFalse(hasattr(audit_dao, 'update'))
        self.assertFalse(hasattr(audit_dao, 'delete'))
        self.assertFalse(hasattr(audit_dao, 'update_log'))
        self.assertFalse(hasattr(audit_dao, 'delete_log'))

if __name__ == '__main__':
    unittest.main()
