from typing import Optional
import sqlite3

class Patient:
    """Patient entity representing extended clinical information for a patient user."""
    def __init__(
        self,
        user_id: int,
        doctor_id: int,
        date_of_birth: Optional[str] = None,
        gender: Optional[str] = None,
        # Optional joined fields for convenience in presentation layer
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        doctor_name: str = ""
    ):
        self.user_id = user_id
        self.doctor_id = doctor_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.doctor_name = doctor_name

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Patient':
        if row is None:
            return None
        keys = row.keys()
        return cls(
            user_id=row['user_id'],
            doctor_id=row['doctor_id'],
            date_of_birth=row['date_of_birth'] if 'date_of_birth' in keys else None,
            gender=row['gender'] if 'gender' in keys else None,
            first_name=row['first_name'] if 'first_name' in keys else "",
            last_name=row['last_name'] if 'last_name' in keys else "",
            email=row['email'] if 'email' in keys else "",
            doctor_name=row['doctor_name'] if 'doctor_name' in keys else ""
        )
