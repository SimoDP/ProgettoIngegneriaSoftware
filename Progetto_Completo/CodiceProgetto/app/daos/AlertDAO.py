from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.Alert import Alert

class AlertDAO:
    """DAO for managing clinical and adherence alerts sent to doctors (FR10, FR13)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, alert: Alert) -> int:
        """Inserts a new clinical alert."""
        query = """
            INSERT INTO alerts (doctor_id, patient_id, severity, message, is_resolved)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            alert.doctor_id,
            alert.patient_id,
            alert.severity,
            alert.message.strip(),
            1 if alert.is_resolved else 0
        )
        alert_id = self.db.execute_query(query, params)
        alert.id = alert_id
        return alert_id

    def get_unresolved_by_doctor(self, doctor_id: int) -> List[Alert]:
        """Fetches all open/unresolved alerts for a doctor, newest first."""
        query = """
            SELECT a.*, (u.first_name || ' ' || u.last_name) AS patient_name
            FROM alerts a
            JOIN users u ON a.patient_id = u.id
            WHERE a.doctor_id = ? AND a.is_resolved = 0
            ORDER BY a.created_at DESC
        """
        rows = self.db.fetch_all(query, (doctor_id,))
        return [Alert.from_row(row) for row in rows]

    def get_all_by_doctor(self, doctor_id: int, limit: int = 50) -> List[Alert]:
        """Fetches all alerts (resolved and unresolved) for a doctor."""
        query = """
            SELECT a.*, (u.first_name || ' ' || u.last_name) AS patient_name
            FROM alerts a
            JOIN users u ON a.patient_id = u.id
            WHERE a.doctor_id = ?
            ORDER BY a.is_resolved ASC, a.created_at DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (doctor_id, limit))
        return [Alert.from_row(row) for row in rows]

    def mark_as_resolved(self, alert_id: int, doctor_id: int) -> bool:
        """Marks an alert as resolved by the doctor."""
        query = "UPDATE alerts SET is_resolved = 1 WHERE id = ? AND doctor_id = ?"
        return self.db.execute_query(query, (alert_id, doctor_id)) > 0

    def exists_unresolved_alert(self, doctor_id: int, patient_id: int, message_keyword: str) -> bool:
        """Checks whether an unresolved alert containing keyword already exists to avoid duplication."""
        query = """
            SELECT id FROM alerts
            WHERE doctor_id = ? AND patient_id = ? AND is_resolved = 0 AND message LIKE ?
            LIMIT 1
        """
        row = self.db.fetch_one(query, (doctor_id, patient_id, f"%{message_keyword}%"))
        return row is not None
