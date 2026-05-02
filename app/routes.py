import re
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .database import get_db

main = Blueprint("main", __name__)

def login_required(view):
    """Protect pages that require login."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped_view

@main.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("main.login"))

@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("main.register"))

        # 🔒 Strong password validation
        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("main.register"))

        if not re.search(r"\d", password):
            flash("Password must contain at least 1 number.", "error")
            return redirect(url_for("main.register"))

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            flash("Password must contain at least 1 special character.", "error")
            return redirect(url_for("main.register"))

        db = get_db()
        existing = db.execute(
            "SELECT id FROM users WHERE username = ? OR email = ?",
            (username, email)
        ).fetchone()

        if existing:
            flash("Username or email already exists.", "error")
            return redirect(url_for("main.register"))

        db.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password))
        )
        db.commit()

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username_or_email or not password:
            flash("Username/email and password are required.", "error")
            return redirect(url_for("main.login"))

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username_or_email, username_or_email.lower())
        ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash("Login successful.", "success")
            return redirect(url_for("main.dashboard"))

        flash("Invalid login details.", "error")
        return redirect(url_for("main.login"))

    return render_template("login.html")

@main.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        new_password = request.form.get("new_password", "")

        if not email or not new_password:
            flash("Email and new password are required.", "error")
            return redirect(url_for("main.forgot_password"))

        if len(new_password) < 6:
            flash("New password must be at least 6 characters.", "error")
            return redirect(url_for("main.forgot_password"))

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if not user:
            flash("No account found with this email.", "error")
            return redirect(url_for("main.forgot_password"))

        db.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (generate_password_hash(new_password), email)
        )
        db.commit()

        flash("Password reset successful. Please login.", "success")
        return redirect(url_for("main.login"))

    return render_template("forgot_password.html")

@main.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("main.login"))

@main.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    history = db.execute(
        "SELECT * FROM scores WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (session["user_id"],)
    ).fetchall()
    categories = ["Advanced Java", "Data Mining", "TOC", "Artificial Intelligence"]
    return render_template("dashboard.html", categories=categories, history=history)

@main.route("/quiz/<category>")
@login_required
def quiz(category):
    allowed = ["Advanced Java", "Data Mining", "TOC", "Artificial Intelligence"]
    if category not in allowed:
        flash("Invalid quiz category.", "error")
        return redirect(url_for("main.dashboard"))
    return render_template("quiz.html", category=category)

@main.route("/api/questions/<category>")
@login_required
def api_questions(category):
    db = get_db()

    # 🔥 category wise session key
    session_key = f"quiz_{category}"

    # agar already stored hai → wahi return karo
    if session_key in session:
        return jsonify(session[session_key])

    # warna new random questions lo
    rows = db.execute(
        """
        SELECT id, question, option_a, option_b, option_c, option_d 
        FROM questions 
        WHERE category = ?
        ORDER BY RANDOM()
        LIMIT 10
        """,
        (category,)
    ).fetchall()

    questions = []
    for row in rows:
        questions.append({
            "id": row["id"],
            "question": row["question"],
            "options": {
                "A": row["option_a"],
                "B": row["option_b"],
                "C": row["option_c"],
                "D": row["option_d"],
            }
        })

    # 🔥 category wise save
    session[session_key] = questions

    return jsonify(questions)


@main.route("/submit-quiz", methods=["POST"])
@login_required
def submit_quiz():
    data = request.get_json()
    category = data.get("category")
    answers = data.get("answers", {})

    db = get_db()
    rows = db.execute(
        "SELECT * FROM questions WHERE category = ?",
        (category,)
    ).fetchall()

    score = 0
    review = []

    for row in rows:
        qid = str(row["id"])
        user_answer = answers.get(qid, "")
        correct = row["correct_option"]

        if user_answer == correct:
            score += 1

        review.append({
            "question": row["question"],
            "your_answer": user_answer if user_answer else "Not Answered",
            "correct_answer": correct,
            "correct_text": row[f"option_{correct.lower()}"],
            "is_correct": user_answer == correct
        })

    total = len(rows)
    percentage = round((score / total) * 100, 2) if total else 0

    db.execute(
        "INSERT INTO scores (user_id, category, score, total, percentage) VALUES (?, ?, ?, ?, ?)",
        (session["user_id"], category, score, total, percentage)
    )
    db.commit()

    session.pop(f"quiz_{category}", None)

    session["last_result"] = {
        "category": category,
        "score": score,
        "total": total,
        "percentage": percentage,
        "status": "PASS" if percentage >= 50 else "FAIL",
        "review": review
    }

    return jsonify({"redirect": url_for("main.result")})

@main.route("/result")
@login_required
def result():
    result_data = session.get("last_result")
    if not result_data:
        return redirect(url_for("main.dashboard"))
    return render_template("result.html", result=result_data)

@main.route("/leaderboard")
@login_required
def leaderboard():
    db = get_db()

    users = db.execute("""
        SELECT users.username, scores.score
        FROM scores
        JOIN users ON users.id = scores.user_id
        ORDER BY scores.score DESC
        LIMIT 10
    """).fetchall()

    return render_template("leaderboard.html", users=users)

@main.route("/profile")
@login_required
def profile():
    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    stats = db.execute("""
        SELECT 
            COUNT(*) as total_quiz,
            AVG(score) as avg_score
        FROM scores
        WHERE user_id = ?
    """, (session["user_id"],)).fetchone()


    return render_template("profile.html", user=user, stats=stats)