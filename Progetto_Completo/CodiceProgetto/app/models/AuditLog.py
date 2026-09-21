from typing import Optional
import sqlite3

class AuditLog:
    """Audit log entity representing immutable tracking of doctor operations (FR12, NFR2)."""
    ACTION_UPDATE_THERAPY = "UPDATE_THERAPY"
    ACTION_UPDATE_MEDICAL_RECORD = "UPDATE_MEDICAL_RECORD"
    ACTION_VIEW_PATIENT = "VIEW_PATIENT"
    ACTION_RESOLVE_ALERT = "RESOLVE_ALERT"

    def __init__(
        self,
        id: Optional[int] = None,
        doctor_id: int = 0,
        action: str = "",
        patient_id: Optional[int] = None,
        details: Optional[str] = None,
        timestamp: str = "",
        doctor_name: str = "",
        patient_name: str = ""
    ):
        self.id = id
        self.doctor_id = doctor_id
        self.action = action
        self.patient_id = patient_id
        self.details = details
        self.timestamp = timestamp
        self.doctor_name = doctor_name
        self.patient_name = patient_name

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'AuditLog':
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row['id'],
            doctor_id=row['doctor_id'],
            action=row['action'],
            patient_id=row['patient_id'] if 'patient_id' in keys else None,
            details=row['details'] if 'details' in keys else None,
            timestamp=str(row['timestamp']) if 'timestamp' in keys else "",
            doctor_name=row['doctor_name'] if 'doctor_name' in keys else "",
            patient_name=row['patient_name'] if 'patient_name' in keys else ""
        )
