import uuid
import sqlite3
from waitress import serve
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = '3db71454123a943ab7b7b293c3965c8001aae7c57893dc21750562a3a10600bf'

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
    return response

DATABASE = 'ticketify.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    with open('schema.sql', 'r') as sql_file:
        sql_script = sql_file.read()

    conn.executescript(sql_script)

    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('dashboard'))
        else:
            flash('Nieprawidłowa nazwa lub hasło.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        company_action = request.form.get('company_action')
        company_uuid = request.form.get('company_uuid')

        hashed_password = generate_password_hash(password)
        conn = get_db_connection()

        if company_action == 'create':
            company_uuid = str(uuid.uuid4())
            conn.execute("INSERT INTO companies (uuid) VALUES (?)", (company_uuid,))
            company_id = conn.execute("SELECT id FROM companies WHERE uuid = ?", (company_uuid,)).fetchone()['id']
            is_admin = True
        elif company_action == 'join':
            company = conn.execute("SELECT id FROM companies WHERE uuid = ?", (company_uuid,)).fetchone()
            if not company:
                flash('Podana firma nie istnieje.', 'error')
                return redirect(url_for('register'))
            company_id = company['id']
            is_admin = False
        else:
            flash('Nieprawidłowa akcja.', 'error')
            return redirect(url_for('register'))

        try:
            conn.execute("INSERT INTO users (username, password, is_admin, company_id) VALUES (?, ?, ?, ?)",
                         (username, hashed_password, is_admin, company_id))
            conn.commit()
            flash('Konto zostało utworzone! Zaloguj się.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Konto o tej samej nazwie już istnieje.', 'error')
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))

    user_id = session['user_id']
    conn = get_db_connection()
    company_id = conn.execute("SELECT company_id FROM users WHERE id = ?", (user_id,)).fetchone()['company_id']
    company_uuid = conn.execute("SELECT uuid FROM companies WHERE id = ?", (company_id,)).fetchone()['uuid']

    tickets = conn.execute('''
        SELECT id, title, description, status, close_comment, created_at
        FROM tickets
        WHERE user_id = ?
        ORDER BY CASE WHEN status = 'open' THEN 0 ELSE 1 END, created_at DESC
    ''', (user_id,)).fetchall()

    conn.close()
    return render_template('dashboard.html', tickets=tickets, company_uuid=company_uuid)

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        return redirect(url_for('login'))

    conn = get_db_connection()
    company_id = conn.execute("SELECT company_id FROM users WHERE id = ?", (session['user_id'],)).fetchone()['company_id']
    company_uuid = conn.execute("SELECT uuid FROM companies WHERE id = ?", (company_id,)).fetchone()['uuid']

    tickets = conn.execute('''
        SELECT t.id, t.title, t.status, t.description, t.created_at, t.close_comment, u.username AS author
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        WHERE t.company_id = ?
        ORDER BY
            CASE WHEN t.status = 'open' THEN 0 ELSE 1 END,
            t.created_at DESC
    ''', (company_id,)).fetchall()

    conn.close()
    return render_template('admin_dashboard.html', tickets=tickets, company_uuid=company_uuid)

@app.route('/submit_ticket', methods=['GET', 'POST'])
def submit_ticket():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        conn = get_db_connection()
        user_id = session['user_id']
        company_id = conn.execute("SELECT company_id FROM users WHERE id = ?", (user_id,)).fetchone()['company_id']
        conn.execute(
            "INSERT INTO tickets (user_id, company_id, title, description) VALUES (?, ?, ?, ?)",
            (user_id, company_id, title, description)
        )
        conn.commit()
        conn.close()
        flash('Zgłoszenie zostało utworzone!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('submit_ticket.html')

@app.route('/close_ticket/<int:ticket_id>', methods=['POST'])
def close_ticket(ticket_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    comment = request.form.get('close_comment', '').strip()
    is_admin = bool(session.get('is_admin', False))
    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()

    if not ticket:
        conn.close()
        flash('Zgłoszenie nie istnieje.', 'error')
        return redirect(url_for('admin_dashboard' if is_admin else 'dashboard'))

    company_id = conn.execute("SELECT company_id FROM users WHERE id = ?", (session['user_id'],)).fetchone()['company_id']
    if not is_admin and ticket['company_id'] != company_id:
        conn.close()
        flash('Brak uprawnień do zamknięcia tego zgłoszenia.', 'error')
        return redirect(url_for('dashboard'))

    close_comment = comment if is_admin else ticket['close_comment']
    conn.execute(
        "UPDATE tickets SET status = ?, close_comment = ? WHERE id = ?",
        ('closed', close_comment, ticket_id)
    )
    conn.commit()
    conn.close()
    flash('Zgłoszenie zostało zamknięte.', 'success')
    return redirect(url_for('admin_dashboard' if is_admin else 'dashboard'))

@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    if 'user_id' not in session:
        flash('Aby usunąć zgłoszenie, musisz być zalogowany.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    is_admin = session.get('is_admin', False)

    conn = get_db_connection()
    ticket = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()

    if not ticket:
        conn.close()
        flash('Zgłoszenie nie istnieje.', 'error')
        return redirect(url_for('admin_dashboard' if is_admin else 'dashboard'))

    if not is_admin and ticket['user_id'] != user_id:
        conn.close()
        flash('Nie masz uprawnień do usunięcia tego zgłoszenia.', 'error')
        return redirect(url_for('dashboard'))

    conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
    conn.commit()
    conn.close()
    flash('Zgłoszenie zostało usunięte.', 'success')
    return redirect(url_for('admin_dashboard' if is_admin else 'dashboard'))

if __name__ == '__main__':
    init_db()
    # app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=False)
    serve(app, host="0.0.0.0", port=5000)
