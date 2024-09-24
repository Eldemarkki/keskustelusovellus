from db import db
from sqlalchemy.sql import text

def get_thread_messages(thread_id: int):
    messages = db.session.execute(text(
        """
            SELECT 
                messages.id,
                messages.message,
                messages.created_at,
                users.username
            FROM messages 
            LEFT JOIN users ON messages.user_id = users.id
            WHERE thread_id = :thread_id 
            ORDER BY created_at DESC
        """), {
        "thread_id": thread_id
    })

    return messages

def create_message(user_id: int, thread_id: int, message: str):
    db.session.execute(text("INSERT INTO messages (user_id, thread_id, message) VALUES (:user_id, :thread_id, :message)"), {
            "user_id": user_id,
            "thread_id": thread_id,
            "message": message  
        })
    
    db.session.commit()