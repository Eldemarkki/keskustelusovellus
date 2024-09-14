import re
from flask import Flask, abort, redirect, render_template, request, session
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
hasher = PasswordHasher()
db = SQLAlchemy(app)

@app.route("/")
def index_page():
    id = session.get("id", None)
    if id != None:
        user = db.session.execute(text("SELECT username FROM users WHERE id = :id"), {"id": id}).first()
        if user != None:
            username = user[0]
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

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.post('/login')
def login_post():
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    errors = []
    if len(password) > 64:
        errors.append("Password must not be longer than 64 characters long.")

    if len(errors) > 0:
        return render_template("login.html", errors=errors)

    user = db.session.execute(text("SELECT id, password_hash FROM users WHERE username = :username"), {"username": username}).first()

    try:
        if user != None:
            password_hash = user[1]
            hasher.verify(password_hash, password)
            session["id"] = user[0]
            return redirect("/")  
        else:
            # Try to verify some garbage to prevent timing attacks.
            password_hash = "$argon2id$v=19$m=65536,t=3,p=4$nQiaw9HH5UxmV44rZk7yMA$0wBr3cHpcfSqyZMQvYCsNv4ywkMxbgIUpS4+TtFmWQ4" # testing1234567890
            hasher.verify(password_hash, "incorrect")
    except VerificationError:
        return render_template("login.html", errors=["Invalid username or password"])

@app.post("/logout")
def logout_post():
    del session["id"]
    return redirect("/")

@app.route("/new-topic")
def new_topic_route():
    if "id" in session:
        return render_template("/new_topic.html")
    return redirect("/login")

@app.post("/new-topic")
def new_topic_post():
    if "id" in session:
        errors = []

        name = request.form.get("name", "")
        if not re.match("^[a-zA-Z0-9]+(?: [a-zA-Z0-9]+)*$", name):
            errors.append("Topic name must only have alphanumeric characters (a-z, A-Z, 0-9) and no consecutive spaces.")
        
        if len(name) <= 0 or len(name) > 100:
            errors.append("Topic name must be 1-100 characters long.")

        description = request.form.get("description", None)
        if len(description) > 500:
            errors.append("Description must not be longer than 500 characters")

        if db.session.execute(text("SELECT COUNT(*) FROM topics WHERE name = :name"), {
            "name": name
        }).first()[0] > 0:
            errors.append("A topic with this name already exists")

        if len(errors) > 0:
            return render_template("/new_topic.html", errors=errors)

        db.session.execute(
            text("INSERT INTO topics (name, description) VALUES (:name, :description)"),
            {"name": name, "description": description}
        )
        db.session.commit()

        return redirect("/topics/" + name)

    return redirect("/login")

@app.route("/topics/<topic_slug>")
def topic_page(topic_slug):
    if topic_slug != None:
        topic = db.session.execute(text("SELECT * FROM topics WHERE slug = :slug"), {
            "slug": topic_slug
        }).first()

        if topic != None:
            return render_template("topic.html", topic=topic)
    
    abort(404)

@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404