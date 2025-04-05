import cv2

import CustomMethodsVI.Connection as Connection

import EmployeeProfile
import CompanyRole
import Resume
import gpt


def init(socketio: Connection.FlaskSocketioServer, gpt_api: gpt.MyGPTAPI) -> None:
    common: Connection.FlaskSocketioNamespace = socketio.of('/common')
    index: Connection.FlaskSocketioNamespace = socketio.of('/index')
    profile: Connection.FlaskSocketioNamespace = socketio.of('/profile')

    @common.on('connect')
    def on_connect(socket: Connection.FlaskSocketioSocket):
        @socket.on('disconnect')
        def on_disconnect(disconnector: bool):
            print(f' - /common: Socket disconnected with UID {socket.uid}; {"KICKED" if disconnector else "DROPPED"}')

        print(f' - /common: Socket connected @ {socket.ip_address} with UID {socket.uid}')

    @index.on('connect')
    def on_connect(socket: Connection.FlaskSocketioSocket):
        @socket.on('disconnect')
        def on_disconnect(disconnector: bool):
            print(f' - /index: Socket disconnected with UID {socket.uid}; {"KICKED" if disconnector else "DROPPED"}')

        @socket.on('request_employee_previews')
        def on_request_employee_previews():
            socket.emit('employee_previews', {uid: {'image': cv2.imencode('.jpg', data.image_icon)[1].tobytes(), 'name': data.name, 'role': data.current_roles[0] if len(data.current_roles) > 0 else None} for uid, data in EmployeeProfile.MyEmployeeProfile.EMPLOYEES.items()})

        print(f' - /index: Socket connected @ {socket.ip_address} with UID {socket.uid}')

    @profile.on('connect')
    def on_connect(socket: Connection.FlaskSocketioSocket):
        @socket.on('disconnect')
        def on_disconnect(disconnector: bool):
            print(f' - /profile: Socket disconnected with UID {socket.uid}; {"KICKED" if disconnector else "DROPPED"}')

        @socket.on('request_employee_previews')
        def on_request_employee_previews():
            socket.emit('employee_previews', {uid: {'image': cv2.imencode('.jpg', data.image_icon)[1].tobytes(), 'name': data.name, 'role': data.current_roles[0]} for uid, data in EmployeeProfile.MyEmployeeProfile.EMPLOYEES.items()})

        @socket.on('request_employee_data')
        def on_request_employee_data(uid: int):
            pass

        @socket.on('request_employee_skills')
        def on_request_employee_skills(uid: int):
            pass

        @socket.on('request_employee_ranked_roles')
        def on_request_employee_ranked_roles(uid: int):
            pass

        print(f' - /profile: Socket connected @ {socket.ip_address} with UID {socket.uid}')
