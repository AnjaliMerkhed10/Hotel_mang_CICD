from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # required for sessions + flash messages

DB_FILE = "database.db"

# 🔹 Initialize database
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()

        # Bookings table
        c.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                room_type TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT NOT NULL
            )
        ''')

        # Users table
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

# 🔹 Home Page
@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', user=session['username'])
    return redirect(url_for('login'))

# 🔹 Rooms Page
@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

# 🔹 Booking Page
@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'username' not in session:
        flash("⚠️ Please login first!", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form.get('name')
        room_type = request.form.get('room_type')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')

        if not name or not room_type or not check_in or not check_out:
            flash("⚠️ All fields are required!", "error")
            return redirect(url_for('booking'))

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("""
                INSERT INTO bookings (name, room_type, check_in, check_out)
                VALUES (?, ?, ?, ?)
            """, (name, room_type, check_in, check_out))
            conn.commit()

        flash("✅ Booking successful!", "success")
        return redirect(url_for('index'))

    return render_template('booking.html')

# 🔹 Admin Dashboard
@app.route('/admin')
def admin():
    if 'username' not in session:
        flash("⚠️ Login required!", "error")
        return redirect(url_for('login'))

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM bookings ORDER BY id DESC")
        data = c.fetchall()
    return render_template('admin.html', bookings=data)

# 🔹 Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash("⚠️ Username & password required", "error")
            return redirect(url_for('register'))

        try:
            with sqlite3.connect(DB_FILE) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
            flash("✅ Registration successful! Please login.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("⚠️ Username already exists!", "error")
            return redirect(url_for('register'))

    return render_template('register.html')

# 🔹 Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()

        if user:
            session['username'] = username
            flash("✅ Logged in successfully!", "success")
            return redirect(url_for('index'))
        else:
            flash("⚠️ Invalid username or password!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

# 🔹 Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("✅ You have logged out.", "info")
    return redirect(url_for('login'))

# 🔹 Run App
if __name__ == '__main__':
    init_db()
    app.run(host="0.0.0.0", port=5005, debug=True)
