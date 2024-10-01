from sqlalchemy.sql import text
from db import db


def has_access_to_private_thread(thread_id: int, user_id: int) -> bool:
    access = db.session.execute(text(
        """
        SELECT * 
        FROM private_thread_participant_rights 
        WHERE thread_id = :thread_id AND user_id = :user_id
        """), {
        "thread_id": thread_id,
        "user_id": user_id
    }).first()

    return access is not None


def add_access_to_private_thread(thread_id: int, user_id: int):
    db.session.execute(text(
        """
        INSERT INTO private_thread_participant_rights (user_id, thread_id) 
        VALUES (:user_id, :thread_id)
        """), {
        "user_id": user_id,
        "thread_id": thread_id
    })

    db.session.commit()


def remove_access_to_private_thread(thread_id: int, user_id: int):
    db.session.execute(text(
        """
        DELETE FROM private_thread_participant_rights 
        WHERE user_id = :user_id AND thread_id = :thread_id
        """), {
        "user_id": user_id,
        "thread_id": thread_id
    })

    db.session.commit()


def get_private_thread_participants(thread_id: int, user_id: int):
    private_thread_participants = db.session.execute(text(
        """
            SELECT user_id, username 
            FROM private_thread_participant_rights 
            LEFT JOIN users ON private_thread_participant_rights.user_id = users.id
            WHERE thread_id = :thread_id AND user_id != :owner_user_id
        """), {
        "thread_id": thread_id,
        "owner_user_id": user_id
    })

    return private_thread_participants
