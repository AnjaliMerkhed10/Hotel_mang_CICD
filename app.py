from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Initialize database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            room_type TEXT NOT NULL,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/rooms')
def rooms():
    return render_template('rooms.html')

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':
        name = request.form['name']
        room_type = request.form['room_type']
        check_in = request.form['check_in']
        check_out = request.form['check_out']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, room_type, check_in, check_out) VALUES (?, ?, ?, ?)",
                  (name, room_type, check_in, check_out))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('booking.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings")
    data = c.fetchall()
    conn.close()
    return render_template('admin.html', bookings=data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
