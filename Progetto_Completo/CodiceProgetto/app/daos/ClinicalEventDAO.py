from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.ClinicalEvent import ClinicalEvent

class ClinicalEventDAO:
    """DAO for managing clinical events like symptoms, pathologies, and other medications (FR3.2)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, event: ClinicalEvent) -> int:
        """Inserts a new clinical event."""
        query = """
            INSERT INTO clinical_events (patient_id, event_type, description, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            event.patient_id,
            event.event_type,
            event.description.strip(),
            event.start_date,
            event.end_date if event.end_date else None
        )
        event_id = self.db.execute_query(query, params)
        event.id = event_id
        return event_id

    def get_by_patient_id(self, patient_id: int) -> List[ClinicalEvent]:
        """Fetches all clinical events for a specific patient, newest first."""
        query = """
            SELECT * FROM clinical_events
            WHERE patient_id = ?
            ORDER BY start_date DESC, id DESC
        """
        rows = self.db.fetch_all(query, (patient_id,))
        return [ClinicalEvent.from_row(row) for row in rows]

    def delete(self, event_id: int, patient_id: int) -> bool:
        """Deletes a clinical event belonging to a patient."""
        query = "DELETE FROM clinical_events WHERE id = ? AND patient_id = ?"
        return self.db.execute_query(query, (event_id, patient_id)) > 0
