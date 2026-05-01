import sqlite3
from flask import current_app, g
from werkzeug.security import generate_password_hash

def get_db():
    """Create one database connection per request."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """Close database connection."""
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    """Create database tables and insert default questions."""
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            percentage REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    count = db.execute("SELECT COUNT(*) AS total FROM questions").fetchone()["total"]

    if count == 0:
        seed_questions(db)

    db.commit()

def seed_questions(db):
    """Insert starter questions for all quiz categories."""
    questions = [
        # Programming
        ("Programming", "Which language is mainly used for web page structure?", "CSS", "HTML", "Python", "SQL", "B"),
        ("Programming", "What does CSS stand for?", "Creative Style Sheets", "Cascading Style Sheets", "Computer Style Syntax", "Colorful Style Sheets", "B"),
        ("Programming", "Which symbol is used for comments in Python?", "//", "#", "/* */", "<!-- -->", "B"),
        ("Programming", "Which data structure uses LIFO?", "Queue", "Array", "Stack", "Tree", "C"),
        ("Programming", "Which keyword is used to define a function in Python?", "func", "define", "def", "function", "C"),

        # General Knowledge
        ("General Knowledge", "Which planet is known as the Red Planet?", "Earth", "Mars", "Jupiter", "Venus", "B"),
        ("General Knowledge", "Who wrote the national anthem of India?", "Rabindranath Tagore", "Mahatma Gandhi", "Sarojini Naidu", "Subhash Chandra Bose", "A"),
        ("General Knowledge", "Which is the largest ocean in the world?", "Indian Ocean", "Arctic Ocean", "Pacific Ocean", "Atlantic Ocean", "C"),
        ("General Knowledge", "How many continents are there?", "5", "6", "7", "8", "C"),
        ("General Knowledge", "Which gas do plants absorb?", "Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen", "B"),

        # Aptitude
        ("Aptitude", "If 5x = 20, then x = ?", "2", "3", "4", "5", "C"),
        ("Aptitude", "Average of 10, 20 and 30 is?", "15", "20", "25", "30", "B"),
        ("Aptitude", "What is 25% of 200?", "25", "40", "50", "75", "C"),
        ("Aptitude", "If a train travels 60 km in 1 hour, speed is?", "30 km/h", "60 km/h", "90 km/h", "120 km/h", "B"),
        ("Aptitude", "Next number: 2, 4, 8, 16, ?", "18", "20", "24", "32", "D"),

        # Technology
        ("Technology", "What does AI stand for?", "Automated Internet", "Artificial Intelligence", "Advanced Input", "Auto Interface", "B"),
        ("Technology", "Which company developed Android?", "Apple", "Google", "Microsoft", "IBM", "B"),
        ("Technology", "What does URL stand for?", "Uniform Resource Locator", "Universal Read Link", "User Resource Login", "Unified Routing Line", "A"),
        ("Technology", "Which is an example of cloud storage?", "Google Drive", "Keyboard", "Monitor", "RAM", "A"),
        ("Technology", "What does CPU stand for?", "Central Processing Unit", "Computer Power Unit", "Central Program Utility", "Control Processing User", "A"),
    ]

    db.executemany("""
        INSERT INTO questions
        (category, question, option_a, option_b, option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, questions)
