async function executeQuery() {
    const query = document.getElementById('query-input').value;
    const response = await fetch('/employee_query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `query=${encodeURIComponent(query)}`
    });
    const result = await response.json();
    document.getElementById('result-container').innerHTML = `
        <h2>Query Result</h2>
        <pre>${JSON.stringify(result, null, 2)}</pre>
    `;
}

async function employeeSearch() {
    const response = await fetch('/employee_search');
    const data = await response.json();

    if (data.error)
    {
        alert(data.error);
    }
    else 
    {
        console.log(data)
        console.log("data is shown")
        //document.getElementById('search-container').innerHTML = `
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
