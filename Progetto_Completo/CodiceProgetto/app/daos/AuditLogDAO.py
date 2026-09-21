from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.AuditLog import AuditLog

class AuditLogDAO:
    """
    DAO for managing immutable audit logs of doctor actions (FR12, NFR2).
    STRICTLY APPEND-ONLY: No update or delete operations are implemented or allowed.
    """
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def insert_log(self, audit_log: AuditLog) -> int:
        """
        Appends an immutable audit log entry.
        Only INSERT operations are permitted by design (NFR2).
        """
        query = """
            INSERT INTO audit_logs (doctor_id, action, patient_id, details)
            VALUES (?, ?, ?, ?)
        """
        params = (
            audit_log.doctor_id,
            audit_log.action,
            audit_log.patient_id,
            audit_log.details.strip() if audit_log.details else None
        )
        log_id = self.db.execute_query(query, params)
        audit_log.id = log_id
        return log_id

    def get_all(self, limit: int = 100) -> List[AuditLog]:
        """Fetches recent audit logs ordered by timestamp descending."""
        query = """
            SELECT
                a.*,
                (d.first_name || ' ' || d.last_name) AS doctor_name,
                (p.first_name || ' ' || p.last_name) AS patient_name
            FROM audit_logs a
            JOIN users d ON a.doctor_id = d.id
            LEFT JOIN users p ON a.patient_id = p.id
            ORDER BY a.timestamp DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (limit,))
        return [AuditLog.from_row(row) for row in rows]

    def get_by_doctor_id(self, doctor_id: int, limit: int = 50) -> List[AuditLog]:
        """Fetches audit logs recorded for a specific doctor."""
        query = """
            SELECT
                a.*,
                (d.first_name || ' ' || d.last_name) AS doctor_name,
                (p.first_name || ' ' || p.last_name) AS patient_name
            FROM audit_logs a
            JOIN users d ON a.doctor_id = d.id
            LEFT JOIN users p ON a.patient_id = p.id
            WHERE a.doctor_id = ?
            ORDER BY a.timestamp DESC
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (doctor_id, limit))
        return [AuditLog.from_row(row) for row in rows]
