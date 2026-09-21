from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from app.daos.TherapyDAO import TherapyDAO
from app.daos.MedicationIntakeDAO import MedicationIntakeDAO
from app.daos.PatientDAO import PatientDAO
from app.daos.AlertDAO import AlertDAO
from app.services.AuditService import AuditService
from app.models.Therapy import Therapy
from app.models.MedicationIntake import MedicationIntake
from app.models.Alert import Alert

class TherapyService:
    """
    Service layer for therapy prescription, intake logging, consistency verification
    and adherence monitoring (FR4, FR5, FR6, FR9, FR12, FR13, UC2, UC3).
    """
    def __init__(
        self,
        therapy_dao: Optional[TherapyDAO] = None,
        intake_dao: Optional[MedicationIntakeDAO] = None,
        patient_dao: Optional[PatientDAO] = None,
        alert_dao: Optional[AlertDAO] = None,
        audit_service: Optional[AuditService] = None
    ):
        self.therapy_dao = therapy_dao or TherapyDAO()
        self.intake_dao = intake_dao or MedicationIntakeDAO()
        self.patient_dao = patient_dao or PatientDAO()
        self.alert_dao = alert_dao or AlertDAO()
        self.audit_service = audit_service or AuditService()

    def save_therapy(
        self,
        patient_id: int,
        doctor_id: int,
        drug_name: str,
        daily_doses: Any,
        quantity_per_dose: Any,
        instructions: Optional[str] = None,
        start_date: Optional[str] = None
    ) -> int:
        """
        Validates and persists a therapy prescription, and writes an audit log (UC2 / FR5 / FR12).
        """
        if not drug_name or not drug_name.strip():
            raise ValueError("Il nome del farmaco è obbligatorio.")

        try:
            doses = int(daily_doses)
            if doses <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("Il numero di assunzioni giornaliere deve essere un numero intero positivo.")

        try:
            qty = float(quantity_per_dose)
            if qty <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("La quantità per dose deve essere un numero positivo.")

        if not start_date or not start_date.strip():
            start_date = date.today().isoformat()

        therapy = Therapy(
            patient_id=patient_id,
            doctor_id=doctor_id,
            drug_name=drug_name.strip(),
            daily_doses=doses,
            quantity_per_dose=qty,
            instructions=instructions.strip() if instructions else None,
            is_active=True,
            start_date=start_date
        )

        # Upsert therapy (deactivates previous for same drug, inserts new)
        therapy_id = self.therapy_dao.upsert_therapy(therapy)

        # Include: Registra Audit Log (FR12 / NFR2 / UC2)
        self.audit_service.log_therapy_update(
            doctor_id=doctor_id,
            patient_id=patient_id,
            drug_name=drug_name.strip(),
            dose=qty
        )

        return therapy_id

    def get_active_therapies(self, patient_id: int) -> List[Therapy]:
        """Returns all active therapies for a patient."""
        return self.therapy_dao.get_active_by_patient(patient_id)

    def get_all_therapies(self, patient_id: int) -> List[Therapy]:
        """Returns complete therapy history for a patient."""
        return self.therapy_dao.get_all_by_patient(patient_id)

    def record_intake(
        self,
        patient_id: int,
        drug_name: str,
        quantity_taken: Any,
        intake_datetime: Optional[str] = None
    ) -> Tuple[int, bool, Optional[str]]:
        """
        Records medication intake and checks consistency against active prescriptions (UC3 / FR4 / FR6).
        Returns: (intake_id, is_consistent, warning_message)
        """
        if not drug_name or not drug_name.strip():
            raise ValueError("Il nome del farmaco è obbligatorio.")

        try:
            qty = float(quantity_taken)
            if qty <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError("La quantità assunta deve essere un numero positivo.")

        if not intake_datetime or not intake_datetime.strip():
            intake_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            intake_datetime = intake_datetime.strip().replace("T", " ")
            if len(intake_datetime) == 16:
                intake_datetime += ":00"

        # Check consistency against active therapy (FR6 / UC3 Extension Point 3.2)
        active_therapy = self.therapy_dao.get_active_by_patient_and_drug(patient_id, drug_name.strip())
        is_consistent = True
        warning_msg = None
        therapy_id = None

        if active_therapy is None:
            # Drug is not in active therapy
            is_consistent = False
            warning_msg = f"Il farmaco '{drug_name}' non risulta tra le terapie attualmente prescritte dal medico."
        else:
            therapy_id = active_therapy.id
            if abs(qty - active_therapy.quantity_per_dose) > 0.001:
                is_consistent = False
                warning_msg = (
                    f"Quantità assunta ({qty}) diversa da quella prescritta "
                    f"({active_therapy.quantity_per_dose}) per il farmaco '{active_therapy.drug_name}'."
                )

        # Persist intake
        intake = MedicationIntake(
            patient_id=patient_id,
            therapy_id=therapy_id,
            drug_name=drug_name.strip(),
            intake_datetime=intake_datetime,
            quantity_taken=qty,
            is_consistent=is_consistent
        )
        intake_id = self.intake_dao.insert(intake)

        # If inconsistent, notify doctor via warning alert (FR6 / TC10)
        if not is_consistent:
            patient = self.patient_dao.get_by_user_id(patient_id)
            if patient:
                alert = Alert(
                    doctor_id=patient.doctor_id,
                    patient_id=patient_id,
                    severity=Alert.SEVERITY_WARNING,
                    message=f"INCOERENZA TERAPIA: {warning_msg}",
                    is_resolved=False
                )
                self.alert_dao.create(alert)

        return intake_id, is_consistent, warning_msg

    def get_patient_intakes(self, patient_id: int, limit: int = 50) -> List[MedicationIntake]:
        """Fetches recent intakes logged by patient."""
        return self.intake_dao.get_by_patient_id(patient_id, limit)

    def check_adherence_alerts_for_doctor(self, doctor_id: int) -> int:
        """
        Dynamically checks for lack of therapy adherence (>3 consecutive days)
        for all patients assigned to this doctor (FR13 / TC18).
        Run on doctor dashboard load to avoid background threads.
        Returns number of new alerts generated.
        """
        patients = self.patient_dao.get_all_by_doctor_id(doctor_id)
        new_alerts_count = 0
        now = datetime.now()

        for pat in patients:
            active_therapies = self.therapy_dao.get_active_by_patient(pat.user_id)
            if not active_therapies:
                continue  # No active therapy to monitor

            last_intake_str = self.intake_dao.get_last_intake_datetime(pat.user_id)
            days_inactive = 0

            if last_intake_str is None:
                # Patient has active therapy but has never logged an intake since assignment
                # Check therapy start date
                oldest_start = min(t.start_date for t in active_therapies)
                try:
                    start_dt = datetime.strptime(str(oldest_start)[:10], "%Y-%m-%d")
                    days_inactive = (now - start_dt).days
                except Exception:
                    days_inactive = 4
            else:
                try:
                    last_dt = datetime.strptime(str(last_intake_str)[:19], "%Y-%m-%d %H:%M:%S")
                    days_inactive = (now - last_dt).days
                except Exception:
                    try:
                        last_dt = datetime.strptime(str(last_intake_str)[:10], "%Y-%m-%d")
                        days_inactive = (now - last_dt).days
                    except Exception:
                        days_inactive = 0

            # If inactive for more than 3 consecutive days
            if days_inactive > 3:
                keyword = "mancata aderenza"
                if not self.alert_dao.exists_unresolved_alert(doctor_id, pat.user_id, keyword):
                    alert = Alert(
                        doctor_id=doctor_id,
                        patient_id=pat.user_id,
                        severity=Alert.SEVERITY_WARNING,
                        message=f"ALLARME MANCATA ADERENZA: Il paziente {pat.full_name} non registra assunzioni di farmaci da {days_inactive} giorni.",
                        is_resolved=False
                    )
                    self.alert_dao.create(alert)
                    new_alerts_count += 1

        return new_alerts_count

    def check_patient_reminders(self, patient_id: int) -> Optional[str]:
        """
        Checks if the patient has forgotten to record medication intakes today (FR9 / TC17).
        Returns a friendly reminder message if intake is missing, or None.
        """
        active_therapies = self.therapy_dao.get_active_by_patient(patient_id)
        if not active_therapies:
            return None

        today_str = date.today().isoformat()
        last_intake = self.intake_dao.get_last_intake_datetime(patient_id)

        if not last_intake or not str(last_intake).startswith(today_str):
            drugs = ", ".join([t.drug_name for t in active_therapies])
            return f"Promemoria giornaliero: Non hai ancora registrato l'assunzione odierna dei tuoi farmaci ({drugs})."

        return None
