from typing import Optional
import sqlite3

class Message:
    """Internal message entity between patient and doctor (FR11)."""
    def __init__(
        self,
        id: Optional[int] = None,
        sender_id: int = 0,
        receiver_id: int = 0,
        content: str = "",
        sent_at: str = "",
        sender_name: str = "",
        receiver_name: str = ""
    ):
        self.id = id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.sent_at = sent_at
        self.sender_name = sender_name
        self.receiver_name = receiver_name

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> 'Message':
        if row is None:
            return None
        keys = row.keys()
        return cls(
            id=row['id'],
            sender_id=row['sender_id'],
            receiver_id=row['receiver_id'],
            content=row['content'],
            sent_at=str(row['sent_at']) if 'sent_at' in keys else "",
            sender_name=row['sender_name'] if 'sender_name' in keys else "",
            receiver_name=row['receiver_name'] if 'receiver_name' in keys else ""
        )
