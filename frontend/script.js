// script.js

let token = localStorage.getItem('token');

function updateUI(isLoggedIn, isAdmin = false) {
    document.getElementById('login').style.display = isLoggedIn ? 'none' : 'block';
    document.getElementById('dashboard').style.display = isLoggedIn ? 'block' : 'none';
    document.getElementById('adminPanel').style.display = isAdmin ? 'block' : 'none';
    document.getElementById('registerDriver').style.display = isLoggedIn ? 'block' : 'none';
    document.getElementById('registerCar').style.display = isLoggedIn ? 'block' : 'none';
}

document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('http://localhost:3000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            token = data.token;
            localStorage.setItem('token', token);
            updateUI(true, data.isAdmin);
        } else {
            alert('Login failed. Please check your credentials.');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});

document.getElementById('logoutBtn').addEventListener('click', () => {
    token = null;
    localStorage.removeItem('token');
    updateUI(false);
});

document.getElementById('driverForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const driverData = {
        name: document.getElementById('driverName').value,
        license_number: document.getElementById('licenseNumber').value,
        state: document.getElementById('state').value,
        address: document.getElementById('address').value
    };

    try {
        const response = await fetch('http://localhost:3000/drivers', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(driverData)
        });

        if (response.ok) {
            alert('Driver registered successfully');
            e.target.reset();
        } else {
            const errorData = await response.json();
            alert(`Registration failed: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});

document.getElementById('carForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const carData = {
        vin: document.getElementById('vin').value,
        make: document.getElementById('make').value,
        model: document.getElementById('model').value,
        year: document.getElementById('year').value,
        color: document.getElementById('color').value,
        owner_license_number: document.getElementById('ownerLicenseNumber').value
    };

    try {
        const response = await fetch('http://localhost:3000/cars', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(carData)
        });

        if (response.ok) {
            alert('Car registered successfully');
            e.target.reset();
        } else {
            const errorData = await response.json();
            alert(`Registration failed: ${errorData.error}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});

document.getElementById('carSearchForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const vin = document.getElementById('searchVin').value;

    try {
        const response = await fetch(`http://localhost:3000/cars/${vin}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            const carData = await response.json();
            document.getElementById('carSearchResult').innerHTML = `
                <h4>Car Details:</h4>
                <p>VIN: ${carData.vin}</p>
                <p>Make: ${carData.make}</p>
                <p>Model: ${carData.model}</p>
                <p>Year: ${carData.year}</p>
                <p>Color: ${carData.color}</p>
                <p>Owner: ${carData.owner_name}</p>
                <p>Owner Address: ${carData.owner_address}</p>
            `;
        } else {
            document.getElementById('carSearchResult').innerHTML = 'Car not found or you do not have permission to view this information.';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    }
});

// Check if user is already logged in
if (token) {
    updateUI(true);
} else {
    updateUI(false);
}