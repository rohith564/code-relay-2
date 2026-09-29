import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret")

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "code_relay"),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def team_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "team_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return redirect(url_for("participant") if session.get("team_id") else url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        code = request.form.get("login_code", "").strip().upper()
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM teams WHERE login_code=%s AND active=1", (code,))
        team = cur.fetchone()
        cur.close(); db.close()
        if not team:
            flash("Invalid team code.", "error")
            return render_template("login.html")
        session.clear()
        session.update(team_id=team["id"], team_name=team["team_name"],
                       member1=team["member1"], member2=team["member2"])
        return redirect(url_for("participant"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/rules")
@team_required
def rules():
    return render_template("rules.html")

@app.route("/participant")
@team_required
def participant():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM event_control WHERE id=1")
    event = cur.fetchone()
    cur.execute("""SELECT * FROM questions WHERE round_no=%s AND active=1
                   ORDER BY id LIMIT 1""", (event["round_no"],))
    question = cur.fetchone()
    cur.close(); db.close()
    return render_template("participant.html", event=event, question=question)

@app.route("/coding")
@team_required
def coding():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM event_control WHERE id=1")
    event = cur.fetchone()
    cur.execute("""SELECT * FROM questions WHERE round_no=%s AND active=1
                   ORDER BY id LIMIT 1""", (event["round_no"],))
    question = cur.fetchone()
    cur.close(); db.close()
    if not question:
        flash("No question is available for this round.", "error")
        return redirect(url_for("participant"))
    return render_template("coding.html", event=event, question=question)

@app.route("/submit", methods=["POST"])
@team_required
def submit():
    question_id = request.form["question_id"]
    member = request.form["member"]
    code = request.form.get("code", "").strip()
    try:
        elapsed = max(0, int(request.form.get("elapsed_seconds", 0)))
    except ValueError:
        elapsed = 0

    if member not in (session["member1"], session["member2"]):
        flash("Invalid member.", "error")
        return redirect(url_for("coding"))
    if not code:
        flash("Paste your final code before submitting.", "error")
        return redirect(url_for("coding"))

    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM event_control WHERE id=1")
    event = cur.fetchone()
    if event["status"] != "running":
        cur.close(); db.close()
        flash("Submissions are currently closed.", "error")
        return redirect(url_for("participant"))

    cur.execute("""SELECT id FROM submissions
                   WHERE team_id=%s AND question_id=%s LIMIT 1""",
                (session["team_id"], question_id))
    if cur.fetchone():
        cur.close(); db.close()
        flash("Your team already submitted this question.", "error")
        return redirect(url_for("participant"))

    cur.execute("""INSERT INTO submissions
                   (team_id, question_id, member, code, elapsed_seconds)
                   VALUES (%s,%s,%s,%s,%s)""",
                (session["team_id"], question_id, member, code, elapsed))
    db.commit()
    cur.close(); db.close()
    return redirect(url_for("submitted"))

@app.route("/submitted")
@team_required
def submitted():
    return render_template("submitted.html")

@app.route("/leaderboard")
def leaderboard():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("""SELECT t.team_name,t.member1,t.member2,s.member,
                          s.elapsed_seconds,s.submitted_at
                   FROM submissions s JOIN teams t ON t.id=s.team_id
                   ORDER BY s.elapsed_seconds ASC,s.submitted_at ASC""")
    results = cur.fetchall()
    cur.close(); db.close()
    return render_template("leaderboard.html", results=results)

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (request.form["username"] == os.getenv("ADMIN_USERNAME", "admin")
            and request.form["password"] == os.getenv("ADMIN_PASSWORD", "admin123")):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM event_control WHERE id=1")
    event = cur.fetchone()
    cur.execute("SELECT COUNT(*) AS n FROM teams WHERE active=1")
    teams = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM submissions")
    submissions = cur.fetchone()["n"]
    cur.execute("""SELECT t.team_name,t.member1,t.member2,s.member,
                          s.elapsed_seconds,s.submitted_at
                   FROM submissions s JOIN teams t ON t.id=s.team_id
                   ORDER BY s.elapsed_seconds ASC,s.submitted_at ASC""")
    rows = cur.fetchall()
    cur.close(); db.close()
    return render_template("admin/dashboard.html", event=event,
                           teams=teams, submissions_count=submissions, rows=rows)

@app.route("/admin/event", methods=["POST"])
@admin_required
def admin_event():
    action = request.form["action"]
    db = get_db()
    cur = db.cursor()
    if action == "round1":
        cur.execute("""UPDATE event_control SET round_no=1,phase='discussion',
                       status='running',phase_started_at=UTC_TIMESTAMP() WHERE id=1""")
    elif action == "round2":
        cur.execute("""UPDATE event_control SET round_no=2,phase='discussion',
                       status='running',phase_started_at=UTC_TIMESTAMP() WHERE id=1""")
    elif action == "finish":
        cur.execute("UPDATE event_control SET status='finished',phase='finished' WHERE id=1")
    elif action == "reset":
        cur.execute("DELETE FROM submissions")
        cur.execute("""UPDATE event_control SET round_no=1,phase='waiting',
                       status='waiting',phase_started_at=NULL WHERE id=1""")
    db.commit()
    cur.close(); db.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/questions", methods=["GET", "POST"])
@admin_required
def admin_questions():
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == "POST":
        cur.execute("""INSERT INTO questions(round_no,title,description)
                       VALUES(%s,%s,%s)""",
                    (request.form["round_no"], request.form["title"].strip(),
                     request.form["description"].strip()))
        db.commit()
    cur.execute("SELECT * FROM questions ORDER BY round_no,id")
    questions = cur.fetchall()
    cur.close(); db.close()
    return render_template("admin/questions.html", questions=questions)

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(debug=True)
