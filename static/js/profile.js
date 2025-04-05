{
    let socket = io('/profile');

    let query = window.location.search;
    let url_params = new URLSearchParams(query);
    let params = Object.fromEntries(url_params.entries());
    let user_uid = parseInt(params.uid);

    socket.on('employee_data', (data) => {
        let user_name = document.getElementById('user-name');
        let user_icon = document.getElementById('user-icon');
        let image = data[user_uid]['Image'][0];
        console.log(image);
        user_icon.src = `data:image/jpg;base64,${btoa(String.fromCharCode(...new Uint8Array(image)))}`;
        user_name.innerText = data[user_uid]['Name'][0];
        console.log(data[user_uid]);
    });

    window.addEventListener('load', (event) => {
       socket.emit('request_employee_data', user_uid);
    });
}