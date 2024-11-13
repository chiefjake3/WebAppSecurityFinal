import sqlite3

def setup_database():
    conn = sqlite3.connect('driver_car_system.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, is_employee BOOLEAN)''')

    c.execute('''CREATE TABLE IF NOT EXISTS drivers
                 (license_number TEXT PRIMARY KEY, state TEXT, address TEXT, name TEXT, username TEXT,
                 FOREIGN KEY (username) REFERENCES users(username))''')

    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (vin TEXT PRIMARY KEY, make TEXT, model TEXT, year INTEGER, color TEXT, owner_license TEXT,
                 FOREIGN KEY (owner_license) REFERENCES drivers(license_number))''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("Database setup complete.")