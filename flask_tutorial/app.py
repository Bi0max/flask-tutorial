import gc

from flask import Flask, render_template, flash, request, url_for, redirect, session, g
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators, BooleanField

from flask_tutorial.content_management import content
from flask_tutorial.db_connect import connection

TOPIC_DICT = content()

app = Flask(__name__)
app.secret_key = 'my unobvious secret key'


@app.route('/')
def homepage():
    return render_template('main.html')


@app.route('/darkboard/')
@app.route('/dashboard/')
def dashboard():
    flash("Flash test!!")
    return render_template('dashboard.html', TOPIC_DICT=TOPIC_DICT)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(405)
def page_not_found(e):
    return render_template('405.html')


@app.route('/slashboard/')
def errorboard():
    try:
        raise ValueError("Show error")
        return render_template('dashboard.html', TOPIC_DICT=TOPIC_DICT)
    except Exception as e:
        return render_template('500.html', error=e)


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    try:
        if request.method == "POST":
            attempted_username = request.form['username']
            attempted_password = request.form['password']

            # flash(attempted_username)
            # flash(attempted_password)

            if attempted_username == 'admin' and attempted_password == 'pass':
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid credentials. Try again."
                return render_template('login.html', error=error)
        return render_template('login.html')
    except Exception as e:
        return render_template('login.html', error=e)


class RegistrationForm(Form):
    username = StringField('Username', [validators.Length(min=4, max=20), validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=50), validators.Email(), validators.DataRequired()])
    password = PasswordField('Password', [validators.Length(min=8, max=16), validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Password do not match.")])
    confirm = PasswordField('Repeat password')
    accept_tos = BooleanField(
        "I accept the <a href='/tos/'>Terms of Service</a> and the "
        "<a href='/privacy/'>Privacy Notice</a> (Last updated 12.07.18).", [validators.DataRequired()])


@app.route('/register/', methods=['GET', 'POST'])
def register_page():
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            c, conn = connection()
            c.execute("SELECT * FROM users WHERE username=?", (username,))
            if len(c.fetchall()) > 0:
                flash("That username is already taken.")
                return render_template("register.html", form=form)
            else:
                c.execute("INSERT INTO users (username, password, email, tracking) VALUES (?, ?, ?, ?)",
                          (username, password, email, "/introduction-to-python-programming/"))
                conn.commit()
                flash("Thanks for registering!")
                c.close()
                conn.close()
                gc.collect()

                session['logged_in'] = True
                session['username'] = username
                return redirect(url_for("dashboard"))
        return render_template("register.html", form=form)




if __name__ == '__main__':
    app.run()
