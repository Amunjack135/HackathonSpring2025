import CustomMethodsVI.Connection as Connection


def init(socketio: Connection.FlaskSocketioServer) -> None:
    common: Connection.FlaskSocketioNamespace = socketio.of('/common')

    @common.on('connect')
    def onconnect(socket: Connection.FlaskSocketioSocket):
        @socket.on('disconnect')
        def ondisconnect(disconnector: bool):
            print(f' - Socket disconnected with UID {socket.uid}; {"KICKED" if disconnector else "DROPPED"}')

        print(f' - Socket connected @ {socket.ip_address} with UID {socket.uid}')
