from flask import Flask, request, jsonify, session, send_from_directory, url_for
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
import json
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Import WhatsApp integration
from whatsapp_integration import setup_whatsapp_routes
from twilio_whatsapp_integration import setup_twilio_whatsapp_routes
from razorpay_integration import setup_razorpay_routes

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'medicos_secret_key_2024'
CORS(app)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',  # Replace with your actual password
    'database': 'medicos_pharmacy'
}

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
GOOGLE_DRIVE_FOLDER_ID = '1HUQ_O8mSB0jrirZarLOy1ct8fYW1B-PE'  # Replace with your actual folder ID from Google Drive

def get_db_connection():
    """Create and return database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            
            # Create database if not exists
            cursor.execute("CREATE DATABASE IF NOT EXISTS medicos_pharmacy")
            cursor.execute("USE medicos_pharmacy")
            
            # Create tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS staff (
                    staff_id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    position VARCHAR(50) NOT NULL,
                    hire_date DATE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS medicines (
                    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
                    medicine_name VARCHAR(200) NOT NULL,
                    batch_number VARCHAR(50) UNIQUE NOT NULL,
                    expiry_date DATE NOT NULL,
                    date_of_purchase DATE NOT NULL,
                    quantity_available INT NOT NULL DEFAULT 0,
                    unit_price DECIMAL(10,2) NOT NULL,
                    manufacturer VARCHAR(200),
                    category VARCHAR(100),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_by INT,
                    FOREIGN KEY (created_by) REFERENCES admins(admin_id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    sale_id INT PRIMARY KEY AUTO_INCREMENT,
                    medicine_id INT NOT NULL,
                    quantity_sold INT NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    doctor_name VARCHAR(100),
                    prescription_photo_url VARCHAR(500),
                    customer_name VARCHAR(100),
                    customer_phone VARCHAR(20),
                    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    sold_by INT NOT NULL,
                    rate_per_tablet DECIMAL(10,2),
                    payment_id VARCHAR(100),
                    order_id VARCHAR(100),
                    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
                    payment_method VARCHAR(50) DEFAULT 'razorpay',
                    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
                    FOREIGN KEY (sold_by) REFERENCES staff(staff_id)
                )
            """)
            
            # Insert default admins if not exists
            cursor.execute("SELECT COUNT(*) FROM admins")
            if cursor.fetchone()[0] == 0:
                admin_password = generate_password_hash('admin123')
                
                # Insert all admin accounts
                admin_data = [
                    ('admin1', admin_password, 'MOHAMMED HANIF (CEO)', 'hanif@medicos.com', '+91 9110232172'),
                    ('admin2', admin_password, 'MOHAMMED HUZEFA', 'huzefa@medicos.com', '+91 9741690949'),
                    ('admin3', admin_password, 'MOHAMMED HANNAN', 'hannan@medicos.com', '+91 9876543210'),
                    ('admin4', admin_password, 'ABDUL SUBHAN', 'subhan@medicos.com', '+91 9876543211'),
                    ('admin5', admin_password, 'NALINI KHARVI', 'nalini@medicos.com', '+91 9876543212'),
                    ('admin6', admin_password, 'SUPRITA', 'suprita@medicos.com', '+91 9876543213'),
                    ('admin7', admin_password, 'MOHAMMED HANZALA', 'hanzala@medicos.com', '+91 9876543214')
                ]
                
                for admin in admin_data:
                    cursor.execute("""
                        INSERT INTO admins (username, password, full_name, email, phone) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, admin)
            
            # Update existing admin passwords to be properly hashed
            admin_password = generate_password_hash('admin123')
            for i in range(1, 8):
                cursor.execute("UPDATE admins SET password = %s WHERE username = %s", (admin_password, f'admin{i}'))
            
            # Insert current staff if not exists
            cursor.execute("SELECT COUNT(*) FROM staff")
            if cursor.fetchone()[0] == 0:
                staff_password = generate_password_hash('staff123')
                
                # Insert all current staff members
                staff_data = [
                    ('mohammed.huzefa', staff_password, 'MOHAMMED HUZEFA', 'huzefa@medicos.com', '+91 9741690949', 'Purchase & Sales Manager', '2020-01-15'),
                    ('nalini.kharvi', staff_password, 'MS. NALINI KHARVI', 'nalini@medicos.com', '+91 9876543215', 'Purchasing Executive', '2022-03-01'),
                    ('mohammed.hannan', staff_password, 'MR. MOHAMMED HANNAN', 'hannan@medicos.com', '+91 9876543216', 'Associate Manager', '2021-06-15'),
                    ('abdul.subhan', staff_password, 'MR. ABDUL SUBHAN', 'subhan@medicos.com', '+91 9876543217', 'Junior Executive', '2022-09-01'),
                    ('suprita', staff_password, 'MS. SUPRITA', 'suprita@medicos.com', '+91 9876543218', 'Nursing Department Head', '2021-12-01'),
                    ('mohammed.hanzala', staff_password, 'MR. MOHAMMED HANZALA', 'hanzala@medicos.com', '+91 9876543219', 'Software Engineer & Sales Head', '2020-08-01')
                ]
                
                for staff in staff_data:
                    cursor.execute("""
                        INSERT INTO staff (username, password, full_name, email, phone, position, hire_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, staff)
            
            # Update existing staff passwords to be properly hashed
            staff_password = generate_password_hash('staff123')
            staff_usernames = ['mohammed.huzefa', 'nalini.kharvi', 'mohammed.hannan', 'abdul.subhan', 'suprita', 'mohammed.hanzala']
            for username in staff_usernames:
                cursor.execute("UPDATE staff SET password = %s WHERE username = %s", (staff_password, username))
            
            # Add sample medicines if not exists
            cursor.execute("SELECT COUNT(*) FROM medicines")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO medicines (medicine_name, batch_number, expiry_date, date_of_purchase, 
                                         quantity_available, unit_price, manufacturer, category, description, created_by)
                    VALUES 
                    ('Paracetamol 500mg', 'BATCH001', '2025-12-31', '2024-01-15', 100, 5.99, 'Johnson & Johnson', 'Pain Relief', 'Fever and pain relief tablets', 1),
                    ('Ibuprofen 400mg', 'BATCH002', '2025-10-31', '2024-02-20', 75, 7.50, 'Pfizer', 'Pain Relief', 'Anti-inflammatory pain relief', 1),
                    ('Amoxicillin 250mg', 'BATCH003', '2025-08-31', '2024-03-10', 50, 12.99, 'GlaxoSmithKline', 'Antibiotics', 'Broad-spectrum antibiotic', 1),
                    ('Omeprazole 20mg', 'BATCH004', '2025-11-30', '2024-01-25', 60, 15.75, 'AstraZeneca', 'Gastric', 'Acid reflux medication', 1),
                    ('Cetirizine 10mg', 'BATCH005', '2025-09-30', '2024-02-15', 80, 8.25, 'Merck', 'Allergy', 'Antihistamine for allergies', 1)
                """)
            
            connection.commit()
            cursor.close()
            connection.close()
            print("Database initialized successfully!")
            
    except Error as e:
        print(f"Error initializing database: {e}")

# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type')  # 'admin' or 'staff'
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        if user_type == 'admin':
            cursor.execute("SELECT * FROM admins WHERE username = %s AND is_active = TRUE", (username,))
        else:
            cursor.execute("SELECT * FROM staff WHERE username = %s AND is_active = TRUE", (username,))
        
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password'], password):
            # Update last login
            if user_type == 'admin':
                cursor.execute("UPDATE admins SET last_login = NOW() WHERE admin_id = %s", (user['admin_id'],))
            else:
                cursor.execute("UPDATE staff SET last_login = NOW() WHERE staff_id = %s", (user['staff_id'],))
            
            connection.commit()
            
            session['user_id'] = user['admin_id'] if user_type == 'admin' else user['staff_id']
            session['user_type'] = user_type
            session['username'] = user['username']
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user['admin_id'] if user_type == 'admin' else user['staff_id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user['email'],
                    'type': user_type
                }
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/register', methods=['POST'])
def register_staff():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')
        position = data.get('position')
        hire_date = data.get('hire_date')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT COUNT(*) FROM staff WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Hash password and insert new staff
        hashed_password = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO staff (username, password, full_name, email, phone, position, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (username, hashed_password, full_name, email, phone, position, hire_date))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Staff registered successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/current-staff', methods=['GET'])
def get_current_staff():
    """Get current logged-in staff member information"""
    try:
        if 'user_id' not in session or 'user_type' not in session or session['user_type'] != 'staff':
            return jsonify({'error': 'Not logged in as staff'}), 401
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT staff_id, username, full_name, email, phone, position, hire_date
            FROM staff 
            WHERE staff_id = %s
        """, (session['user_id'],))
        
        staff = cursor.fetchone()
        
        if not staff:
            return jsonify({'error': 'Staff not found'}), 404
        
        # Convert dates to strings for JSON serialization
        staff['hire_date'] = staff['hire_date'].isoformat() if staff['hire_date'] else None
        
        cursor.close()
        connection.close()
        
        return jsonify({'staff': staff})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/staff', methods=['GET'])
