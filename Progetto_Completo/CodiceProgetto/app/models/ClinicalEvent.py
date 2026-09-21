from typing import Optional
import sqlite3

class ClinicalEvent:
    """Clinical event entity for symptoms, concurrent pathologies, and therapies (FR3.2)."""
    TYPE_SYMPTOM = 'SYMPTOM'
    TYPE_PATHOLOGY = 'PATHOLOGY'
    TYPE_OTHER_DRUG = 'OTHER_DRUG'

    VALID_TYPES = [TYPE_SYMPTOM, TYPE_PATHOLOGY, TYPE_OTHER_DRUG]

    def __init__(
        self,
        id: Optional[int] = None,
        patient_id: int = 0,
        event_type: str = TYPE_SYMPTOM,
        description: str = "",
        start_date: str = "",
        end_date: Optional[str] = None
    ):
        self.id = id
        self.patient_id = patient_id
        self.event_type = event_type
        self.description = description
        self.start_date = start_date
        self.end_date = end_date

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'ClinicalEvent':
        if row is None:
            return None
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            event_type=row['event_type'],
            description=row['description'],
            start_date=row['start_date'],
            end_date=row['end_date']
        )
