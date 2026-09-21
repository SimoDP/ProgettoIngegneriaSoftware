from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.Measurement import Measurement

class MeasurementDAO:
    """DAO for managing patient glycemic readings (FR3.1, FR8)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def insert(self, measurement: Measurement) -> int:
        """Inserts a new glycemic reading."""
        query = """
            INSERT INTO glycemic_readings (patient_id, glucose_level, reading_datetime, meal_context)
            VALUES (?, ?, ?, ?)
        """
        params = (
            measurement.patient_id,
            measurement.glucose_level,
            measurement.reading_datetime,
            measurement.meal_context
        )
        reading_id = self.db.execute_query(query, params)
        measurement.id = reading_id
        return reading_id

    def get_by_patient_id(self, patient_id: int, limit: int = 50) -> List[Measurement]:
        """Fetches glycemic readings for a patient ordered by date descending."""
        query = """
            SELECT * FROM glycemic_readings
            WHERE patient_id = ?
            ORDER BY reading_datetime DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (patient_id, limit))
        return [Measurement.from_row(row) for row in rows]

    def get_by_patient_and_period(self, patient_id: int, days: int = 30) -> List[Measurement]:
        """
        Fetches glycemic readings for the last N days (FR8 - weekly/monthly analysis).
        Ordered chronologically ascending for graphing and trend analysis.
        """
        query = """
            SELECT * FROM glycemic_readings
            WHERE patient_id = ?
              AND reading_datetime >= datetime('now', '-' || ? || ' days', 'localtime')
            ORDER BY reading_datetime ASC
        """
        rows = self.db.fetch_all(query, (patient_id, days))
        return [Measurement.from_row(row) for row in rows]

    def get_latest_by_patient(self, patient_id: int) -> Optional[Measurement]:
        """Fetches the most recent measurement for a patient."""
        query = """
            SELECT * FROM glycemic_readings
            WHERE patient_id = ?
            ORDER BY reading_datetime DESC
            LIMIT 1
        """
        row = self.db.fetch_one(query, (patient_id,))
        return Measurement.from_row(row) if row else None
