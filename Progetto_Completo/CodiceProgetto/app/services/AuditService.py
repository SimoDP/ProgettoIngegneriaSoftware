from typing import Optional, List
from app.daos.AuditLogDAO import AuditLogDAO
from app.models.AuditLog import AuditLog

class AuditService:
    """
    Service layer for recording doctor audit trails (FR12, NFR2).
    Enforces append-only immutable logging.
    """
    def __init__(self, audit_dao: Optional[AuditLogDAO] = None):
        self.audit_dao = audit_dao or AuditLogDAO()

    def log_operation(
        self,
        doctor_id: int,
        action: str,
        patient_id: Optional[int] = None,
        details: Optional[str] = None
    ) -> int:
        """Appends an immutable audit log entry."""
        audit_entry = AuditLog(
            doctor_id=doctor_id,
            action=action,
            patient_id=patient_id,
            details=details
        )
        return self.audit_dao.insert_log(audit_entry)

    def log_therapy_update(self, doctor_id: int, patient_id: int, drug_name: str, dose: float) -> int:
        """Specialized helper for therapy updates (UC2)."""
        details = f"Prescritta terapia per farmaco '{drug_name}' (dose: {dose})"
        return self.log_operation(doctor_id, AuditLog.ACTION_UPDATE_THERAPY, patient_id, details)

    def log_medical_record_update(self, doctor_id: int, patient_id: int, details: str) -> int:
        """Specialized helper for updating risk factors/comorbidities (UC7)."""
        return self.log_operation(doctor_id, AuditLog.ACTION_UPDATE_MEDICAL_RECORD, patient_id, details)

    def get_recent_logs(self, limit: int = 100) -> List[AuditLog]:
        """Fetches recent audit logs."""
        return self.audit_dao.get_all(limit)

    def get_doctor_logs(self, doctor_id: int, limit: int = 50) -> List[AuditLog]:
        """Fetches audit logs for a specific doctor."""
        return self.audit_dao.get_by_doctor_id(doctor_id, limit)
