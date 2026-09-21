from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.Therapy import Therapy

class TherapyDAO:
    """DAO for managing doctor prescribed therapies (FR5)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, therapy: Therapy) -> int:
        """Inserts a new therapy."""
        query = """
            INSERT INTO therapies (
                patient_id, doctor_id, drug_name, daily_doses, quantity_per_dose,
                instructions, is_active, start_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            therapy.patient_id,
            therapy.doctor_id,
            therapy.drug_name.strip(),
            therapy.daily_doses,
            therapy.quantity_per_dose,
            therapy.instructions.strip() if therapy.instructions else None,
            1 if therapy.is_active else 0,
            therapy.start_date
        )
        therapy_id = self.db.execute_query(query, params)
        therapy.id = therapy_id
        return therapy_id

    def upsert_therapy(self, therapy: Therapy) -> int:
        """
        Deactivates any existing active therapy for the same patient and drug,
        then inserts the new updated therapy.
        """
        deactivate_query = """
            UPDATE therapies
            SET is_active = 0
            WHERE patient_id = ? AND LOWER(drug_name) = LOWER(?) AND is_active = 1
        """
        self.db.execute_query(deactivate_query, (therapy.patient_id, therapy.drug_name.strip()))
        return self.create(therapy)

    def get_by_id(self, therapy_id: int) -> Optional[Therapy]:
        """Fetches a therapy by ID."""
        query = """
            SELECT t.*, (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM therapies t
            JOIN users d ON t.doctor_id = d.id
            WHERE t.id = ?
        """
        row = self.db.fetch_one(query, (therapy_id,))
        return Therapy.from_row(row) if row else None

    def get_active_by_patient(self, patient_id: int) -> List[Therapy]:
        """Fetches all currently active therapies for a patient."""
        query = """
            SELECT t.*, (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM therapies t
            JOIN users d ON t.doctor_id = d.id
            WHERE t.patient_id = ? AND t.is_active = 1
            ORDER BY t.start_date DESC
        """
        rows = self.db.fetch_all(query, (patient_id,))
        return [Therapy.from_row(row) for row in rows]

    def get_all_by_patient(self, patient_id: int) -> List[Therapy]:
        """Fetches all therapies (active and historical) for a patient."""
        query = """
            SELECT t.*, (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM therapies t
            JOIN users d ON t.doctor_id = d.id
            WHERE t.patient_id = ?
            ORDER BY t.is_active DESC, t.start_date DESC
        """
        rows = self.db.fetch_all(query, (patient_id,))
        return [Therapy.from_row(row) for row in rows]

    def get_active_by_patient_and_drug(self, patient_id: int, drug_name: str) -> Optional[Therapy]:
        """Fetches active therapy for a patient with matching drug name (case-insensitive)."""
        query = """
            SELECT t.*, (d.first_name || ' ' || d.last_name) AS doctor_name
            FROM therapies t
            JOIN users d ON t.doctor_id = d.id
            WHERE t.patient_id = ? AND LOWER(t.drug_name) = LOWER(?) AND t.is_active = 1
            LIMIT 1
        """
        row = self.db.fetch_one(query, (patient_id, drug_name.strip()))
        return Therapy.from_row(row) if row else None
