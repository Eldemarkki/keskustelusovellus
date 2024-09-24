from db import db
from sqlalchemy.sql import text

def get_user_by_id(user_id: int):
    user = db.session.execute(text(
        """
        SELECT username 
        FROM users 
        WHERE id = :id
        """),
        {
            "id": user_id
        }).first()
    
    return user

def get_user_by_username(username: str):
    user = db.session.execute(text(
        """
        SELECT * 
        FROM users 
        WHERE username = :username
        """),
        {
            "username": username
        }).first()
    return user

def user_exists(username: str) -> bool:
    username_exists = db.session.execute(text(
        """
        SELECT COUNT(*) 
        FROM users 
        WHERE username = :username
        """),
        {
            "username": username
        }).first()[0] > 0
    return username_exists

def create_user(username: str, password_hash: str) -> int:
    user_id = db.session.execute(text(
        """
        INSERT INTO users (username, password_hash) 
        VALUES (:username, :password_hash) 
        RETURNING id
        """),
        {
            "username": username, 
            "password_hash": password_hash
        }).first()[0]

    db.session.commit()

    return user_id

