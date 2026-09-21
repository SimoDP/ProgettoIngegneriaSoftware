from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.Patient import Patient

class PatientDAO:
    """DAO for managing Patient records and Doctor-Patient associations."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, patient: Patient) -> int:
        """Creates a new patient profile linked to an existing user."""
        query = """
            INSERT INTO patients (user_id, doctor_id, date_of_birth, gender)
            VALUES (?, ?, ?, ?)
        """
        params = (patient.user_id, patient.doctor_id, patient.date_of_birth, patient.gender)
        return self.db.execute_query(query, params)

    def get_by_user_id(self, user_id: int) -> Optional[Patient]:
        """Fetches patient profile with joined user and doctor names."""
        query = """
            SELECT
                p.user_id,
                p.doctor_id,
                p.date_of_birth,
                p.gender,
                u.first_name,
                u.last_name,
                u.email,
                (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM patients p
            JOIN users u ON p.user_id = u.id
            JOIN users d ON p.doctor_id = d.id
            WHERE p.user_id = ?
        """
        row = self.db.fetch_one(query, (user_id,))
        return Patient.from_row(row) if row else None

    def get_all_by_doctor_id(self, doctor_id: int) -> List[Patient]:
        """Fetches all patients assigned to a specific doctor."""
        query = """
            SELECT
                p.user_id,
                p.doctor_id,
                p.date_of_birth,
                p.gender,
                u.first_name,
                u.last_name,
                u.email,
                (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM patients p
            JOIN users u ON p.user_id = u.id
            JOIN users d ON p.doctor_id = d.id
            WHERE p.doctor_id = ?
            ORDER BY u.last_name, u.first_name
        """
        rows = self.db.fetch_all(query, (doctor_id,))
        return [Patient.from_row(row) for row in rows]

    def get_all(self) -> List[Patient]:
        """Fetches all patients in the system (useful for Admin and Doctors)."""
        query = """
            SELECT
                p.user_id,
                p.doctor_id,
                p.date_of_birth,
                p.gender,
                u.first_name,
                u.last_name,
                u.email,
                (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM patients p
            JOIN users u ON p.user_id = u.id
            JOIN users d ON p.doctor_id = d.id
            ORDER BY u.last_name, u.first_name
        """
        rows = self.db.fetch_all(query)
        return [Patient.from_row(row) for row in rows]
