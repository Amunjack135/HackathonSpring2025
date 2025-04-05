import flask

import CustomMethodsVI.Connection as Connection

app: flask.Flask = flask.Flask(__name__)


@app.route("/")
def index():

    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)