import flask
import time

import CustomMethodsVI.Connection as Connection

app: flask.Flask = flask.Flask(__name__, static_folder='static', template_folder='templates')
socketio: Connection.FlaskSocketioServer = Connection.FlaskSocketioServer(app)


@app.route('/ncathack')
def index():
    return flask.render_template('index.html')


if __name__ == '__main__':
    try:
        socketio.async_listen(port=443)
        print(f'Server started @ {socketio.host}:{socketio.port}')

        while not socketio.closed:
            time.sleep(1)
    except (SystemExit, KeyboardInterrupt):
        print('Server closed.')
        socketio.close()
