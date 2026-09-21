from typing import Optional
import sqlite3

class MedicationIntake:
    """Medication intake entity representing a dose logged by the patient (FR4, FR6)."""
    def __init__(
        self,
        id: Optional[int] = None,
        patient_id: int = 0,
        therapy_id: Optional[int] = None,
        drug_name: str = "",
        intake_datetime: str = "",
        quantity_taken: float = 1.0,
        is_consistent: bool = True
    ):
        self.id = id
        self.patient_id = patient_id
        self.therapy_id = therapy_id
        self.drug_name = drug_name
        self.intake_datetime = intake_datetime
        self.quantity_taken = quantity_taken
        self.is_consistent = bool(is_consistent)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'MedicationIntake':
        if row is None:
            return None
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            therapy_id=row['therapy_id'] if 'therapy_id' in row.keys() else None,
            drug_name=row['drug_name'],
            intake_datetime=str(row['intake_datetime']),
            quantity_taken=float(row['quantity_taken']),
            is_consistent=bool(row['is_consistent'])
        )
