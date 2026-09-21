from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from app.daos.UserDAO import UserDAO
from app.models.User import User

class AuthService:
    """
    Service layer for authentication, password hashing and user validation (FR1, NFR4, UC4).
    Uses secure password hashing (scrypt / pbkdf2 via werkzeug.security).
    """
    def __init__(self, user_dao: Optional[UserDAO] = None):
        self.user_dao = user_dao or UserDAO()

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticates a user with email and raw password.
        Returns the User instance if valid, or None if authentication fails.
        """
        if not email or not password:
            return None

        user = self.user_dao.get_by_email(email.strip())
        if not user or not user.is_active:
            return None

        # Verify cryptographic password hash
        if not check_password_hash(user.password_hash, password):
            return None

        return user

    def hash_password(self, raw_password: str) -> str:
        """Generates a secure hash for the given plain text password."""
        if not raw_password or len(raw_password) < 4:
            raise ValueError("La password deve contenere almeno 4 caratteri.")
        return generate_password_hash(raw_password)

    def register_user(
        self,
        email: str,
        raw_password: str,
        first_name: str,
        last_name: str,
        role: int
    ) -> User:
        """
        Registers a new user in the system with hashed password (FR2).
        Validates input fields.
        """
        if not email or "@" not in email:
            raise ValueError("Indirizzo email non valido.")
        if not first_name or not first_name.strip():
            raise ValueError("Il nome è obbligatorio.")
        if not last_name or not last_name.strip():
            raise ValueError("Il cognome è obbligatorio.")
        if role not in (User.ROLE_PATIENT, User.ROLE_DOCTOR, User.ROLE_ADMIN):
            raise ValueError("Ruolo utente non valido.")

        existing = self.user_dao.get_by_email(email.strip())
        if existing:
            raise ValueError(f"Un utente con l'email '{email.strip()}' esiste già nel sistema.")

        password_hash = self.hash_password(raw_password)
        new_user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            role=role,
            is_active=True
        )
        self.user_dao.create(new_user)
        return new_user
