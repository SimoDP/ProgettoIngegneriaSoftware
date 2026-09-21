from typing import Optional, List
from app.daos.MessageDAO import MessageDAO
from app.daos.UserDAO import UserDAO
from app.models.Message import Message

class MessageService:
    """
    Service layer for internal messaging and simulated email communication between
    patient and assigned doctor (FR11, UC9).
    """
    def __init__(
        self,
        message_dao: Optional[MessageDAO] = None,
        user_dao: Optional[UserDAO] = None
    ):
        self.message_dao = message_dao or MessageDAO()
        self.user_dao = user_dao or UserDAO()

    def send_message(self, sender_id: int, receiver_id: int, content: str) -> int:
        """
        Sends an internal communication message / simulated email.
        Validates content and recipient.
        """
        if not content or not content.strip():
            raise ValueError("Il testo del messaggio non può essere vuoto.")

        receiver = self.user_dao.get_by_id(receiver_id)
        if not receiver:
            raise ValueError("Destinatario non trovato.")

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content.strip()
        )
        msg_id = self.message_dao.create(message)

        # Log simulated email dispatch (FR11 / TC19)
        sender = self.user_dao.get_by_id(sender_id)
        sender_name = sender.full_name if sender else f"ID {sender_id}"
        print(f"[SIMULATED EMAIL DISPATCH] Da: {sender_name} A: {receiver.email} | Testo: {content.strip()}")

        return msg_id

    def get_conversation(self, user1_id: int, user2_id: int) -> List[Message]:
        """Fetches the conversation thread between two users."""
        return self.message_dao.get_conversation(user1_id, user2_id)
