from textblob import TextBlob
from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- HOME ----------------
@app.route("/")
def home():
    return "Mental Health Mood Journal is running 💙"


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("mood_journal.db")
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "⚠️ Email already registered. Try logging in."

        conn.close()
        return redirect("/login")

    return render_template("register.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect("mood_journal.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/dashboard")
        else:
            return "❌ Invalid email or password"

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT mood FROM mood_entries WHERE user_id=? ORDER BY date DESC LIMIT 5",
        (session["user_id"],)
    )

    moods = [row[0] for row in cursor.fetchall()]
    conn.close()

    suggestion = ""

    if moods:
        avg_mood = sum(moods) / len(moods)

        if avg_mood <= 2:
            suggestion = "😢 You've been feeling low. Try a walk or talk to a friend."
        elif avg_mood == 3:
            suggestion = "😐 You're doing okay. Maybe take a short break and relax."
        else:
            suggestion = "😊 Great! Keep up your positive energy!"

    return render_template("dashboard.html", suggestion=suggestion)


# ---------------- ADD MOOD ----------------
@app.route("/add-mood", methods=["GET", "POST"])
def add_mood():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        mood = request.form.get("mood")
        note = request.form.get("note")
        today = date.today().isoformat()
        
        
     # SENTIMENT ANALYSIS
    sentiment = TextBlob(note).sentiment.polarity

    if sentiment > 0:
        detected_mood = "Positive 😊"
    elif sentiment < 0:
        detected_mood = "Negative 😢"
    else:
        detected_mood = "Neutral 😐"   
    


        conn = sqlite3.connect("mood_journal.db")
        cursor = conn.cursor()

        cursor.execute(
    "INSERT INTO mood_entries (user_id, mood, note, sentiment, date) VALUES (?, ?, ?, ?, ?)",
    (session["user_id"], mood, note, detected_mood, today)
)
        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_mood.html")


# ---------------- HISTORY ----------------
@app.route("/history")
def history():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM mood_entries WHERE user_id=? ORDER BY date DESC",
        (session["user_id"],)
    )

    moods = cursor.fetchall()
    conn.close()

    return render_template("history.html", moods=moods)


# ---------------- CHART ----------------
@app.route("/chart")
def chart():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("mood_journal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT date, mood FROM mood_entries WHERE user_id=? ORDER BY date",
        (session["user_id"],)
    )

    data = cursor.fetchall()
    conn.close()

    dates = [row[0] for row in data]
    moods = [row[1] for row in data]

    return render_template("chart.html", dates=dates, moods=moods)


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
