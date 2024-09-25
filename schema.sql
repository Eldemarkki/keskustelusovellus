CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE topics (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    slug TEXT GENERATED ALWAYS AS (replace(lower(name), ' ', '-')) STORED,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE threads (
    id SERIAL PRIMARY KEY,
    topic_id INT NOT NULL REFERENCES topics(id),
    title TEXT NOT NULL,
    private BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    thread_id INT NOT NULL REFERENCES threads(id),
    message TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE private_thread_participant_rights (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    thread_id INT NOT NULL REFERENCES threads(id)
);

CREATE TABLE thread_followers (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL REFERENCES users(id),
    thread_id INT NOT NULL REFERENCES threads(id),
    read_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE (user_id, thread_id)
);
