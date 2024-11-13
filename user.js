function showUploadDriverInfo() {
    const formHtml = `
        <h2>Upload Driver Info</h2>
        <form id="driver-info-form">
            <input type="text" name="license_number" placeholder="License Number" required>
            <input type="text" name="state" placeholder="State" required>
            <input type="text" name="address" placeholder="Address" required>
            <input type="text" name="name" placeholder="Name" required>
            <button type="submit">Submit</button>
        </form>
    `;
    document.getElementById('form-container').innerHTML = formHtml;
    document.getElementById('driver-info-form').addEventListener('submit', uploadDriverInfo);
}

function showRegisterCar() {
    const formHtml = `
        <h2>Register New Car</h2>
        <form id="car-registration-form">
            <input type="text" name="vin" placeholder="VIN" required>
            <input type="text" name="make" placeholder="Make" required>
            <input type="text" name="model" placeholder="Model" required>
            <input type="number" name="year" placeholder="Year" required>
            <input type="text" name="color" placeholder="Color" required>
            <input type="text" name="owner_license" placeholder="Owner's License Number" required>
            <button type="submit">Submit</button>
        </form>
    `;
    document.getElementById('form-container').innerHTML = formHtml;
    document.getElementById('car-registration-form').addEventListener('submit', registerCar);
}

async function uploadDriverInfo(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/upload_driver_info', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    alert(result.message || result.error);
}

async function registerCar(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const response = await fetch('/register_car', {
        method: 'POST',
        body: formData
    });
    const result = await response.json();
    alert(result.message || result.error);
}

async function viewInfo() {
    const response = await fetch('/view_info');
    const data = await response.json();

    if (data.error)
    {
        alert(data.error);
    }
    else 
    {
        console.log(data)
        console.log("data is shown")
        //document.getElementById('info-container').innerHTML = `
        const infoContainer = document.querySelector('#info');
        infoContainer.innerHTML = `
        <p>Name: ${data.name}</p>
        <p>License Number: ${data.license_number}</p>
        <p>Address: ${data.address}</p>
        <h3>Cars:</h3>
        <ul>
            ${data.cars.map(car => `<li>${car.year} ${car.make} ${car.model} (VIN: ${car.vin})</li>`).join('')}
        </ul>
        `;
        console.log("we are done here");
    }
   
}