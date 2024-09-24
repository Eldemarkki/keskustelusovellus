from db import db
from sqlalchemy.sql import text

def topic_exists(name):
    if db.session.execute(text("SELECT COUNT(*) FROM topics WHERE name = :name"), {
            "name": name
        }).first()[0] > 0:
        return True
    
    return False

def create_topic(name, description):
    topic = db.session.execute(
            text("INSERT INTO topics (name, description) VALUES (:name, :description) RETURNING slug"),
            {"name": name, "description": description}
        ).first()
    
    db.session.commit()

    return topic

def get_topic_by_id(topic_id):
    topic = db.session.execute(text("SELECT * FROM topics WHERE id = :id"), {
        "id": topic_id
    }).first()
    return topic

def get_topic_by_slug(slug):
    topic = db.session.execute(text("SELECT * FROM topics WHERE slug = :slug"), {
        "slug": slug
    }).first()
    return topic

def get_topics(user_id):
    topics = db.session.execute(text(
        """
        SELECT name, slug, COUNT(
                CASE
                    WHEN private = false OR private_thread_participant_rights.user_id = :user_id 
                    THEN threads.id
                END
            )
        FROM topics 
        LEFT JOIN threads ON topics.id = threads.topic_id 
        LEFT JOIN private_thread_participant_rights ON threads.id = private_thread_participant_rights.thread_id
        GROUP BY topics.name, topics.slug;
        """),
        {
            "user_id": user_id
        }).all()

    return topics