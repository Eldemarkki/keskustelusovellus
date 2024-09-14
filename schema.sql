CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT GENERATED ALWAYS AS (replace(lower(name), ' ', '-')) STORED,
    description TEXT
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    private BOOLEAN NOT NULL
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    message_id TEXT NOT NULL
);

CREATE TABLE private_thread_participant_rights (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    thread_id INT NOT NULL REFERENCES threads(id)
);

CREATE TABLE thread_followers (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    thread_id INT NOT NULL REFERENCES threads(id)
);
