from flask import Flask, render_template, flash, url_for, session, redirect, request, logging
from flask_mysqldb import MySQL
import csv
import pandas as pd
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret123'

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'examreg'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)
mysql.connection.autocommit(on='true')

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
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            role = data['role']

            # Compare
            if password_candidate == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                if role == 1:
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

@app.route('/upload', methods=['POST'] )
def upload():
    cur = mysql.connection.cursor()
    f = request.files['inputFile']
    r = pd.read_csv(f, sep=',')
    for it in r.iterrows():
        cur.execute('INSERT INTO test(id, name, score1, score2) VALUES(%s, %s, %s, %s)', it[1])
    cur.close()
    return "success"

if __name__ == '__main__':
    app.run(debug=True)