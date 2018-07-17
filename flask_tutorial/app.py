import gc
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, flash, request, url_for, redirect, session, g, make_response
from passlib.hash import sha256_crypt
from wtforms import Form, StringField, PasswordField, validators, BooleanField

from flask_tutorial.content_management import content
from flask_tutorial.db_connect import connection
from string import Template

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


HTML_TEMPLATE = Template("""
<h1>Hello ${place_name}!</h1>

<img src="https://maps.googleapis.com/maps/api/staticmap?size=700x300&markers=${place_name}" alt="map of ${place_name}">

<img src="https://maps.googleapis.com/maps/api/streetview?size=700x300&location=${place_name}" alt="street view of ${place_name}">
""")


@app.route('/<some_place>')
def some_place_page(some_place):
    return(HTML_TEMPLATE.substitute(place_name=some_place))


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        logged_in = session.get('logged_in', False)
        if logged_in:
            return f(*args, **kwargs)
        else:
            flash("You need to login first.")
            return redirect(url_for('login_page'))
    return wrapper


@app.route('/logout/')
@login_required
def logout_page():
    session.clear()
    flash("You have been logged out.")
    gc.collect()
    return redirect(url_for('homepage'))


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    try:
        c, conn = connection()
        error = ''
        if request.method == "POST":
            attempted_username = request.form['username']
            c.execute("SELECT * FROM users WHERE username=?", (attempted_username,))
            user_data = c.fetchone()
            if user_data is not None:
                hashed_password = user_data[2]
                if sha256_crypt.verify(request.form['password'], hashed_password):
                    session['logged_in'] = True
                    session['username'] = attempted_username
                    flash("You are now logged in.")
                    return redirect(url_for('dashboard'))
            error = "Invalid credentials. Try again."
            gc.collect()
        return render_template("login.html", error=error)

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


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    try:
        """Generate sitemap.xml. Makes a list of urls and date modified."""
        pages = []
        ten_days_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
        # static pages
        for rule in app.url_map.iter_rules():
            if "GET" in rule.methods and len(rule.arguments) == 0:
                pages.append(
                    ["http://pythonprogramming.net" + str(rule.rule), ten_days_ago]
                )
        print(pages)
        sitemap_xml = render_template('sitemap_template.xml', pages=pages)
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"

        return response
    except Exception as e:
        return (str(e))


# LIVE VERSION
@app.route('/robots.txt/')
def robots():
    return("User-agent: *\nDisallow: /register/\nDisallow: /login/\nDisallow: /donation-success/")


# DEV VERSION - disallow everything
# @app.route('/robots.txt/')
# def robots():
#     return("User-agent: *\nDisallow: /")
#


@app.route('/include_example/')
def include_example():
    try:
        # normally, should come from database
        replies = {'Jack': 'Cool post',
                   'Jane': '+1',
                   'Erika': 'Most definitely',
                   'Bob': 'wow',
                   'Carl': 'amazing!', }
        return render_template('include_tutorial.html', replies=replies)
    except Exception as e:
        return str(e)


@app.route('/jinjaman/')
def jinjaman():
    try:
        data = [15, '15', 'Python is good', 'Python, Java, php, SQL, C++', '<p><strong>Hey there!</strong></p>']
        return render_template("jinja_templating.html", data=data)

    except Exception as e:
        return str(e)




if __name__ == '__main__':
    app.run()
