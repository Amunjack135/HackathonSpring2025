{
    let socket = io('/index');

    socket.on('employee_previews', (previews) => {
        let root = document.getElementById('avatar-container');

        for (let uid in previews)
        {
            let preview = previews[uid];
            let container = document.createElement('div');
            let image = document.createElement('img');
            let name = document.createElement('span');
            image.src = `data:image/jpg;base64,${btoa(String.fromCharCode(...new Uint8Array(preview['image'])))}`;
            name.innerText = preview['name'];
            container.appendChild(image);
            container.appendChild(name);
            root.appendChild(container);
        }
    });

    window.addEventListener('load', (event) => {
       socket.emit('request_employee_previews');
    });
}