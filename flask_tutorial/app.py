from flask import Flask, render_template

from flask_tutorial.content_management import content

TOPIC_DICT = content()

app = Flask(__name__)


@app.route('/')
def homepage():
    return render_template('main.html')


@app.route('/darkboard/')
@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html', TOPIC_DICT=TOPIC_DICT)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.route('/slashboard/')
def slashboard():
    try:
        raise ValueError("Show error")
        return render_template('dashboard.html', TOPIC_DICT=TOPIC_DICT)
    except Exception as e:
        return render_template('500.html', error=e)


if __name__ == '__main__':
    app.run()
