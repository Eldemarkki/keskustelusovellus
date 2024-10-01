import re
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from flask import abort, redirect, render_template, request, session
from app import app
from messages import create_message, get_thread_messages
from private_thread_participant_rights import add_access_to_private_thread, get_private_thread_participants, has_access_to_private_thread, remove_access_to_private_thread
from thread_followers import check_follows_thread, follow_thread, unfollow_thread
from threads import create_thread, get_thread_by_id, get_thread_owner_id, get_topic_threads, get_followed_thread_activity, update_read_time
from topics import create_topic, get_topic_by_id, get_topic_by_slug, get_topics, topic_exists
from users import create_user, get_user_by_id, get_user_by_username, user_exists

hasher = PasswordHasher()

@app.route("/")
def index_page():
    user_id = session.get("id")
    if user_id is not None:
        user = get_user_by_id(user_id)
        if user is not None:
            username = user[0]
            active_threads = get_followed_thread_activity(user_id)
            return render_template("index.html", username=username, active_threads=active_threads)
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
        errors.append("Käyttäjänimessä täytyy olla ainoastaan alfanumeerisia merkkejä (a-z, A-Z, 0-9) ja olla 1-32 merkkiä pitkä.")
    if len(password) < 16 or len(password) > 64:
        errors.append("Salasanan täytyy olla 16-64 merkkiä pitkä.")
    username_exists = user_exists(username)
    if username_exists:
        errors.append("Käyttäjänimi on varattu.")

    if len(errors) > 0:
        return render_template("register.html", errors=errors)
    else:
        password_hash = hasher.hash(password)
        user_id = create_user(username, password_hash)
        session["id"] = user_id
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
        errors.append("Salasana ei voi olla pidempi kuin 64 merkkiä.")

    if len(errors) > 0:
        return render_template("login.html", errors=errors)

    user = get_user_by_username(username)

    try:
        if user is not None:
            hasher.verify(user.password_hash, password)
            session["id"] = user.id
            return redirect("/")
        else:
            # Try to verify some garbage to prevent timing attacks.
            password_hash = "$argon2id$v=19$m=65536,t=3,p=4$nQiaw9HH5UxmV44rZk7yMA$0wBr3cHpcfSqyZMQvYCsNv4ywkMxbgIUpS4+TtFmWQ4" # testing1234567890
            hasher.verify(password_hash, "incorrect")
    except VerificationError:
        return render_template("login.html", errors=["Virheellinen käyttäjänimi tai salasana"])

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
            errors.append("Aiheen nimessä tulee olla ainoastaan alfanumeerisia merkkejä (a-z, A-Z, 0-9) eikä siinä saa olla peräkkäisiä välilyöntejä.")
        
        if len(name) <= 0 or len(name) > 100:
            errors.append("Aiheen nimeen tulee olla 1-100 merkkiä pitkä.")

        description = request.form.get("description", None)
        if len(description) > 500:
            errors.append("Kuvaus saa olla enintään 500 merkkiä pitkä.")

        if topic_exists(name):
            errors.append("Tämänniminen aihe on jo olemassa.")

        if len(errors) > 0:
            return render_template("/new_topic.html", errors=errors)

        topic = create_topic(name, description)

        return redirect("/topics/" + topic[0])

    return redirect("/login")

@app.route("/topics/<topic_slug>")
def topic_page(topic_slug):
    user_id = session.get("id")

    if topic_slug is not None:
        topic = get_topic_by_slug(topic_slug)
        threads = get_topic_threads(topic.id, user_id)

        if topic is not None:
            return render_template("topic.html", topic=topic, threads=threads)
    
    abort(404)

@app.route("/topics/<topic_slug>/new-thread")
def new_thread_page(topic_slug):
    if "id" in session:
        topic = get_topic_by_slug(topic_slug)

        if topic is None:
            abort(404)
            return

        return render_template("/new_thread.html", topic=topic)
    return redirect("/login")

@app.post("/topics/<topic_slug>/new-thread")
def new_thread_post(topic_slug):
    if "id" in session:
        user_id = session.get("id")
        title = request.form.get("title", "")
        private = request.form.get("private", False, type=bool)
        message = request.form.get("message", "")
        topic = get_topic_by_slug(topic_slug)

        if topic is None:
            abort(404)
            return

        thread_id = create_thread(title, private, topic.id)

        create_message(user_id, thread_id, message)

        add_access_to_private_thread(thread_id, user_id)

        return redirect("/threads/" + str(thread_id))
    return redirect("/login")

