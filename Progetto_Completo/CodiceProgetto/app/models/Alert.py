from typing import Optional
import sqlite3

class Alert:
    """Alert entity for abnormal measurements and adherence warnings (FR10, FR13)."""
    SEVERITY_WARNING = 'WARNING'
    SEVERITY_CRITICAL = 'CRITICAL'

    VALID_SEVERITIES = [SEVERITY_WARNING, SEVERITY_CRITICAL]

    def __init__(
        self,
        id: Optional[int] = None,
        doctor_id: int = 0,
        patient_id: int = 0,
        severity: str = SEVERITY_WARNING,
        message: str = "",
        is_resolved: bool = False,
        created_at: str = "",
        patient_name: str = ""
    ):
        self.id = id
        self.doctor_id = doctor_id
        self.patient_id = patient_id
        self.severity = severity
        self.message = message
        self.is_resolved = bool(is_resolved)
        self.created_at = created_at
        self.patient_name = patient_name

    @property
    def severity_badge_class(self) -> str:
        """CSS badge class for UI."""
        return "danger" if self.severity == self.SEVERITY_CRITICAL else "warning"

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Alert':
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row['id'],
            doctor_id=row['doctor_id'],
            patient_id=row['patient_id'],
            severity=row['severity'],
            message=row['message'],
            is_resolved=bool(row['is_resolved']),
            created_at=str(row['created_at']) if 'created_at' in keys else "",
            patient_name=row['patient_name'] if 'patient_name' in keys else ""
        )
