from flask import Flask, render_template, flash, url_for, session, redirect, request
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

@app.route('/contact')
def contact():
    return render_template('contact.html')

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
            id = data['id']

            # Compare
            if password_candidate == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['id'] = id

                if role == 2:
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

# User login
@app.route('/', methods=['GET', 'POST'])
def home():
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
            id = data['id']

            # Compare
            if password_candidate == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['id'] = id

                if role == 2:
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

    return render_template('home.html')


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
    flash('Import Success', 'success')
    return redirect(url_for('admin'))

@app.route('/')

@app.route('/information', methods=['GET'])
def information():
    cur = mysql.connection.cursor()
    cur.execute('SELECT users.id, users.name, users.user_name, s.name, s.code, ss.is_approved FROM users INNER JOIN students_subjects ss ON users.id = ss.student_id INNER JOIN subjects s ON s.id = ss.subject_id WHERE users.role_id = 2 ORDER BY users.id ASC')
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    result = []
    for r in rv:
        result.append(dict(zip(row_headers, r)))
    return json.dumps(result)


@app.route('/makeContest', methods=['POST'])
def makeContest():
    mysql.connection.autocommit(on=True)
    if request.method == 'POST':
        nameContest = request.form['namecontest']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO contest(name) VALUES (%s)', [nameContest])

    cur.close()
    return flash('Success', 'success')


@app.route('/addTiming', methods=['POST'])
def addTiming():
    mysql.connection.autocommit(on=True)
    if request.method == 'POST':
        data = request.json()
        name = data['name']
        begin_time = data['begin_time']
        end_time = data['end_time']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO timing(name, begin_time, end_time) VALUES (%s, %s, %s)', [name, begin_time, end_time])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/addRooms', methods=['POST'])
def addRoom():
    if request.method == 'POST':
        data = request.get_json()
        name = data['name']
        slots =  data['slots']

        mysql.connection.autocommit(on=True)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO rooms (name, slots) VALUES(%s, %s)",
                    (name, slots))
        cur.close()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/getListOfRoom', methods=['GET'])
def getListOfRoom():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM room')
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    result = []
    for r in rv:
        result.append(dict(zip(row_headers, r)))
    return json.dumps(result)


@app.route('/getListOfTiming', methods=['GET'])
def getListOfTiming():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM timing')
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    result = []
    for r in rv:
        result.append(dict(zip(row_headers, r)))
    return json.dumps(result)


@app.route('/timingOfSubject', methods=['GET'])
def timingOfSubject():
        index = session['id']
        cur = mysql.connection.cursor()
        cur.execute('SELECT t.id, t.name, t.begin_time, t.end_time, ss.subject_id FROM timing AS t INNER JOIN timing_room AS tr ON t.id = tr.timing_id INNER JOIN students_subjects AS ss ON tr.subject_id = ss.subject_id WHERE ss.student_id = %s', [index])
        #row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        #result = []
        #for r in rv:
            #result.append(dict(zip(row_headers, r)))
        result = json.dumps(rv)
        return result

@app.route('/roomOfTimingSubject', methods=['GET'])
def roomOfTimingSubject():
    cur = mysql.connection.cursor()
    cur.execute('SELECT r.id, r.name, tr.timing_id, tr.subject_id FROM rooms AS r INNER JOIN timing_room AS tr ON r.id = tr.room_id')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result

@app.route('/yourSubjects', methods=['GET'])
def yourSubjects():
    index = session['id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT s.id, s.code, s.name, ss.is_approved FROM subjects AS s INNER JOIN students_subjects AS ss ON s.id = ss.subject_id  WHERE ss.student_id = %s ', [index])
    #row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    #result = []
    #for r in rv:
        #result.append(dict(zip(row_headers, r)))
    result = json.dumps(rv)
    return result

@app.route('/yourRegisted', methods=['GET'])
def yourRegisted():
    index = session['id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT s.code, s.name, t.name, t.begin_time, t.end_time, r.name FROM registered AS reg INNER JOIN timing_room AS tr ON reg.timing_room_id = tr.id INNER JOIN subjects AS s ON tr.subject_id = s.id INNER JOIN timing AS t ON tr.timing_id = t.id INNER JOIN rooms AS r ON tr.room_id = r.id WHERE reg.student_id = %s', index)
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    result = []
    for r in rv:
        result.append(dict(zip(row_headers, r)))
    return json.dumps(result)

@app.route('/registed', methods=['POST'])
def registed():
    index = session['id']
    mysql.connection.autocommit(on=True)
    data = request.get_json(force=True)
    cur = mysql.connection.cursor()
    tid = data['timing_id']
    rid = data['room_id']
    subid = data['subject_id']
    cur.execute('SELECT tr.id FROM timing_room AS tr  WHERE tr.timing_id = %s AND tr.room_id = %s AND tr.subject_id = %s ',[tid, rid, subid])
    rv = cur.fetchone()
    cur.execute('INSERT INTO registered(student_id, timing_room_id) VALUE(%s, %s)', [index, rv['id']])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/getRegisted', methods=['GET'])
def getRegisted():
    index = session['id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT s.name, s.code, t.name AS tname, t.begin_time, t.end_time, r.name AS rname, reg.id FROM registered AS reg INNER JOIN timing_room AS tr ON reg.timing_room_id = tr.id INNER JOIN timing AS t ON tr.timing_id = t.id INNER JOIN rooms AS r ON tr.room_id = r.id INNER JOIN subjects s ON tr.subject_id = s.id WHERE reg.student_id = %s', [index])
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/registedAdmin', methods=['GET'])
def registedAdmin():
    data = request.get_json()
    timing_name, room_name = data['timing_name'], data['room_name']
    cur = mysql.connection.cursor()
    cur.execute('SELECT u.name, s.code, t.name, t.begin_time, t.end_time FROM registered AS reg INNER JOIN timing_room AS tr ON reg.timing_room_id = tr.id INNER JOIN subjects AS s ON tr.subject_id = s.id INNER JOIN timing AS t ON tr.timing_id = t.id INNER JOIN rooms AS r ON tr.room_id = r.id INNER JOIN users AS u ON reg.student_id = u.id ORDER BY u.name DESC WHERE t.name = %s AND r.name = %s', [timing_name, room_name])
    #row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    #result = []
    #for r in rv:
        #result.append(dict(zip(row_headers, r)))
    result = json.dumps(rv)
    return result


@app.route('/deleteRegistered', methods=['POST'])
def deleteRegistered():
    mysql.connection.autocommit(on=True)
    data = request.get_json(force=True)
    key = data['id']
    print(key)
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM registered WHERE id = %s', [key])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

@app.route('/test1', methods=["GET"])
def test1():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result




if __name__ == '__main__':
    app.run(debug=True)