def get_staff():
    """Get all staff members"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT staff_id, username, full_name, email, phone, position, hire_date, 
                   created_at, last_login, is_active
            FROM staff 
            ORDER BY created_at DESC
        """)
        
        staff_members = cursor.fetchall()
        
        # Convert dates to strings for JSON serialization
        for staff in staff_members:
            staff['hire_date'] = staff['hire_date'].isoformat() if staff['hire_date'] else None
            staff['created_at'] = staff['created_at'].isoformat() if staff['created_at'] else None
            staff['last_login'] = staff['last_login'].isoformat() if staff['last_login'] else None
        
        cursor.close()
        connection.close()
        
        return jsonify({'staff': staff_members})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/staff/<int:staff_id>', methods=['PUT'])
def update_staff(staff_id):
    """Update staff member"""
    try:
        if 'user_type' not in session or session['user_type'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if staff exists
        cursor.execute("SELECT COUNT(*) FROM staff WHERE staff_id = %s", (staff_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Staff member not found'}), 404
        
        # Update staff
        cursor.execute("""
            UPDATE staff 
            SET full_name = %s, email = %s, phone = %s, position = %s, is_active = %s
            WHERE staff_id = %s
        """, (data.get('full_name'), data.get('email'), data.get('phone'), 
              data.get('position'), data.get('is_active', True), staff_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Staff updated successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/staff/<int:staff_id>', methods=['DELETE'])
def delete_staff(staff_id):
    """Delete staff member (soft delete)"""
    try:
        if 'user_type' not in session or session['user_type'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if staff exists
        cursor.execute("SELECT COUNT(*) FROM staff WHERE staff_id = %s", (staff_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Staff member not found'}), 404
        
        # Soft delete staff
        cursor.execute("UPDATE staff SET is_active = FALSE WHERE staff_id = %s", (staff_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Staff deleted successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# Medicine CRUD operations (Admin only)
@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT m.*, a.full_name as created_by_name 
            FROM medicines m 
            LEFT JOIN admins a ON m.created_by = a.admin_id 
            ORDER BY m.created_at DESC
        """)
        
        medicines = cursor.fetchall()
        
        # Convert dates to strings for JSON serialization
        for medicine in medicines:
            medicine['expiry_date'] = medicine['expiry_date'].isoformat() if medicine['expiry_date'] else None
            medicine['date_of_purchase'] = medicine['date_of_purchase'].isoformat() if medicine['date_of_purchase'] else None
            medicine['created_at'] = medicine['created_at'].isoformat() if medicine['created_at'] else None
            medicine['updated_at'] = medicine['updated_at'].isoformat() if medicine['updated_at'] else None
        
        cursor.close()
        connection.close()
        
        return jsonify({'medicines': medicines})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/medicines/<int:medicine_id>', methods=['GET'])
def get_medicine(medicine_id):
    """Get a single medicine by ID"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT medicine_id, medicine_name, batch_number, expiry_date, date_of_purchase,
                   quantity_available, unit_price, manufacturer, category, description
            FROM medicines 
            WHERE medicine_id = %s
        """, (medicine_id,))
        
        medicine = cursor.fetchone()
        
        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404
        
        # Convert dates to strings for JSON serialization
        medicine['expiry_date'] = medicine['expiry_date'].isoformat() if medicine['expiry_date'] else None
        medicine['date_of_purchase'] = medicine['date_of_purchase'].isoformat() if medicine['date_of_purchase'] else None
        
        cursor.close()
        connection.close()
        
        return jsonify(medicine)
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/medicines', methods=['POST'])
def add_medicine():
    try:
        if 'user_type' not in session or session['user_type'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        medicine_name = data.get('medicine_name')
        batch_number = data.get('batch_number')
        expiry_date = data.get('expiry_date')
        date_of_purchase = data.get('date_of_purchase')
        quantity_available = data.get('quantity_available')
        unit_price = data.get('unit_price')
        manufacturer = data.get('manufacturer')
        category = data.get('category')
        description = data.get('description')
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if batch number already exists
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE batch_number = %s", (batch_number,))
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'Batch number already exists'}), 400
        
        cursor.execute("""
            INSERT INTO medicines (medicine_name, batch_number, expiry_date, date_of_purchase,
                                 quantity_available, unit_price, manufacturer, category, description, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (medicine_name, batch_number, expiry_date, date_of_purchase, quantity_available,
              unit_price, manufacturer, category, description, session['user_id']))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Medicine added successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/medicines/<int:medicine_id>', methods=['PUT'])
def update_medicine(medicine_id):
    try:
        if 'user_type' not in session or session['user_type'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if medicine exists
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE medicine_id = %s", (medicine_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Medicine not found'}), 404
        
        # Update medicine
        cursor.execute("""
            UPDATE medicines 
            SET medicine_name = %s, batch_number = %s, expiry_date = %s, date_of_purchase = %s,
                quantity_available = %s, unit_price = %s, manufacturer = %s, category = %s, description = %s
            WHERE medicine_id = %s
        """, (data.get('medicine_name'), data.get('batch_number'), data.get('expiry_date'),
              data.get('date_of_purchase'), data.get('quantity_available'), data.get('unit_price'),
              data.get('manufacturer'), data.get('category'), data.get('description'), medicine_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Medicine updated successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/medicines/<int:medicine_id>', methods=['DELETE'])
def delete_medicine(medicine_id):
    try:
        if 'user_type' not in session or session['user_type'] != 'admin':
            return jsonify({'error': 'Unauthorized'}), 401
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if medicine exists
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE medicine_id = %s", (medicine_id,))
        if cursor.fetchone()[0] == 0:
            return jsonify({'error': 'Medicine not found'}), 404
        
        # Delete medicine
        cursor.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Medicine deleted successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# Sales operations (Staff only)
@app.route('/api/sales', methods=['GET'])
def get_sales():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, m.medicine_name, st.full_name as sold_by_name
            FROM sales s
            JOIN medicines m ON s.medicine_id = m.medicine_id
            JOIN staff st ON s.sold_by = st.staff_id
            ORDER BY s.sale_date DESC
        """)
        
        sales = cursor.fetchall()
        
        # Convert dates to strings for JSON serialization
        for sale in sales:
            sale['sale_date'] = sale['sale_date'].isoformat() if sale['sale_date'] else None
        
        cursor.close()
        connection.close()
        
        return jsonify({'sales': sales})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@app.route('/api/sales', methods=['POST'])
def add_sale():
    try:
        if 'user_type' not in session or session['user_type'] != 'staff':
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        medicine_id = data.get('medicine_id')
        quantity_sold = data.get('quantity_sold')
        doctor_name = data.get('doctor_name')
        rate_per_tablet = data.get('rate_per_tablet')
        total_amount = data.get('total_amount')
        prescription_photo_url = data.get('prescription_photo_url')
        customer_name = data.get('customer_name')
        customer_phone = data.get('customer_phone')
        sold_by = session.get('user_id')  # Get staff ID from session
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Check if medicine exists and has sufficient quantity
        cursor.execute("SELECT quantity_available, unit_price FROM medicines WHERE medicine_id = %s", (medicine_id,))
        medicine = cursor.fetchone()
        
        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404
        
        if medicine[0] < quantity_sold:
            return jsonify({'error': 'Insufficient quantity available'}), 400
        
        unit_price = medicine[1]
        # Use provided total_amount or calculate from rate_per_tablet
        if total_amount is None and rate_per_tablet:
            total_amount = quantity_sold * rate_per_tablet
        elif total_amount is None:
            total_amount = quantity_sold * unit_price
        
        # Insert sale record
        cursor.execute("""
            INSERT INTO sales (medicine_id, quantity_sold, unit_price, total_amount,
                             doctor_name, prescription_photo_url,
                             customer_name, customer_phone, sold_by, rate_per_tablet)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (medicine_id, quantity_sold, unit_price, total_amount, doctor_name,
              prescription_photo_url, customer_name, customer_phone, sold_by, rate_per_tablet))
        
        # Update medicine quantity
        cursor.execute("""
            UPDATE medicines 
            SET quantity_available = quantity_available - %s
            WHERE medicine_id = %s
        """, (quantity_sold, medicine_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({'success': True, 'message': 'Sale recorded successfully'})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# Google Drive upload for prescriptions
@app.route('/api/upload-prescription', methods=['POST'])
def upload_prescription():
    try:
        if 'prescription' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['prescription']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save file locally
        uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        filename = secure_filename(file.filename)
        save_path = os.path.join(uploads_dir, filename)
        file.save(save_path)
        
        # Upload to Google Drive if credentials are available
        drive_url = None
        try:
            if os.path.exists(SERVICE_ACCOUNT_FILE):
                credentials = service_account.Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
                service = build('drive', 'v3', credentials=credentials)
                
                # Create file metadata
                file_metadata = {
                    'name': filename,
                    'parents': [GOOGLE_DRIVE_FOLDER_ID]
                }
                
                # Create media upload
                media = MediaFileUpload(save_path, resumable=True)
                
                # Upload file
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id,webViewLink'
                ).execute()
                
                drive_url = file.get('webViewLink')
                print(f"✅ File uploaded to Google Drive: {drive_url}")
            else:
                print("⚠️ Google Drive credentials not found, skipping Drive upload")
        except Exception as drive_error:
            print(f"⚠️ Google Drive upload failed: {drive_error}")
        
        # Return the local file URL and Drive URL if available
        file_url = url_for('uploaded_file', filename=filename, _external=True)
        return jsonify({
            'success': True, 
            'file_url': file_url,
            'drive_url': drive_url
        })
    except Exception as e:
        return jsonify({'error': f'Upload error: {str(e)}'}), 500

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(uploads_dir, filename)

# Dashboard statistics
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        
        # Get total medicines
        cursor.execute("SELECT COUNT(*) FROM medicines")
        total_medicines = cursor.fetchone()[0]
        
        # Get low stock medicines (less than 50)
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE quantity_available < 50")
        low_stock = cursor.fetchone()[0]
        
        # Get expiring medicines (within 30 days)
        cursor.execute("SELECT COUNT(*) FROM medicines WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)")
        expiring_soon = cursor.fetchone()[0]
        
        # Get total sales today
        cursor.execute("SELECT COUNT(*) FROM sales WHERE DATE(sale_date) = CURDATE()")
        sales_today = cursor.fetchone()[0]
        
        # Get total revenue today
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM sales WHERE DATE(sale_date) = CURDATE()")
        revenue_today = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return jsonify({
            'total_medicines': total_medicines,
            'low_stock': low_stock,
            'expiring_soon': expiring_soon,
            'sales_today': sales_today,
            'revenue_today': float(revenue_today)
        })
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# Available medicines for staff selection
@app.route('/api/medicines/available', methods=['GET'])
def get_available_medicines():
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT medicine_id, medicine_name, batch_number, quantity_available, unit_price
            FROM medicines 
            WHERE quantity_available > 0 AND expiry_date > CURDATE()
            ORDER BY medicine_name
        """)
        
        medicines = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return jsonify({'medicines': medicines})
        
    except Error as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500

# Serve static HTML files
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')



@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Setup WhatsApp routes
    setup_whatsapp_routes(app)
    setup_twilio_whatsapp_routes(app)
    setup_razorpay_routes(app)
    
    print("🚀 MEDicos Pharmacy Management System Backend")
    print("📊 Database initialized with sample data")
    print("🔐 Default admin credentials: admin1/admin123 or admin2/admin123")
    print("👥 Sample staff credentials: staff1/staff123, staff2/staff123, staff3/staff123")
    print("📱 WhatsApp receipt integration enabled (Facebook API + Twilio)")
    print("💳 Razorpay payment integration enabled")
    print("🌐 Server starting on http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)