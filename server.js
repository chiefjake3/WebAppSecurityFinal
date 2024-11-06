const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// MySQL Database Connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',      // Change this if your MySQL user is different
    password: 'your_password',  // Replace with your MySQL root password
    database: 'driver_database'
});

db.connect((err) => {
    if (err) {
        console.error('Error connecting to MySQL:', err);
        return;
    }
    console.log('Connected to MySQL');
});

// Endpoint to handle form submission
app.post('/submit-driver-form', (req, res) => {
    const { name, licenseNumber, state, address } = req.body;

    // Insert form data into the database
    const sql = 'INSERT INTO drivers (name, licenseNumber, state, address) VALUES (?, ?, ?, ?)';
    db.query(sql, [name, licenseNumber, state, address], (err, result) => {
        if (err) {
            console.error('Error inserting data:', err);
            return res.status(500).send('Server error');
        }
        res.send('Driver information successfully added!');
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
