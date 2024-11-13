from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import logging
from logging import Formatter, FileHandler
import secrets
from flask_wtf.csrf import CSRFProtect, CSRFError

app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.config['SECRET_KEY'] = secret_key
csrf = CSRFProtect(app)

# Database connection
def get_db():
    db = sqlite3.connect('driver_car_system.db')
    db.row_factory = sqlite3.Row
    return db
@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()
def setup_database():
    conn = sqlite3.connect('driver_car_system.db')
    cursor = conn.cursor()
    
    # Create users table with email field if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            email TEXT NOT NULL,
            is_employee BOOLEAN DEFAULT FALSE
        );
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        license_number TEXT PRIMARY KEY,
        state TEXT,
        address TEXT,
        name TEXT,
        username TEXT,
        FOREIGN KEY (username) REFERENCES users(username)
    )
    ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cars
                 (vin TEXT PRIMARY KEY, make TEXT, model TEXT, year INTEGER, color TEXT, owner_license TEXT,
                 FOREIGN KEY (owner_license) REFERENCES drivers(license_number))''')
    
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password'], password):
            session['user'] = username
            session['is_employee'] = user['is_employee']
            if user['is_employee']:
                return redirect(url_for('employee_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/user_dashboard')
def user_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('user_dashboard.html', username=session['user'])

@app.route('/employee_dashboard')
def employee_dashboard():
    if 'user' not in session or not session.get('is_employee'):
        return redirect(url_for('login'))
    
    return render_template('employee_dashboard.html', username=session['user'])

@app.route('/employee_search', methods=['GET', 'POST'])
def employee_search():
    if 'user' not in session or not session.get('is_employee'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Retrieve the form data from the POST request
        driver_license = request.form.get('driver_license', '')
        state = request.form.get('state', '')
        address = request.form.get('address', '')
        name = request.form.get('name', '')
        
        vin = request.form.get('vin', '')
        make = request.form.get('make', '')
        model = request.form.get('model', '')
        color = request.form.get('color', '')

        # Construct the query and parameters
        query = "SELECT * FROM drivers WHERE 1=1"
        params = []
        
        if driver_license:
            query += " AND license_number LIKE ?"
            params.append(f"%{driver_license}%")
        if state:
            query += " AND state LIKE ?"
            params.append(f"%{state}%")
        if name:
            query += " AND name LIKE ?"
            params.append(f"%{name}%")
        if address:
            query += " AND address LIKE ?"
            params.append(f"%{address}%")

        # For searching cars:
        if vin:
            query += " AND vin LIKE ?"
            params.append(f"%{vin}%")
        if make:
            query += " AND make LIKE ?"
            params.append(f"%{make}%")
        if model:
            query += " AND model LIKE ?"
            params.append(f"%{model}%")
        if color:
            query += " AND color LIKE ?"
            params.append(f"%{color}%")

        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, params)
        
        # Fetch matching results
        driver_results = cursor.fetchall()
        
        # If driver search results found, fetch the cars related to those drivers
        cars = []
        if driver_results:
            for driver in driver_results:
                driver_license_number = driver['license_number']
                car_query = 'SELECT * FROM cars WHERE owner_license = ?'
                cursor.execute(car_query, (driver_license_number,))
                car_results = cursor.fetchall()
                cars.append({ 'driver': driver, 'cars': car_results })

        db.close()
        
        # Return the results to the template for display
        return render_template('employee_search.html', username=session['user'], drivers=cars)

    return render_template('employee_search.html', username=session['user'])




@app.route('/upload_driver_info_page')
def upload_driver_info_page():
     return render_template('upload_driver_info_page.html')

@app.route('/register_car_page')
def register_car_page():
     return render_template('register_car_form.html')

@app.route('/transfer_car_info_page')
def transfer_car_info_page():
     return render_template('transfer_car_info.html')

@app.route('/view_info_page')
def view_info_page():
     return render_template('view_info.html')


# Logout route
@app.route('/logout')
def logout():
     session.clear()
     return redirect(url_for('login'))

# Route to handle driver info form submission
@app.route('/upload_driver_info', methods=['POST'])
def upload_driver_info():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    license_number = request.form['licenseNumber']
    state = request.form['state']
    address = request.form['address']
    name = request.form['name']
    username = session['user']
    
    db = get_db()
    try:
        # Insert new driver into the drivers table
        db.execute('INSERT INTO drivers (license_number, state, address, name, username) VALUES (?, ?, ?, ?, ?)', 
                   (license_number, state, address, name, username))
        db.commit()
        flash("Driver info uploaded successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Driver info already exists!", "error")
    finally:
        db.close()
    return redirect(url_for('user_dashboard'))

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            flash('Username already exists', 'error')
            return render_template('create_account.html')
        
        # Insert new user into the database
        cursor.execute('INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
                       (username, generate_password_hash(password), email))
        db.commit()
        
        flash('Account created successfully', 'success')
        return redirect(url_for('login'))
    
    return render_template('create_account.html')


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400

# Route to handle car registration form submission
@app.route('/register_car', methods=['POST'])
def register_car():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    vin = request.form.get('vin')
    make = request.form.get('make')
    model = request.form.get('model')
    year = request.form.get('year')
    color = request.form.get('color')
    
    db = get_db()
    try:
        # Get the driver's license number for the current user
        driver = db.execute('SELECT license_number FROM drivers WHERE username = ?', (session['user'],)).fetchone()
        if not driver:
            flash("Please upload your driver information first!", "error")
            return redirect(url_for('user_dashboard'))
        
        owner_license = driver['license_number']
        
        # Insert new car into the cars table
        db.execute('INSERT INTO cars (vin, make, model, year, color, owner_license) VALUES (?, ?, ?, ?, ?, ?)', 
                   (vin, make, model, year, color, owner_license))
    #wait(2) something needs to go here for the db lock
        db.commit()
        flash("Car registered successfully!", "success")
    except sqlite3.IntegrityError:
        flash("Car with this VIN already exists!", "error")
    finally:
        db.close()
    return redirect(url_for('user_dashboard'))

@app.route('/view_info', methods=['GET'])
def view_info():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    db = get_db()
    driver = db.execute('SELECT * FROM drivers WHERE username = ?', (session['user'],)).fetchone()
    
    if not driver:
        db.close()
        return jsonify('view_info.html', driver=None, cars=[])
        #return render_template('view_info.html', driver=None, cars=[])

    cars = db.execute('SELECT * FROM cars WHERE owner_license = ?', (driver['license_number'],)).fetchall()
    db.close()
    
    #return render_template('view_info.html', driver=driver, cars=cars)
    return jsonify({
        'name': driver['name'], 
        'license_number': driver['license_number'], 
        'address': driver['address'], 
        'cars': [dict(car) for car in cars]
    })

@app.route('/transfer_car_info', methods=['POST'])
def transfer_car_info():
     if 'user' not in session:
         return jsonify({"error": "Unauthorized"}), 401

     vin = request.form['vin']
     new_owner_license = request.form['newOwnerLicense']

     db = get_db()

     try:
         # Update the owner of the car in the cars table
         db.execute('UPDATE cars SET owner_license = ? WHERE vin = ?', (new_owner_license, vin))
         db.commit()
         flash("Car ownership transferred successfully!", "success")
     except sqlite3.Error as e:
         flash(f"An error occurred while transferring ownership: {str(e)}", "error")
     finally:
         db.close()

     return redirect(url_for('user_dashboard'))

@app.route('/employee_query', methods=['POST'])
def employee_query():
    if 'user' not in session or not session['is_employee']:
        return jsonify({"error": "Unauthorized"}), 401

    query = request.form['query']
    params = request.form.get('params', [])

    db = get_db()
    try:
        result = db.execute(query, params).fetchall()
        return jsonify([dict(row) for row in result]), 200
    except sqlite3.Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        db.close()

if __name__ == '__main__':
    setup_database()
    app.run(debug=True)


@app.route('/employee_search', methods=['GET'])
def employee_search():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    db = get_db()
    driver = db.execute('SELECT * FROM drivers WHERE username = ?', (session['user'],)).fetchone()
    
    if not driver:
        db.close()
        return jsonify('employee_search.html', driver=None, cars=[])
        #return render_template('employee_search.html', driver=None, cars=[])

    cars = db.execute('SELECT * FROM cars WHERE owner_license = ?', (driver['license_number'],)).fetchall()
    db.close()
    
    #return render_template('view_info.html', driver=driver, cars=cars)
    return jsonify({
        'name': driver['name'], 
        'license_number': driver['license_number'], 
        'address': driver['address'], 
        'cars': [dict(car) for car in cars]
    })


@app.route('/search', methods=['GET'])
def search():
    # Get search parameters from the query string
    license_number = request.args.get('license_number', '')
    state = request.args.get('state', '')
    name = request.args.get('name', '')
    vin = request.args.get('vin', '')

    # Construct the SQL query based on the search parameters
    query = "SELECT * FROM drivers WHERE 1=1"
    params = []

    if license_number:
        query += " AND license_number LIKE ?"
        params.append(f"%{license_number}%")
    if state:
        query += " AND state LIKE ?"
        params.append(f"%{state}%")
    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")
    if vin:
        query += " AND vin LIKE ?"
        params.append(f"%{vin}%")

    # Execute the query and fetch results
    cursor = db.execute(query, params)
    results = cursor.fetchall()

    # Convert results to a list of dictionaries (assuming SQLite)
    drivers = [{'license_number': row[0], 'state': row[1], 'name': row[2], 'vin': row[3]} for row in results]

    return jsonify(drivers)
