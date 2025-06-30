
from flask import Flask, request, session, g
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"
CORS(app)

DATABASE = 'worktime.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        db.commit()

@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    password = request.form["password"]
    db = get_db()
    try:
        db.execute("INSERT INTO users (email, password) VALUES (?, ?)",
                   (email, generate_password_hash(password)))
        db.commit()
        return "User registered successfully", 200
    except sqlite3.IntegrityError:
        return "User already exists", 400

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if user and check_password_hash(user['password'], password):
        session['user'] = email
        return f"Clocked in at login time", 200
    return "Invalid credentials", 401

@app.route("/logout", methods=["POST"])
def logout():
    if "user" in session:
        user = session.pop("user")
        return f"User {user} clocked out", 200
    return "No active session", 400

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
