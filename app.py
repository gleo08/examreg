from flask import Flask, render_template, flash, url_for, session, redirect, request, logging
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)
app.secret_key = 'secret123'

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'VinID1234!@#$'
app.config['MYSQL_DB'] = 'examreg'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)


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
            password = data['password']

            # Compare
            if password_candidate == password:
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('information'))
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


# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))


@app.route('/information')
def information():
    return render_template('information.html')


if __name__ == '__main__':
    app.run(debug=True)
