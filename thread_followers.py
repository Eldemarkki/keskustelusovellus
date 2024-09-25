from db import db
from sqlalchemy.sql import text

def follow_thread(thread_id: int, user_id: int):
    db.session.execute(text(
        """
        INSERT INTO thread_followers (thread_id, user_id) VALUES (:thread_id, :user_id)
        """), {
            "thread_id": thread_id,
            "user_id": user_id,
        })
    db.session.commit()

def unfollow_thread(thread_id: int, user_id: int):
    db.session.execute(text(
        """
        DELETE FROM thread_followers WHERE thread_id = :thread_id AND user_id = :user_id
        """), {
            "thread_id": thread_id,
            "user_id": user_id,
        })
    db.session.commit()

def check_follows_thread(thread_id: int, user_id: int):
    follows = db.session.execute(text(
        """
        SELECT COUNT(*) FROM thread_followers WHERE thread_id = :thread_id AND user_id = :user_id
        """
    ), {
        "thread_id": thread_id,
        "user_id": user_id
    }).first()[0] > 0

    return follows
