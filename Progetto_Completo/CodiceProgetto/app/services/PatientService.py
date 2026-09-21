from typing import Optional, List, Dict, Any
from app.daos.PatientDAO import PatientDAO
from app.daos.UserDAO import UserDAO
from app.services.AuthService import AuthService
from app.models.Patient import Patient
from app.models.User import User

class PatientService:
    """
    Service layer for patient management, registration, and profile administration (FR2, UC5).
    """
    def __init__(
        self,
        patient_dao: Optional[PatientDAO] = None,
        user_dao: Optional[UserDAO] = None,
        auth_service: Optional[AuthService] = None
    ):
        self.patient_dao = patient_dao or PatientDAO()
        self.user_dao = user_dao or UserDAO()
        self.auth_service = auth_service or AuthService(self.user_dao)

    def register_patient(
        self,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        doctor_id: int,
        date_of_birth: Optional[str] = None,
        gender: Optional[str] = None
    ) -> Patient:
        """
        Creates a new Patient user and their associated patient profile (FR2 / UC5 / TC03).
        """
        # Validate doctor exists and is indeed a doctor
        doctor = self.user_dao.get_by_id(doctor_id)
        if not doctor or not doctor.is_doctor():
            raise ValueError("Il medico specificato non esiste o non ha il ruolo di Medico.")

        # Validate gender if provided
        if gender and gender not in ('M', 'F', 'O'):
            raise ValueError("Genere non valido. Utilizzare 'M', 'F' o 'O'.")

        # Create user with role Patient
        user = self.auth_service.register_user(
            email=email,
            raw_password=password,
            first_name=first_name,
            last_name=last_name,
            role=User.ROLE_PATIENT
        )

        patient = Patient(
            user_id=user.id,
            doctor_id=doctor_id,
            date_of_birth=date_of_birth.strip() if date_of_birth else None,
            gender=gender
        )
        self.patient_dao.create(patient)
        return self.patient_dao.get_by_user_id(user.id)

    def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Fetches a patient by their user ID."""
        return self.patient_dao.get_by_user_id(patient_id)

    def get_doctor_patients(self, doctor_id: int) -> List[Patient]:
        """Fetches all patients in care with a specific doctor."""
        return self.patient_dao.get_all_by_doctor_id(doctor_id)

    def get_all_patients(self) -> List[Patient]:
        """Fetches all patients in the system."""
        return self.patient_dao.get_all()
