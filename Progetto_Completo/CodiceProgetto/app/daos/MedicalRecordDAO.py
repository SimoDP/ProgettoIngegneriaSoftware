from typing import Optional
from app.database.DatabaseManager import DatabaseManager
from app.models.MedicalRecord import MedicalRecord

class MedicalRecordDAO:
    """DAO for managing patient risk factors and comorbidities (FR7)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def get_by_patient_id(self, patient_id: int) -> Optional[MedicalRecord]:
        """Fetches the medical record for a given patient."""
        query = "SELECT * FROM medical_records WHERE patient_id = ?"
        row = self.db.fetch_one(query, (patient_id,))
        return MedicalRecord.from_row(row) if row else None

    def upsert(self, record: MedicalRecord) -> bool:
        """Inserts or updates the patient medical record."""
        query = """
            INSERT INTO medical_records (
                patient_id, is_smoker, has_alcohol_issues, has_hypertension, has_obesity
            ) VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(patient_id) DO UPDATE SET
                is_smoker = excluded.is_smoker,
                has_alcohol_issues = excluded.has_alcohol_issues,
                has_hypertension = excluded.has_hypertension,
                has_obesity = excluded.has_obesity
        """
        params = (
            record.patient_id,
            1 if record.is_smoker else 0,
            1 if record.has_alcohol_issues else 0,
            1 if record.has_hypertension else 0,
            1 if record.has_obesity else 0
        )
        return self.db.execute_query(query, params) >= 0
