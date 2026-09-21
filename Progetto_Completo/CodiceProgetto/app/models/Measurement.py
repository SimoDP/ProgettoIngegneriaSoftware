from typing import Optional
import sqlite3

class Measurement:
    """Measurement entity representing a blood glucose reading (FR3.1)."""
    CONTEXT_BEFORE_MEAL = 'BEFORE_MEAL'
    CONTEXT_AFTER_MEAL = 'AFTER_MEAL'

    VALID_CONTEXTS = [CONTEXT_BEFORE_MEAL, CONTEXT_AFTER_MEAL]

    def __init__(
        self,
        id: Optional[int] = None,
        patient_id: int = 0,
        glucose_level: int = 0,
        reading_datetime: str = "",
        meal_context: str = CONTEXT_BEFORE_MEAL
    ):
        self.id = id
        self.patient_id = patient_id
        self.glucose_level = glucose_level
        self.reading_datetime = reading_datetime
        self.meal_context = meal_context

    @property
    def meal_context_label(self) -> str:
        """Italian readable label for the UI."""
        return "Prima del pasto" if self.meal_context == self.CONTEXT_BEFORE_MEAL else "Dopo il pasto"

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Measurement':
        if row is None:
            return None
        return cls(
            id=row['id'],
            patient_id=row['patient_id'],
            glucose_level=row['glucose_level'],
            reading_datetime=str(row['reading_datetime']),
            meal_context=row['meal_context']
        )

# Alias for domain consistency
GlycemicReading = Measurement
