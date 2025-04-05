{
    let socket = io('/profile');

    let query = window.location.search;
    let url_params = new URLSearchParams(query);
    let params = Object.fromEntries(url_params.entries());
    let user_uid = parseInt(params.uid);
    let company_roles;
    let role_names = {};

    socket.on('employee_data', (data) => {
        let image = data[user_uid]['Image'][0];
        let phone1 = data[user_uid]['Phone'][0];
        let phone2 = (data[user_uid]['Phone'].length > 1) ? data[user_uid]['Phone'][1] : '###-###-####';
        let role = data[user_uid]['CurrentRole'][0];
        let hired = new Date(data[user_uid]['StartDate'])

        document.getElementById('user-icon').src = `data:image/jpg;base64,${btoa(String.fromCharCode(...new Uint8Array(image)))}`;
        document.getElementById('user-name').innerText = data[user_uid]['Name'][0];
        document.getElementById('user-roles').innerText = `Role: ${(role === undefined) ? 'N/A' : role}`;
        //document.getElementById('full-name').innerText = data[user_uid]['Name'][0];
        //document.getElementById('user-email').innerText = data[user_uid]['Email'][0];
        //document.getElementById('phone1').innerText = phone1;
        //document.getElementById('phone2').innerText = phone2;
        document.getElementById('time-since').innerText = `Since: ${hired.toDateString()}`;

        let links = ['website', 'github', 'twitter', 'instagram', 'facebook']
        let portfolio = data[user_uid]['DigitalPortfolio'];

        for (let link_type of links)
        {
            //document.getElementById(`link-${link_type}`).innerText = (link_type in portfolio) ? portfolio[link_type.toLowerCase()] : 'N/A';
        }
    });

    socket.on('company_roles', (roles) => {
        company_roles = roles;
        let root = document.getElementById('skillDropdown');

        for (let roleid in roles)
        {
            let role = roles[roleid];
            let option = document.createElement('option');
            option.innerText = role['Name'];
            root.appendChild(option);
            role_names[role['Name']] = roleid;
        }
    });

    socket.on('employee_skills', (data) => {
        let selectElement = document.getElementById('skillDropdown');
        let selectedIndex = selectElement.selectedIndex;
        let selectedOption = selectElement.options[selectedIndex];
        let target_data = data[role_names[selectedOption.text]];
        console.log(target_data);

        const dialog = document.getElementById("skillDialog");
        const container = document.getElementById("skillsGraphContainer");
        const container2 = document.getElementById('resultsGraphContainer')

        container.innerHTML = "";

        let required = target_data['RequiredPartial'] * 100;
        let optional = target_data['OptionalPartial'] * 100;

        const required_wrapper = document.createElement("div");
        required_wrapper.className = "mb-2";

        const required_label = document.createElement("div");
        required_label.innerText = `Matched Required Skills: ${Math.round(required)}%`;

        const required_bar = document.createElement("div");
        required_bar.style.width = required + "%";
        required_bar.style.height = "20px";
        required_bar.style.backgroundColor = "#007bff";
        required_bar.style.color = "#fff";
        required_bar.style.textAlign = "right";
        required_bar.style.paddingRight = "5px";
        required_bar.style.borderRadius = "4px";
        required_bar.innerText = Math.round(required) + "%";

        required_wrapper.appendChild(required_label);
        required_wrapper.appendChild(required_bar);
        container2.appendChild(required_wrapper);

        const optional_wrapper = document.createElement("div");
        optional_wrapper.className = "mb-2";

        const optional_label = document.createElement("div");
        optional_label.innerText = `Matched Optional Skills: ${Math.round(optional)}%`;

        const optional_bar = document.createElement("div");
        optional_bar.style.width = optional + "%";
        optional_bar.style.height = "20px";
        optional_bar.style.backgroundColor = "#007bff";
        optional_bar.style.color = "#fff";
        optional_bar.style.textAlign = "right";
        optional_bar.style.paddingRight = "5px";
        optional_bar.style.borderRadius = "4px";
        optional_bar.innerText = Math.round(optional) + "%";

        optional_wrapper.appendChild(optional_label);
        optional_wrapper.appendChild(optional_bar);
        container2.appendChild(optional_wrapper);

        for (let role in target_data) {

            Object.entries(target_data[role]).forEach(([skill, percent]) => {
                const wrapper = document.createElement("div");
                wrapper.className = "mb-2";

                const label = document.createElement("div");
                label.innerText = `${skill}: ${percent}%`;

                const bar = document.createElement("div");
                bar.style.width = percent + "%";
                bar.style.height = "20px";
                bar.style.backgroundColor = "#007bff";
                bar.style.color = "#fff";
                bar.style.textAlign = "right";
                bar.style.paddingRight = "5px";
                bar.style.borderRadius = "4px";
                bar.innerText = percent + "%";

                wrapper.appendChild(label);
                wrapper.appendChild(bar);
                container.appendChild(wrapper);
            });
        }

            dialog.showModal();
    });

    window.addEventListener('load', (event) => {
       socket.emit('request_employee_data', user_uid);
       socket.emit('request_company_roles');
    });

    function openSkillDialog() {
        socket.emit('request_employee_skills', user_uid);
    }
}