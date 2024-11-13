import sqlite3
from werkzeug.security import generate_password_hash

def create_admin_account():
    # Connect to the database
    conn = sqlite3.connect('driver_car_system.db')
    cursor = conn.cursor()

    # Admin account details
    admin_username = 'admin'
    admin_password = 'password'  # You should change this to a strong password
    admin_email = 'admin@example.com'
    is_employee = True

    # Hash the password
    hashed_password = generate_password_hash(admin_password)

    try:
        # Insert the admin account into the users table
        cursor.execute('''
        INSERT INTO users (username, password, email, is_employee)
        VALUES (?, ?, ?, ?)
        ''', (admin_username, hashed_password, admin_email, is_employee))

        # Commit the changes
        conn.commit()
        print("Admin account created successfully!")

    except sqlite3.IntegrityError:
        print("Admin account already exists.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Close the connection
        conn.close()

if __name__ == '__main__':
    create_admin_account()