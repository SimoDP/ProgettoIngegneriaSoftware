from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.MedicationIntake import MedicationIntake

class MedicationIntakeDAO:
    """DAO for managing patient medication intakes and tracking adherence (FR4, FR6, FR13)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def insert(self, intake: MedicationIntake) -> int:
        """Inserts a medication intake record."""
        query = """
            INSERT INTO medication_intakes (
                patient_id, therapy_id, drug_name, intake_datetime, quantity_taken, is_consistent
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            intake.patient_id,
            intake.therapy_id,
            intake.drug_name.strip(),
            intake.intake_datetime,
            intake.quantity_taken,
            1 if intake.is_consistent else 0
        )
        intake_id = self.db.execute_query(query, params)
        intake.id = intake_id
        return intake_id

    def get_by_patient_id(self, patient_id: int, limit: int = 50) -> List[MedicationIntake]:
        """Fetches medication intakes for a patient ordered by intake_datetime descending."""
        query = """
            SELECT * FROM medication_intakes
            WHERE patient_id = ?
            ORDER BY intake_datetime DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (patient_id, limit))
        return [MedicationIntake.from_row(row) for row in rows]

    def get_last_intake_datetime(self, patient_id: int) -> Optional[str]:
        """
        Returns the latest intake datetime recorded by the patient.
        Used for the dynamic 3-day adherence check (FR13).
        """
        query = """
            SELECT intake_datetime FROM medication_intakes
            WHERE patient_id = ?
            ORDER BY intake_datetime DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (patient_id,))
        return row['intake_datetime'] if row else None
