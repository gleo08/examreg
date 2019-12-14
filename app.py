from flask import Flask, render_template, flash, url_for, session, redirect, request, jsonify
from flask_mysqldb import MySQL
import json
import pandas as pd
from functools import wraps
from config import config

app = Flask(__name__)

app.secret_key = config.app_secret_key

# Config MySQL
app.config['MYSQL_HOST'] = config.mysql_host
app.config['MYSQL_USER'] = config.mysql_user
app.config['MYSQL_PASSWORD'] = config.mysql_pass
app.config['MYSQL_DB'] = config.mysql_db
app.config['MYSQL_CURSORCLASS'] = config.mysql_cursor_class
# init MYSQL
mysql = MySQL(app)

# mysql.connection.autocommit(on=True)


@app.route('/')
def index():
    return render_template('home.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']

        # Create cursor
        cur = mysql.connection.cursor()

        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE user_name = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['pass']
            role = data['role_id']

            # Compare
            if password_candidate == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                if role == 0:
                    session['logged_in1'] = True
                    return redirect(url_for('student'))
                else:
                    session['logged_in0'] = True
                    return redirect(url_for('admin'))

            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
        cur.close()

    return render_template('login.html')


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap

def is_logged_in0(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in0' in session:
            return f(*args, **kwargs)
        else:
            session.clear()
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap

def is_logged_in1(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in1' in session:
            return f(*args, **kwargs)
        else:
            session.clear()
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))

    return wrap


# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/student')
@is_logged_in
@is_logged_in1
def student():
    return render_template('student.html')

@app.route('/admin')
@is_logged_in
@is_logged_in0
def admin():
    return render_template('admin.html')

@app.route('/upload1', methods=['POST'] )
def upload1():
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    f = request.files['inputFile']
    r = pd.read_csv(f, sep=',')
    for it in r.iterrows():
       cur.execute('INSERT INTO users(user_name, pass, name, role_id) VALUES(%s, %s, %s, %s)', it[1])

    cur.close()
    flash('Import Success', 'success')
    return redirect(url_for('admin'))

@app.route('/upload2', methods=['POST'])
def upload2():
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    f = request.files['inputFile']
    r = pd.read_csv(f, sep=',')
    for it in r.iterows():
        cur.execute('INSERT INTO subjects_students(student_id, subject_id, contest_id, is_approved) VALUES(%s, %s, %s, %s)', it[1])

    cur.close()
    flash('Import Succes', 'success')
    return redirect(url_for('admin'))

@app.route('/information', methods=['GET'])
def information():
    cur = mysql.connection.cursor()
    cur.execute('SELECT users.id, users.name, users.user_name, s.name, s.code, ss.is_approved FROM users INNER JOIN students_subjects ss ON users.id = ss.student_id INNER JOIN subjects s ON s.id = ss.subject_id WHERE users.role_id = 2 ORDER BY users.id ASC')
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    result = []
    for r in rv:
        result.append(dict(zip(row_headers, r)))
    return json.dump(result)

@app.route('/makeContest', methods=['POST'])
def makeContest():
    mysql.connection.autocommit(on=True)
    if request.method == 'POST':
        nameContest = request.form['namecontest']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO contest(name) VALUES (%s)', [nameContest])

    cur.close()

@app.route('/addTiming', methods=['POST'])
def addTiming():
    mysql.connection.autocommit(on=True)
    if request.method == 'POST':
        name = request.get_json('name')
        begin_time = request.get_json('begin_time')
        end_time = request.get_json('end_time')
        room_name = request.get_json('room_name')
        subject_name = request.get_json('subject_name')
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO timing(name, begin_time, end_time) VALUES (%s, %s, %s)', [name, begin_time, end_time])
    cur.execute('INSERT INTO timing_room(')

    cur.close()


@app.route('/getListOfRoom', methods=['GET'])
def getListofRoom():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM room')
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    result = []
    for r in rv:
        result.append(dict(zip(row_headers, r)))
    return json.dump(result)


@app.route('/rooms', methods=['POST'])
def create_room():
    if request.method == 'POST':
        data = request.get_json()
        name, slots = data['name'], data['slots']

        mysql.connection.autocommit(on=True)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO rooms (name, slots) VALUES(%s, %s)",
                    (name, slots))
        cur.close()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)


