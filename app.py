import re
from flask import Flask, redirect, render_template, request

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

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
    if False: # TODO: Check that username is not taken
        errors.append("Username is taken")

    if len(errors) > 0:
        return render_template("register.html", errors=errors)
    else:
        # TODO: Set cookie
        return redirect("/")