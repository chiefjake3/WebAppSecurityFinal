from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
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
    cursor.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (license_number TEXT PRIMARY KEY, state TEXT, address TEXT, name TEXT, username TEXT,
                 FOREIGN KEY (username) REFERENCES users(username))''')

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

    db = get_db()

    try:
        # Insert new driver into the drivers table
        db.execute('INSERT INTO drivers (license_number, state, address, name, username) VALUES (?, ?, ?, ?, ?)',
                   (license_number, state, address, name, session['user']))
        
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

    vin = request.form['vin']
    make = request.form['make']
    model = request.form['model']
    year = request.form['year']
    color = request.form['color']
    owner_name = request.form['ownerName']
    owner_license = request.form['ownerLicense']

    db = get_db()

    try:
        # Insert new car into the cars table
        db.execute('INSERT INTO cars (vin, make, model, year, color, owner_license) VALUES (?, ?, ?, ?, ?, ?)',
                   (vin, make, model, year, color, owner_license))
        
        db.commit()
        
        flash("Car registered successfully!", "success")
    
    except sqlite3.IntegrityError:
        flash("Car with this VIN already exists!", "error")
    
    finally:
        db.close()

    return redirect(url_for('user_dashboard'))

@app.route('/view_info')
def view_info():
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    db = get_db()

    driver = db.execute('SELECT * FROM drivers WHERE username = ?', (session['user'],)).fetchone()

    if not driver:
        db.close()
        return render_template('view_info.html', driver=None, cars=[])

    cars = db.execute('SELECT * FROM cars WHERE owner_license = ?', (driver['license_number'],)).fetchall()

    db.close()

    return render_template('view_info.html', driver=driver, cars=cars)

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