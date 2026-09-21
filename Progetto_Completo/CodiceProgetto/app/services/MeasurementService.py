from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from app.daos.MeasurementDAO import MeasurementDAO
from app.daos.AlertDAO import AlertDAO
from app.daos.PatientDAO import PatientDAO
from app.models.Measurement import Measurement
from app.models.Alert import Alert

class MeasurementService:
    """
    Service layer for glycemic readings, threshold validation and clinical alert generation (FR3.1, FR10, FR8, UC1).
    """
    # Normal clinical thresholds
    PRE_MEAL_MIN = 80
    PRE_MEAL_MAX = 130
    POST_MEAL_MAX = 180

    # Critical thresholds
    SEVERE_HYPO_THRESHOLD = 60    # e.g., 40 mg/dL is severe hypoglycemia
    SEVERE_HYPER_THRESHOLD = 250  # severe hyperglycemia

    def __init__(
        self,
        measurement_dao: Optional[MeasurementDAO] = None,
        alert_dao: Optional[AlertDAO] = None,
        patient_dao: Optional[PatientDAO] = None
    ):
        self.measurement_dao = measurement_dao or MeasurementDAO()
        self.alert_dao = alert_dao or AlertDAO()
        self.patient_dao = patient_dao or PatientDAO()

    def record_measurement(
        self,
        patient_id: int,
        glucose_level: Any,
        reading_datetime: Optional[str],
        meal_context: str
    ) -> Tuple[int, Optional[Alert]]:
        """
        Validates data, saves the glycemic reading, checks thresholds,
        and triggers a clinical alert if abnormal (UC1 / FR3.1 / FR10).

        Returns: (reading_id, generated_alert_or_none)
        Raises: ValueError if inputs are invalid.
        """
        # 1. Validation
        val = self._validate_glucose_value(glucose_level)
        context = self._validate_meal_context(meal_context)
        dt_str = self._validate_datetime(reading_datetime)

        patient = self.patient_dao.get_by_user_id(patient_id)
        if not patient:
            raise ValueError(f"Profilo paziente non trovato per l'ID {patient_id}.")

        # 2. Persist measurement
        measurement = Measurement(
            patient_id=patient_id,
            glucose_level=val,
            reading_datetime=dt_str,
            meal_context=context
        )
        reading_id = self.measurement_dao.insert(measurement)

        # 3. Check thresholds (Extension Point 1.2: InviaNotificaAllarmeGlicemia)
        alert = None
        severity, alert_message = self.evaluate_reading(val, context)

        if severity is not None:
            alert = Alert(
                doctor_id=patient.doctor_id,
                patient_id=patient_id,
                severity=severity,
                message=alert_message,
                is_resolved=False
            )
            self.alert_dao.create(alert)

            # High severity triggers simulated emergency email to doctor (FR10 / TC06)
            if severity == Alert.SEVERITY_CRITICAL:
                self._send_emergency_email_alert(patient.doctor_id, alert_message)

        return reading_id, alert

    def evaluate_reading(self, glucose_level: int, meal_context: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Evaluates a glucose reading against clinical guidelines.
        Returns: (severity, alert_message) or (None, None) if normal.
        """
        context_label = "prima del pasto" if meal_context == Measurement.CONTEXT_BEFORE_MEAL else "dopo il pasto"

        # Check critical conditions first
        if glucose_level < self.SEVERE_HYPO_THRESHOLD:
            return (
                Alert.SEVERITY_CRITICAL,
                f"ALLARME CRITICO: Ipoglicemia grave ({glucose_level} mg/dL, {context_label}). Richiesto intervento immediato!"
            )
        if glucose_level >= self.SEVERE_HYPER_THRESHOLD:
            return (
                Alert.SEVERITY_CRITICAL,
                f"ALLARME CRITICO: Iperglicemia severa ({glucose_level} mg/dL, {context_label}). Verificare la terapia!"
            )

        # Check medium severity (Warning) conditions
        if meal_context == Measurement.CONTEXT_BEFORE_MEAL:
            if glucose_level < self.PRE_MEAL_MIN:
                return (
                    Alert.SEVERITY_WARNING,
                    f"ATTENZIONE: Valore glicemico basso ({glucose_level} mg/dL prima del pasto, range atteso 80-130)."
                )
            elif glucose_level > self.PRE_MEAL_MAX:
                return (
                    Alert.SEVERITY_WARNING,
                    f"ATTENZIONE: Valore glicemico elevato ({glucose_level} mg/dL prima del pasto, range atteso 80-130)."
                )
        elif meal_context == Measurement.CONTEXT_AFTER_MEAL:
            if glucose_level > self.POST_MEAL_MAX:
                return (
                    Alert.SEVERITY_WARNING,
                    f"ATTENZIONE: Valore glicemico post-prandiale elevato ({glucose_level} mg/dL dopo il pasto, limite <180)."
                )

        # Normal reading
        return (None, None)

    def get_patient_readings(self, patient_id: int, limit: int = 50) -> List[Measurement]:
        """Fetches recent readings for patient."""
        return self.measurement_dao.get_by_patient_id(patient_id, limit)

    def get_summary_report(self, patient_id: int, days: int = 30) -> Dict[str, Any]:
        """
        Computes clinical statistics for doctor review over a period (FR8 - weekly/monthly analysis).
        """
        readings = self.measurement_dao.get_by_patient_and_period(patient_id, days)

        if not readings:
            return {
                'count': 0,
                'average': 0.0,
                'min': 0,
                'max': 0,
                'in_target_count': 0,
                'in_target_percent': 0.0,
                'readings': []
            }

        values = [r.glucose_level for r in readings]
        avg_val = round(sum(values) / len(values), 1)
        min_val = min(values)
        max_val = max(values)

        # Count in target:
        # Pre-meal: 80-130, Post-meal: < 180
        in_target = 0
        for r in readings:
            if r.meal_context == Measurement.CONTEXT_BEFORE_MEAL and (self.PRE_MEAL_MIN <= r.glucose_level <= self.PRE_MEAL_MAX):
                in_target += 1
            elif r.meal_context == Measurement.CONTEXT_AFTER_MEAL and (r.glucose_level <= self.POST_MEAL_MAX):
                in_target += 1

        in_target_pct = round((in_target / len(readings)) * 100, 1)

        return {
            'count': len(readings),
            'average': avg_val,
            'min': min_val,
            'max': max_val,
            'in_target_count': in_target,
            'in_target_percent': in_target_pct,
            'readings': readings
        }

    def _validate_glucose_value(self, value: Any) -> int:
        try:
            val = int(value)
        except (ValueError, TypeError):
            raise ValueError("Il valore glicemico deve essere un numero intero valido.")
        if val <= 0:
            raise ValueError("Il valore glicemico deve essere positivo.")
        if val < 20 or val > 600:
            raise ValueError("Il valore glicemico inserito è al di fuori dei limiti fisiologici (20-600 mg/dL).")
        return val

    def _validate_meal_context(self, context: str) -> str:
        if not context or context.strip() not in Measurement.VALID_CONTEXTS:
            raise ValueError("Il contesto del pasto deve essere 'BEFORE_MEAL' o 'AFTER_MEAL'.")
        return context.strip()

    def _validate_datetime(self, dt_str: Optional[str]) -> str:
        if not dt_str or not dt_str.strip():
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Format normalization
        cleaned = dt_str.strip().replace("T", " ")
        if len(cleaned) == 16:  # YYYY-MM-DD HH:MM
            cleaned += ":00"
        return cleaned

    def _send_emergency_email_alert(self, doctor_id: int, message: str):
        """Simulates automatic emergency email dispatch for critical alerts (TC06 / FR10)."""
        print(f"[SIMULATED EMAIL TO DOCTOR #{doctor_id}] Oggetto: ALLARME CLINICO CRITICO - {message}")
