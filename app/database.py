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

            # ================= ADVANCED JAVA =================
            ("Advanced Java", "What is JDBC?", "Java Database Connectivity", "Java Data Control", "Java DB Class", "None", "A"),
            ("Advanced Java", "Servlet is used for?", "Frontend", "Backend processing", "Styling", "Design", "B"),
            ("Advanced Java", "Which package is used for JDBC?", "java.sql", "java.io", "java.net", "java.util", "A"),
            ("Advanced Java", "Which method starts a thread?", "run()", "start()", "execute()", "init()", "B"),
            ("Advanced Java", "JSP stands for?", "Java Server Pages", "Java Simple Pages", "Java Service Pages", "None", "A"),
            ("Advanced Java", "Which is session tracking?", "Cookies", "URL rewriting", "Hidden fields", "All", "D"),
            ("Advanced Java", "DriverManager class is in?", "java.sql", "java.io", "java.net", "java.util", "A"),
            ("Advanced Java", "Which protocol used in servlet?", "HTTP", "FTP", "SMTP", "TCP", "A"),
            ("Advanced Java", "doGet() method is used for?", "Insert", "Retrieve", "Delete", "Update", "B"),
            ("Advanced Java", "JDBC full form?", "Java Database Connectivity", "Java Data Control", "Java DB Class", "None", "A"),

            # ================= DATA MINING =================
            ("Data Mining", "Data Mining is used for?", "Data analysis", "Cooking", "Drawing", "Gaming", "A"),
            ("Data Mining", "Clustering is?", "Grouping data", "Sorting", "Deleting", "Printing", "A"),
            ("Data Mining", "Classification is?", "Predicting category", "Sorting", "Grouping", "None", "A"),
            ("Data Mining", "K-means is?", "Clustering algorithm", "Sorting method", "DB tool", "None", "A"),
            ("Data Mining", "Association rule mining finds?", "Relationships", "Sorting", "Deleting", "Printing", "A"),
            ("Data Mining", "Data warehouse stores?", "Large data", "Small data", "Images", "Audio", "A"),
            ("Data Mining", "Apriori algorithm is used for?", "Association", "Sorting", "Clustering", "None", "A"),
            ("Data Mining", "Outlier is?", "Abnormal data", "Normal data", "Sorted data", "None", "A"),
            ("Data Mining", "Data preprocessing includes?", "Cleaning", "Cooking", "Painting", "None", "A"),
            ("Data Mining", "Decision tree is?", "Classification model", "Sorting", "DB", "None", "A"),

            # ================= TOC =================
            ("TOC", "DFA stands for?", "Deterministic Finite Automata", "Data File Access", "Digital Format App", "None", "A"),
            ("TOC", "NFA means?", "Non-deterministic FA", "New File Access", "Network File App", "None", "A"),
            ("TOC", "Regular expression is?", "Pattern", "Data", "File", "None", "A"),
            ("TOC", "Grammar is used for?", "Language", "Sorting", "Database", "None", "A"),
            ("TOC", "Pushdown automata uses?", "Stack", "Queue", "Array", "None", "A"),
            ("TOC", "Turing machine is?", "Powerful model", "Weak model", "DB", "None", "A"),
            ("TOC", "Context free grammar is?", "CFG", "DFG", "AFG", "None", "A"),
            ("TOC", "Language accepted by DFA is?", "Regular", "Context free", "Recursive", "None", "A"),
            ("TOC", "Finite automata has?", "Finite states", "Infinite states", "No states", "None", "A"),
            ("TOC", "Alphabet is?", "Set of symbols", "Numbers", "Words", "None", "A"),

            # ================= AI =================
            ("Artificial Intelligence", "AI full form?", "Artificial Intelligence", "Auto Input", "Advanced Internet", "None", "A"),
            ("Artificial Intelligence", "Machine learning is part of?", "AI", "Web", "DB", "OS", "A"),
            ("Artificial Intelligence", "AI used in?", "Robotics", "Cooking", "Painting", "None", "A"),
            ("Artificial Intelligence", "Supervised learning uses?", "Labeled data", "Unlabeled", "Random", "None", "A"),
            ("Artificial Intelligence", "Neural network is?", "AI model", "DB", "OS", "None", "A"),
            ("Artificial Intelligence", "Deep learning is?", "Advanced ML", "Basic ML", "DB", "None", "A"),
            ("Artificial Intelligence", "AI goal is?", "Smart machines", "Fast typing", "Gaming", "None", "A"),
            ("Artificial Intelligence", "Chatbot uses?", "AI", "HTML", "CSS", "None", "A"),
            ("Artificial Intelligence", "Vision in AI means?", "Image processing", "Sound", "Text", "None", "A"),
            ("Artificial Intelligence", "NLP stands for?", "Natural Language Processing", "Network Language", "None", "None", "A"),

            ("Python", "Python is?", "Programming Language", "Database", "OS", "None", "A"),
            ("Python", "Which keyword defines function?", "def", "fun", "function", "None", "A"),
            ("Python", "List is?", "Mutable", "Immutable", "Static", "None", "A"),
            ("Python", "Tuple is?", "Mutable", "Immutable", "Dynamic", "None", "B"),
            ("Python", "Which loop exists?", "for", "while", "both", "None", "C"),
            ("Python", "Indentation means?", "Spacing", "Error", "Loop", "None", "A"),
            ("Python", "File extension?", ".py", ".java", ".cpp", "None", "A"),
            ("Python", "Which is list?", "[ ]", "{ }", "( )", "None", "A"),
            ("Python", "Dictionary uses?", "{ }", "[ ]", "( )", "None", "A"),
            ("Python", "Print function?", "print()", "echo()", "cout", "None", "A"),

            ("DBMS", "DBMS stands for?", "Database Management System", "Data Backup System", "None", "None", "A"),
            ("DBMS", "Primary key is?", "Unique", "Duplicate", "Null", "None", "A"),
            ("DBMS", "Foreign key is?", "Reference", "Unique", "Primary", "None", "A"),
            ("DBMS", "SQL used for?", "Query", "Game", "OS", "None", "A"),
            ("DBMS", "Table means?", "Rows and Columns", "Only rows", "Only columns", "None", "A"),
            ("DBMS", "Which is DB?", "MySQL", "HTML", "CSS", "None", "A"),
            ("DBMS", "Data redundancy?", "Duplicate data", "Unique", "None", "None", "A"),
            ("DBMS", "Normalization is?", "Reduce redundancy", "Increase data", "Delete data", "None", "A"),
            ("DBMS", "Which is query?", "SELECT", "PRINT", "RUN", "None", "A"),
            ("DBMS", "Which DB is relational?", "MySQL", "Excel", "Word", "None", "A"),

            ("Operating System", "OS stands for?", "Operating System", "Open System", "None", "None", "A"),
            ("Operating System", "OS is?", "System Software", "Application", "Game", "None", "A"),
            ("Operating System", "CPU scheduling is?", "Process control", "Game", "None", "None", "A"),
            ("Operating System", "Process is?", "Program in execution", "File", "Data", "None", "A"),
            ("Operating System", "Deadlock is?", "Blocked state", "Running", "Ready", "None", "A"),
            ("Operating System", "Memory management?", "RAM control", "Disk", "None", "None", "A"),
            ("Operating System", "Which OS?", "Windows", "HTML", "CSS", "None", "A"),
            ("Operating System", "File system?", "Storage", "Network", "None", "None", "A"),
            ("Operating System", "Multitasking?", "Multiple tasks", "Single", "None", "None", "A"),
            ("Operating System", "Kernel is?", "Core of OS", "App", "File", "None", "A"),

            ("Computer Networks", "Network is?", "Connection", "File", "Data", "None", "A"),
            ("Computer Networks", "IP stands for?", "Internet Protocol", "Input Process", "None", "None", "A"),
            ("Computer Networks", "LAN means?", "Local Area Network", "Large Area", "None", "None", "A"),
            ("Computer Networks", "WAN means?", "Wide Area Network", "Wireless", "None", "None", "A"),
            ("Computer Networks", "Router does?", "Routing", "Printing", "None", "None", "A"),
            ("Computer Networks", "Protocol is?", "Rules", "Data", "File", "None", "A"),
            ("Computer Networks", "HTTP is?", "Protocol", "Language", "None", "None", "A"),
            ("Computer Networks", "IP address?", "Unique ID", "File", "None", "None", "A"),
            ("Computer Networks", "Switch is?", "Network device", "App", "None", "None", "A"),
            ("Computer Networks", "Firewall?", "Security", "Game", "None", "None", "A"),

]
    db.executemany("""
        INSERT INTO questions
        (category, question, option_a, option_b, option_c, option_d, correct_option)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, questions)