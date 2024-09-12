import re
from flask import Flask, redirect, render_template, request, session
from argon2 import PasswordHasher
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:secretpassword@localhost:5432/postgres"
hasher = PasswordHasher()
db = SQLAlchemy(app)

@app.route("/")
def index_page():
    id = session.get("id", None)
    if id != None:
        username = db.session.execute(text("SELECT username FROM users WHERE id = :id"), {"id": id}).first()[0]
        
        return render_template("index.html", username=username)

    return render_template("index.html")


@app.route("/register")
def register_page():
    return render_template("register.html")

@app.post('/register')
def register_post():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    errors = []
    if not re.match("^[a-zA-Z0-9]{1,32}$", username):
        errors.append("Username must only have alphanumeric characters (a-z, A-Z, 0-9) and be 1-32 characters long")
    if len(password) < 16 or len(password) > 64:
        errors.append("Password must be 16-64 characters long.")
    username_exists = db.session.execute(text("SELECT COUNT(*) FROM users WHERE username = :username"), {"username": username}).first()[0] > 0
    if username_exists:
        errors.append("Username is taken")

    if len(errors) > 0:
        return render_template("register.html", errors=errors)
    else:
        password_hash = hasher.hash(password)

        sql = text("INSERT INTO users (username, password_hash) VALUES (:username, :password_hash)")
        db.session.execute(sql, {
            "username": username, 
            "password_hash": password_hash
        })
        db.session.commit()

        id = db.session.execute(text("SELECT id FROM users WHERE username = :username"), {"username": username}).first()[0]

        session["id"] = id

        return redirect("/")  
