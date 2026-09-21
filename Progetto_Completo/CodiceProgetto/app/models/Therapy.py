from typing import Optional
import sqlite3

class Therapy:
    """Therapy entity representing a medical prescription for a patient (FR5)."""
    def __init__(
        self,
        id: Optional[int] = None,
        patient_id: int = 0,
        doctor_id: int = 0,
        drug_name: str = "",
        daily_doses: int = 1,
        quantity_per_dose: float = 1.0,
        instructions: Optional[str] = None,
        is_active: bool = True,
        start_date: str = "",
        doctor_name: str = ""
    ):
        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.drug_name = drug_name
        self.daily_doses = daily_doses
        self.quantity_per_dose = quantity_per_dose
        self.instructions = instructions
        self.is_active = bool(is_active)
        self.start_date = start_date
        self.doctor_name = doctor_name

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Therapy':
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            doctor_id=row['doctor_id'],
            drug_name=row['drug_name'],
            daily_doses=row['daily_doses'],
            quantity_per_dose=float(row['quantity_per_dose']),
            instructions=row['instructions'] if 'instructions' in keys else None,
            is_active=bool(row['is_active']),
            start_date=str(row['start_date']),
            doctor_name=row['doctor_name'] if 'doctor_name' in keys else ""
        )
