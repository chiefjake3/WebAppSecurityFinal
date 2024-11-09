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