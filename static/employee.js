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

function employeeSearch() {
    // Collect values from form fields
    const licenseNumber = document.getElementById('licenseNumber').value.trim();
    const state = document.getElementById('state').value.trim();
    const name = document.getElementById('name').value.trim();
    const vin = document.getElementById('vin').value.trim();

    // Construct search criteria object based on filled fields
    const searchCriteria = {};
    if (licenseNumber) searchCriteria.license_number = licenseNumber;
    if (state) searchCriteria.state = state;
    if (name) searchCriteria.name = name;
    if (vin) searchCriteria.vin = vin;

    // Create the query string from the search criteria
    const queryString = new URLSearchParams(searchCriteria).toString();

    // Call the function to fetch data from the server
    fetchSearchResults(queryString);
}

function fetchSearchResults(queryString) {
    const searchInfoDiv = document.getElementById('search-info');
    
    // Make sure we show a loading message while fetching results
    searchInfoDiv.innerHTML = '<p>Loading search results...</p>';

    // Send a GET request to the server with the query string
    fetch(`/search?${queryString}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                searchInfoDiv.innerHTML = '<p>No results found.</p>';
            } else {
                displaySearchResults(data);
            }
        })
        .catch(error => {
            searchInfoDiv.innerHTML = '<p>Error fetching results. Please try again later.</p>';
            console.error('Error:', error);
        });
}

function displaySearchResults(data) {
    const searchInfoDiv = document.getElementById('search-info');

    // Clear any previous results
    searchInfoDiv.innerHTML = '';

    // Create a table to display the results
    const table = document.createElement('table');
    table.setAttribute('border', '1');
    table.style.width = '100%';
    table.style.marginTop = '20px';

    // Add table headers
    const headers = ['License Number', 'State', 'Driver Name', 'VIN'];
    const headerRow = table.insertRow();
    headers.forEach(headerText => {
        const headerCell = headerRow.insertCell();
        headerCell.textContent = headerText;
        headerCell.style.fontWeight = 'bold';
    });

    // Add data rows
    data.forEach(item => {
        const row = table.insertRow();
        row.insertCell().textContent = item.license_number;
        row.insertCell().textContent = item.state;
        row.insertCell().textContent = item.name;
        row.insertCell().textContent = item.vin;
    });

    // Append the table to the results div
    searchInfoDiv.appendChild(table);
}
