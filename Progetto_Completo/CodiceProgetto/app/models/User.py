from typing import Optional
import sqlite3

class User:
    """User entity representing a user in the telemedicine system."""
    ROLE_PATIENT = 0
    ROLE_DOCTOR = 1
    ROLE_ADMIN = 2

    def __init__(
        self,
        id: Optional[int] = None,
        email: str = "",
        password_hash: str = "",
        first_name: str = "",
        last_name: str = "",
        role: int = ROLE_PATIENT,
        is_active: bool = True
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.is_active = bool(is_active)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def is_patient(self) -> bool:
        return self.role == self.ROLE_PATIENT

    def is_doctor(self) -> bool:
        return self.role == self.ROLE_DOCTOR

    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'User':
        if row is None:
            return None
        return cls(
            id=row['id'],
            email=row['email'],
            password_hash=row['password_hash'],
            first_name=row['first_name'],
            last_name=row['last_name'],
            role=row['role'],
            is_active=bool(row['is_active'])
        )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'is_active': self.is_active
        }
