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


@app.route('/getSubjects', methods=['GET'])
def getSubjects():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM subjects')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/insertUsers', methods=['POST'] )
def insertUsers():
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    f = request.files['file']
    r = pd.read_csv(f, sep=',')
    for it in r.iterrows():
       cur.execute('INSERT INTO users(user_name, pass, name, date_of_birth, role_id) VALUES(%s, %s, %s, %s, %s)', it[1])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/insertSubjects', methods=['POST'])
def insertSubjects():
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    f = request.files['file']
    r = pd.read_csv(f, sep=',')
    for it in r.iterrows():
        cur.execute('INSERT INTO subjects(name, code) VALUES(%s, %s)', it[1])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/insertSS/<id>', methods=['POST'])
def insertSS(id):
    subjectId = id
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    f = request.files['file']
    r = pd.read_csv(f, sep=',')
    for it in r.iterrows():
        cur.execute('INSERT INTO students_subjects(student_id, student_name, date_of_birth, contest_id, is_approved, subject_id) VALUES(%s, %s, %s, %s, %s, %s)', [it[1][0],it[1][1],it[1][2],it[1][3],it[1][4],subjectId])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/makeContest', methods=['POST'])
def makeContest():
    mysql.connection.autocommit(on=True)
    data = request.get_json()
    nameContest = data['nameContest']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO contest(name) VALUES (%s)', [nameContest])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/addTiming', methods=['POST'])
def addTiming():
    mysql.connection.autocommit(on=True)
    data = request.get_json()
    date = data['date']
    name = data['shiftName']
    begin_time = data['beginTime']
    end_time = data['endTime']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO timing(date, name, begin_time, end_time) VALUES (%s, %s, %s, %s)', [date, name, begin_time, end_time])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/addRoom', methods=['POST'])
def addRoom():
    if request.method == 'POST':
        data = request.get_json()
        name = data['roomName']
        slots =  data['slots']
        mysql.connection.autocommit(on=True)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO rooms (name, slots) VALUES(%s, %s)",(name, slots))
        cur.close()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/insertSRS/<id>', methods=["POST"])
def insertSRS(id):
    subjectId = id
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    f = request.files['file']
    r = pd.read_csv(f, sep=',')
    for it in r.iterrows():
        cur.execute('INSERT INTO timing_room(timing_id, room_id, contest_id, subject_id) VALUES(%s, %s, %s, %s)',[it[1][0], it[1][1], it[1][2], subjectId])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/getListOfRooms', methods=['GET'])
def getListOfRooms():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM rooms')
    #row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    #result = []
    #for r in rv:
        #result.append(dict(zip(row_headers, r)))
    result = json.dumps(rv)
    return result


@app.route('/getListOfTiming', methods=['GET'])
def getListOfTiming():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM timing')
    #row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    #result = []
    #for r in rv:
        #result.append(dict(zip(row_headers, r)))
    result = json.dumps(rv)
    return result


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


@app.route('/timingOfSubjectAdmin', methods=['GET'])
def timingOfSubjectAdmin():
    cur = mysql.connection.cursor()
    cur.execute('SELECT tr.timing_id, t.name, t.begin_time, t.end_time, tr.subject_id FROM timing_room AS tr INNER JOIN timing AS t ON t.id = tr.timing_id')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/roomOfTimingSubjectAdmin', methods=['GET'])
def roomresult():
    cur = mysql.connection.cursor()
    cur.execute('SELECT r.name, r.id, tr.timing_id, tr.subject_id FROM timing_room AS tr INNER JOIN rooms AS r ON tr.room_id = r.id ')
    rv = cur.fetchall()
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


