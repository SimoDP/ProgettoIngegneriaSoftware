from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.User import User

class UserDAO:
    """DAO for managing User entities."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, user: User) -> int:
        """Inserts a new user and returns generated ID."""
        query = """
            INSERT INTO users (email, password_hash, first_name, last_name, role, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            user.email.strip().lower(),
            user.password_hash,
            user.first_name.strip(),
            user.last_name.strip(),
            user.role,
            1 if user.is_active else 0
        )
        user_id = self.db.execute_query(query, params)
        user.id = user_id
        return user_id

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetches a user by ID."""
        query = "SELECT * FROM users WHERE id = ?"
        row = self.db.fetch_one(query, (user_id,))
        return User.from_row(row) if row else None

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetches a user by email (case-insensitive)."""
        query = "SELECT * FROM users WHERE LOWER(email) = LOWER(?)"
        row = self.db.fetch_one(query, (email.strip(),))
        return User.from_row(row) if row else None

    def get_all_by_role(self, role: int) -> List[User]:
        """Fetches all users with a specific role."""
        query = "SELECT * FROM users WHERE role = ? AND is_active = 1 ORDER BY last_name, first_name"
        rows = self.db.fetch_all(query, (role,))
        return [User.from_row(row) for row in rows]

    def update_password(self, user_id: int, password_hash: str) -> bool:
        """Updates user password hash."""
        query = "UPDATE users SET password_hash = ? WHERE id = ?"
        return self.db.execute_query(query, (password_hash, user_id)) > 0
