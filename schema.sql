-- CS348 Media Tracker - Database Schema

DROP TABLE IF EXISTS Tags;
DROP TABLE IF EXISTS UserMediaLog;
DROP TABLE IF EXISTS MediaItems;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT    NOT NULL UNIQUE,
    email     TEXT    NOT NULL UNIQUE
);

CREATE TABLE MediaItems (
    item_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT    NOT NULL,
    type         TEXT    NOT NULL CHECK(type IN ('Movie','Book','Game','TV Show')),
    genre        TEXT    NOT NULL,
    release_year INTEGER NOT NULL,
    description  TEXT
);

CREATE TABLE UserMediaLog (
    log_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    item_id    INTEGER NOT NULL REFERENCES MediaItems(item_id) ON DELETE CASCADE,
    status     TEXT    NOT NULL CHECK(status IN ('Want','Watching','Completed','Dropped')),
    rating     REAL    CHECK(rating >= 1 AND rating <= 10),
    date_added TEXT    NOT NULL DEFAULT (DATE('now')),
    review     TEXT,
    UNIQUE(user_id, item_id)
);

CREATE TABLE Tags (
    tag_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    log_id   INTEGER NOT NULL REFERENCES UserMediaLog(log_id) ON DELETE CASCADE,
    tag_name TEXT    NOT NULL
);

-- Seed Users
INSERT INTO Users (username, email) VALUES
    ('alice',   'alice@example.com'),
    ('bob',     'bob@example.com'),
    ('charlie', 'charlie@example.com');

-- Seed MediaItems
INSERT INTO MediaItems (title, type, genre, release_year, description) VALUES
    ('The Dark Knight',      'Movie',   'Action',   2008, 'Batman faces the Joker in Gotham City.'),
    ('Inception',            'Movie',   'Sci-Fi',   2010, 'A thief enters dreams to plant an idea.'),
    ('Breaking Bad',         'TV Show', 'Drama',    2008, 'A chemistry teacher turns to making drugs.'),
    ('The Witcher 3',        'Game',    'RPG',      2015, 'Open-world RPG with rich storytelling.'),
    ('Dune',                 'Book',    'Sci-Fi',   1965, 'Epic sci-fi set on the desert planet Arrakis.'),
    ('Interstellar',         'Movie',   'Sci-Fi',   2014, 'Astronauts search for a new home for humanity.'),
    ('Elden Ring',           'Game',    'RPG',      2022, 'Open world action RPG by FromSoftware.'),
    ('Attack on Titan',      'TV Show', 'Action',   2013, 'Humanity fights giant humanoid Titans.'),
    ('The Name of the Wind', 'Book',    'Fantasy',  2007, 'The tale of the legendary wizard Kvothe.'),
    ('Oppenheimer',          'Movie',   'Drama',    2023, 'The story of the atomic bomb creator.'),
    ('Cyberpunk 2077',       'Game',    'Action',   2020, 'Open world RPG set in Night City.'),
    ('1984',                 'Book',    'Dystopia', 1949, 'George Orwell dystopian novel.'),
    ('Stranger Things',      'TV Show', 'Sci-Fi',   2016, 'Kids uncover supernatural mysteries.'),
    ('The Last of Us',       'Game',    'Action',   2013, 'Survivor escort in post-apocalyptic USA.'),
    ('Project Hail Mary',    'Book',    'Sci-Fi',   2021, 'An astronaut must save Earth alone.');

-- Seed UserMediaLog
INSERT INTO UserMediaLog (user_id, item_id, status, rating, review) VALUES
    (1, 1,  'Completed', 9.5, 'One of the greatest films ever made.'),
    (1, 2,  'Completed', 8.5, 'Mind-bending and visually stunning.'),
    (1, 5,  'Completed', 10,  'A masterpiece of science fiction.'),
    (1, 7,  'Watching',  9.0, 'Incredible open world experience.'),
    (2, 3,  'Completed', 9.8, 'Best TV show ever created.'),
    (2, 4,  'Completed', 9.2, 'Spent 200 hours and loved every minute.'),
    (2, 6,  'Want',      NULL, NULL),
    (2, 10, 'Completed', 9.0, 'Stunning practical effects.'),
    (3, 8,  'Completed', 9.5, 'Emotional rollercoaster.'),
    (3, 9,  'Watching',  8.0, 'Beautifully written prose.'),
    (3, 12, 'Completed', 9.7, 'Terrifyingly relevant today.'),
    (3, 15, 'Completed', 9.9, 'Best sci-fi book in years.');

-- Seed Tags
INSERT INTO Tags (log_id, tag_name) VALUES
    (1, 'classic'), (1, 'superhero'),
    (2, 'mindbender'), (2, 'must-watch'),
    (3, 'binge-worthy'), (3, 'classic'),
    (5, 'greatest-ever'), (5, 'binge-worthy'),
    (10, 'literary'),
    (12, 'important'), (12, 'classic');


-- INDEXES (Stage 3)

-- Speeds up the report when filtering by genre
CREATE INDEX IF NOT EXISTS idx_mediaitems_genre ON MediaItems(genre);

-- Speeds up the report when filtering by type
CREATE INDEX IF NOT EXISTS idx_mediaitems_type ON MediaItems(type);

-- Speeds up the report when filtering by year range
CREATE INDEX IF NOT EXISTS idx_mediaitems_year ON MediaItems(release_year);

-- Speeds up log lookups when joining MediaItems to UserMediaLog in the report
CREATE INDEX IF NOT EXISTS idx_log_item_id ON UserMediaLog(item_id);

-- Speeds up the report when filtering by status
CREATE INDEX IF NOT EXISTS idx_log_status ON UserMediaLog(status);