@app.route('/registed', methods=['POST'])
def registed():
    index = session['id']
    cur = mysql.connection.cursor()
    mysql.connection.autocommit(on=True)
    data = request.get_json(force=True)
    timingId = data['timing_id']
    roomId = data['room_id']
    subjectId = data['subject_id']
    #GET timing_room_id:
    cur1 = mysql.connection.cursor()
    cur1.execute('SELECT tr.id FROM timing_room AS tr  WHERE tr.timing_id = %s AND tr.room_id = %s AND tr.subject_id = %s ',[timingId, roomId, subjectId])
    rv1 = cur1.fetchone()
    i = rv1['id']
    #GET number of registed:
    cur2 = mysql.connection.cursor()
    cur2.execute('SELECT COUNT(*) as s FROM registered AS reg INNER JOIN timing_room AS tr ON reg.timing_room_id = tr.id WHERE tr.id = %s', [i])
    rv2 = cur2.fetchone()
    j = rv2['s']
    #GET slots of room:
    cur3 = mysql.connection.cursor()
    cur3.execute('SELECT r.slots FROM rooms AS r WHERE r.id = %s', [roomId])
    rv3 = cur3.fetchone()
    k = rv3['slots']
    #Registetration:
    if k > j:
        cur.execute('INSERT INTO registered(student_id, timing_room_id) VALUE(%s, %s)', [index, i])
        cur.close()
        cur1.close()
        cur2.close()
        cur3.close()
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else :
        return json.dumps({'success': False}), 200, {'ContentType': 'application/json'}


@app.route('/getRegisted', methods=['GET'])
def getRegisted():
    index = session['id']
    cur = mysql.connection.cursor()
    cur.execute('SELECT s.name, s.code, t.date, t.name AS tname, t.begin_time, t.end_time, r.name AS rname, reg.id FROM registered AS reg INNER JOIN timing_room AS tr ON reg.timing_room_id = tr.id INNER JOIN timing AS t ON tr.timing_id = t.id INNER JOIN rooms AS r ON tr.room_id = r.id INNER JOIN subjects s ON tr.subject_id = s.id WHERE reg.student_id = %s', [index])
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/registedAdmin', methods=['GET'])
def registedAdmin():
    cur = mysql.connection.cursor()
    cur.execute('SELECT u.name, u.date_of_birth FROM registered AS reg  INNER JOIN timing_room AS tr ON reg.timing_room_id = tr.id INNER JOIN users AS u ON reg.student_id = u.id INNER JOIN rooms AS r ON tr.room_id = r.id INNER JOIN timing AS t ON t.id = tr.timing_id INNER JOIN subjects AS s ON tr.subject_id = s.id')
    #row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    #result = []
    #for r in rv:
        #result.append(dict(zip(row_headers, r)))
    result = json.dumps(rv)
    return result


@app.route('/getDate', methods=['GET'])
def getDate():
    cur = mysql.connection.cursor()
    cur.execute('SELECT DISTINCT t.date FROM timing AS t')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/getShiftOfDate', methods=['GET'])
def getShift():
    cur = mysql.connection.cursor()
    cur.execute('SELECT t.id, t.date, t.name, t.begin_time, t.end_time FROM timing AS t')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/getRooms', methods=['GET'])
def getRooms():
    cur = mysql.connection.cursor()
    cur.execute('SELECT r.id, r.name, r.slots FROM rooms AS r')
    rv = cur.fetchall()
    result = json.dumps(rv)
    return result


@app.route('/insertTRS', methods=['POST'])
def insert():
    mysql.connection.autocommit(on=True)
    cur = mysql.connection.cursor()
    data = request.get_json()
    tID = data['timing_id']
    print(data)
    rID = data['room_id']
    sID = data['subject_id']
    cur.execute('INSERT INTO timing_room(timing_id, room_id, subject_id, contest_id) VALUES(%s, %s,%s,%s)', [tID, rID, sID, 1])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/deleteRegistered', methods=['POST'])
def deleteRegistered():
    mysql.connection.autocommit(on=True)
    data = request.get_json(force=True)
    key = data['id']
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM registered WHERE id = %s', [key])
    cur.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(debug=True)


