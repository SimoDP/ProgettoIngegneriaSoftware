from typing import Optional, List
from app.database.DatabaseManager import DatabaseManager
from app.models.Message import Message

class MessageDAO:
    """DAO for managing communication between patients and doctors (FR11)."""
    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()

    def create(self, message: Message) -> int:
        """Inserts a new message."""
        query = """
            INSERT INTO messages (sender_id, receiver_id, content)
            VALUES (?, ?, ?)
        """
        params = (message.sender_id, message.receiver_id, message.content.strip())
        msg_id = self.db.execute_query(query, params)
        message.id = msg_id
        return msg_id

    def get_conversation(self, user1_id: int, user2_id: int) -> List[Message]:
        """Fetches the conversation thread between two users, chronologically ordered."""
        query = """
            SELECT
                m.*,
                (s.first_name || ' ' || s.last_name) AS sender_name,
                (r.first_name || ' ' || r.last_name) AS receiver_name
            FROM messages m
            JOIN users s ON m.sender_id = s.id
            JOIN users r ON m.receiver_id = r.id
            WHERE (m.sender_id = ? AND m.receiver_id = ?)
               OR (m.sender_id = ? AND m.receiver_id = ?)
            ORDER BY m.sent_at ASC
        """
        rows = self.db.fetch_all(query, (user1_id, user2_id, user2_id, user1_id))
        return [Message.from_row(row) for row in rows]
