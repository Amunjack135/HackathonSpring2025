{
    let socket = io('/common');

    socket.on('disconnect', () => {
        document.open();
       alert('Server Closed');
    });
}