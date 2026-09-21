from typing import Optional, List
from app.daos.AlertDAO import AlertDAO
from app.services.AuditService import AuditService
from app.models.Alert import Alert
from app.models.AuditLog import AuditLog

class AlertService:
    """
    Service layer for clinical alerts management (FR10, FR13).
    """
    def __init__(
        self,
        alert_dao: Optional[AlertDAO] = None,
        audit_service: Optional[AuditService] = None
    ):
        self.alert_dao = alert_dao or AlertDAO()
        self.audit_service = audit_service or AuditService()

    def get_unresolved_alerts(self, doctor_id: int) -> List[Alert]:
        """Fetches all active, unresolved alerts for a doctor."""
        return self.alert_dao.get_unresolved_by_doctor(doctor_id)

    def get_all_alerts(self, doctor_id: int, limit: int = 50) -> List[Alert]:
        """Fetches all alerts for a doctor."""
        return self.alert_dao.get_all_by_doctor(doctor_id, limit)

    def resolve_alert(self, alert_id: int, doctor_id: int) -> bool:
        """Marks an alert as resolved and records an audit log entry."""
        success = self.alert_dao.mark_as_resolved(alert_id, doctor_id)
        if success:
            self.audit_service.log_operation(
                doctor_id=doctor_id,
                action=AuditLog.ACTION_RESOLVE_ALERT,
                details=f"Risolto allarme #{alert_id}"
            )
        return success
