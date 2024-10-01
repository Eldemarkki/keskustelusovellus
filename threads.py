from db import db
from sqlalchemy.sql import text

def create_thread(title: str, private: bool, topic_id: int) -> int:
    thread_id = db.session.execute(text(
        """
        INSERT INTO threads (title, private, topic_id)
        VALUES (:title, :private, :topic_id)
        RETURNING id
        """), {
        "title": title,
        "private": private,
        "topic_id": topic_id
    }).first()[0]
    
    return thread_id

def get_thread_by_id(thread_id: int):
    thread = db.session.execute(text("SELECT * FROM threads WHERE id = :thread_id"), {
        "thread_id": thread_id
    }).first()

    return thread

def get_topic_threads(topic_id: int, user_id: int):
    threads = db.session.execute(text(
        """
        SELECT 
            threads.id, 
            threads.private,
            title, 
            COUNT(messages.id) 
        FROM 
            threads 
        LEFT JOIN messages ON threads.id = messages.thread_id 
        LEFT JOIN private_thread_participant_rights ON threads.id = private_thread_participant_rights.thread_id
        WHERE 
            topic_id = :topic_id AND
                (
                    private = false OR 
                    private_thread_participant_rights.user_id = :user_id
                )
        GROUP BY 
            threads.id
        ORDER BY 
            threads.created_at DESC;
        """), {
        "topic_id": topic_id,
        "user_id": user_id
    }).all()
    
    return threads

def get_thread_owner_id(thread_id: int) -> int:
    # Thread owner is whoever sent the first message to this thread
    thread_owner = db.session.execute(text("SELECT user_id FROM messages WHERE thread_id = :thread_id ORDER BY created_at DESC LIMIT 1"), {
        "thread_id": thread_id
    }).first()[0]

    return thread_owner

def get_followed_thread_activity(user_id: int):
    result = db.session.execute(text(
        """
        SELECT threads.id, threads.title, COUNT(messages.id) 
        FROM threads 
        LEFT JOIN thread_followers ON threads.id = thread_followers.thread_id 
        LEFT JOIN messages ON threads.id = messages.thread_id 
        WHERE 
            messages.created_at > thread_followers.read_time AND 
            thread_followers.user_id = :user_id
        GROUP BY threads.id;
        """
    ), {
        "user_id": user_id
    }).all()

    return result

def update_read_time(thread_id: int, user_id: int):
    db.session.execute(text(
        """
        UPDATE thread_followers SET read_time = NOW() WHERE thread_id = :thread_id AND user_id = :user_id
        """), {
            "thread_id": thread_id,
            "user_id": user_id
        })

    db.session.commit()