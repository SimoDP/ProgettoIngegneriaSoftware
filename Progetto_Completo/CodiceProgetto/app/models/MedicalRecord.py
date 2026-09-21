from typing import Optional
import sqlite3

class MedicalRecord:
    """Medical record entity representing chronic conditions and risk factors (FR7)."""
    def __init__(
        self,
        patient_id: int,
        is_smoker: bool = False,
        has_alcohol_issues: bool = False,
        has_hypertension: bool = False,
        has_obesity: bool = False
    ):
        self.patient_id = patient_id
        self.is_smoker = bool(is_smoker)
        self.has_alcohol_issues = bool(has_alcohol_issues)
        self.has_hypertension = bool(has_hypertension)
        self.has_obesity = bool(has_obesity)

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'MedicalRecord':
        if row is None:
            return None
        return cls(
            patient_id=row['patient_id'],
            is_smoker=bool(row['is_smoker']),
            has_alcohol_issues=bool(row['has_alcohol_issues']),
            has_hypertension=bool(row['has_hypertension']),
            has_obesity=bool(row['has_obesity'])
        )

    def to_dict(self) -> dict:
        return {
            'patient_id': self.patient_id,
            'is_smoker': self.is_smoker,
            'has_alcohol_issues': self.has_alcohol_issues,
            'has_hypertension': self.has_hypertension,
            'has_obesity': self.has_obesity
        }
