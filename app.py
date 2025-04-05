import atexit
import flask
import time

import CustomMethodsVI.Connection as Connection

import SocketHandler
import EmployeeProfile
import CompanyRole
import Resume

app: flask.Flask = flask.Flask(__name__, static_folder='static', template_folder='templates')
socketio: Connection.FlaskSocketioServer = Connection.FlaskSocketioServer(app)
SocketHandler.init(socketio)
EmployeeProfile.MyEmployeeProfile.load('data/employee_profiles')
CompanyRole.MyCompanyRole.load('data/company_roles')
Resume.MyResume.load('data/resumes')


@app.route('/ncathack')
def index():
    return flask.render_template('index.html')


def socketio_main():
    try:
        socketio.async_listen(port=443)
        print(f'Server started @ {socketio.host}:{socketio.port}')

        while not socketio.closed:
            time.sleep(1)
    except (SystemExit, KeyboardInterrupt):
        fallback_cleanup()
        socketio.close()


def fallback_cleanup():
    Resume.MyResume.save('data/resumes')
    print('Server closed.')


if __name__ == '__main__':
    socketio_main()
else:
    atexit.register(fallback_cleanup)
    print(f'Server started @ {socketio.host}:{socketio.port}')
