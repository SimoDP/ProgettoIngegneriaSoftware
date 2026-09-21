from typing import Optional, List
from app.daos.MedicalRecordDAO import MedicalRecordDAO
from app.daos.ClinicalEventDAO import ClinicalEventDAO
from app.services.AuditService import AuditService
from app.models.MedicalRecord import MedicalRecord
from app.models.ClinicalEvent import ClinicalEvent

class MedicalRecordService:
    """
    Service layer for managing patient medical records (FR7),
    clinical events (FR3.2), and auditing medical updates (FR12, UC7).
    """
    def __init__(
        self,
        record_dao: Optional[MedicalRecordDAO] = None,
        event_dao: Optional[ClinicalEventDAO] = None,
        audit_service: Optional[AuditService] = None
    ):
        self.record_dao = record_dao or MedicalRecordDAO()
        self.event_dao = event_dao or ClinicalEventDAO()
        self.audit_service = audit_service or AuditService()

    def get_patient_record(self, patient_id: int) -> MedicalRecord:
        """Fetches the patient medical record or returns a blank one."""
        record = self.record_dao.get_by_patient_id(patient_id)
        if not record:
            record = MedicalRecord(patient_id=patient_id)
        return record

    def update_patient_record(
        self,
        doctor_id: int,
        patient_id: int,
        is_smoker: bool,
        has_alcohol_issues: bool,
        has_hypertension: bool,
        has_obesity: bool
    ) -> bool:
        """
        Updates medical record and creates audit log entry (UC7 / FR7 / FR12).
        """
        record = MedicalRecord(
            patient_id=patient_id,
            is_smoker=is_smoker,
            has_alcohol_issues=has_alcohol_issues,
            has_hypertension=has_hypertension,
            has_obesity=has_obesity
        )
        success = self.record_dao.upsert(record)

        # Tracing with Audit Log (FR12 / TC15)
        details = (
            f"Aggiornati fattori di rischio/comorbilità: "
            f"Fumo={is_smoker}, Alcol={has_alcohol_issues}, "
            f"Ipertensione={has_hypertension}, Obesità={has_obesity}"
        )
        self.audit_service.log_medical_record_update(
            doctor_id=doctor_id,
            patient_id=patient_id,
            details=details
        )
        return success

    def add_clinical_event(
        self,
        patient_id: int,
        event_type: str,
        description: str,
        start_date: str,
        end_date: Optional[str] = None
    ) -> int:
        """
        Registers a symptom, pathology, or concurrent medication (FR3.2 / UC6 / TC08).
        """
        if event_type not in ClinicalEvent.VALID_TYPES:
            raise ValueError(f"Tipo di evento clinico '{event_type}' non valido.")
        if not description or not description.strip():
            raise ValueError("La descrizione dell'evento clinico è obbligatoria.")
        if not start_date or not start_date.strip():
            raise ValueError("La data di inizio dell'evento è obbligatoria.")

        event = ClinicalEvent(
            patient_id=patient_id,
            event_type=event_type,
            description=description.strip(),
            start_date=start_date.strip(),
            end_date=end_date.strip() if end_date and end_date.strip() else None
        )
        return self.event_dao.create(event)

    def get_clinical_events(self, patient_id: int) -> List[ClinicalEvent]:
        """Fetches all clinical events for a patient."""
        return self.event_dao.get_by_patient_id(patient_id)

    def delete_clinical_event(self, event_id: int, patient_id: int) -> bool:
        """Deletes a clinical event belonging to a patient."""
        return self.event_dao.delete(event_id, patient_id)