@app.route("/topics")
def topics_route():
    user_id = session.get("id")
    
    topics = get_topics(user_id)

    return render_template("topics.html", topics=topics)

def render_thread_page(thread_id, error=None, is_participants_open=False):
    thread = get_thread_by_id(thread_id)

    if thread is None:
        abort(404)
        return
    
    user_id = session.get("id")
    if thread.private and not has_access_to_private_thread(thread_id, user_id):
        abort(404)
        return

    topic = get_topic_by_id(thread.topic_id)

    messages = get_thread_messages(thread.id)
    thread_owner = get_thread_owner_id(thread.id)
    show_participant_list = thread_owner == user_id
    private_thread_participants = get_private_thread_participants(thread.id, user_id)

    follows_thread = check_follows_thread(thread.id, user_id)

    update_read_time(thread.id, user_id)

    return render_template(
        "thread.html", 
        thread=thread,
        messages=messages,
        topic=topic,
        private_participants=private_thread_participants,
        is_participants_open=is_participants_open,
        show_participant_list=show_participant_list,
        error=error,
        follows_thread=follows_thread
    )

@app.route("/threads/<thread_id>")
def thread_route(thread_id):
    return render_thread_page(thread_id)

@app.post("/threads/<thread_id>")
def thread_post(thread_id):
    user_id = session.get("id")
    if user_id is None:
        return redirect("/login")
    
    thread = get_thread_by_id(thread_id)

    if thread is None:
        abort(404)
        return
    
    if thread.private and not has_access_to_private_thread(thread_id, user_id):
        abort(404)
        return

    message = request.form.get("message", "")

    create_message(user_id, thread_id, message)
    update_read_time(thread_id, user_id)

    return redirect("/threads/" + str(thread_id))

@app.post("/threads/<thread_id>/add-participant")
def add_participant_post(thread_id):
    user_id = session.get("id")
    if user_id is None:
        return redirect("/login")
    
    thread = get_thread_by_id(thread_id)
    if thread is None:
        print("thread not found")
        abort(404)
        return

    if not thread.private:
        abort(403)
        return
    
    thread_owner = get_thread_owner_id(thread_id)

    if thread_owner != user_id:
        return redirect("/login")

    username = request.form.get("participant-username")

    new_participant = get_user_by_username(username)

    if new_participant is None:
        return render_thread_page(thread_id=thread_id, error="Käyttäjää ei löytynyt", is_participants_open=True)
    
    add_access_to_private_thread(thread_id, new_participant.id)

    return render_thread_page(thread_id=thread_id, is_participants_open=True)

@app.post("/threads/<thread_id>/remove-participant")
def remove_participant_post(thread_id):
    user_id = session.get("id")
    if user_id is None:
        return redirect("/login")

    thread = get_thread_by_id(thread_id)
    if thread is None:
        print("thread not found")
        abort(404)
        return

    if not thread.private:
        abort(403)
        return
    
    thread_owner = get_thread_owner_id(thread_id)

    if thread_owner != user_id:
        return redirect("/login")

    participant_id = request.form.get("participant-id", type=int)
    
    remove_access_to_private_thread(thread_id, participant_id)

    return render_thread_page(thread_id=thread_id, is_participants_open=True)

@app.post("/threads/<thread_id>/follow")
def follow_thread_post(thread_id):
    user_id = session.get("id")
    if user_id is None:
        return redirect("/login")

    thread = get_thread_by_id(thread_id)
    if thread is None:
        print("thread not found")
        abort(404)
        return
    
    user_id = session.get("id")
    if thread.private and not has_access_to_private_thread(thread.id, user_id):
        abort(404)
        return

    if not check_follows_thread(thread.id, user_id):
        follow_thread(thread.id, user_id)

    return redirect("/threads/" + str(thread.id))

@app.post("/threads/<thread_id>/unfollow")
def unfollow_thread_post(thread_id):
    user_id = session.get("id")
    if user_id is None:
        return redirect("/login")

    thread = get_thread_by_id(thread_id)
    if thread is None:
        print("thread not found")
        abort(404)
        return
    
    user_id = session.get("id")
    if thread.private and not has_access_to_private_thread(thread.id, user_id):
        abort(404)
        return

    if check_follows_thread(thread.id, user_id):
        unfollow_thread(thread.id, user_id)

    return redirect("/threads/" + str(thread.id))

@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404