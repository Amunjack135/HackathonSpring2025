{
    let socket = io('/common');

    socket.on('disconnect', () => {
       alert('Server Closed');
       document.open();
    });
}