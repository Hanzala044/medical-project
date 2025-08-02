from flask import Flask, request, jsonify, session, send_from_directory, url_for
from flask_cors import CORS
import os
import json
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Import database configuration
from database_config import get_db_connection, get_cursor, execute_query, fetch_all, fetch_one, get_last_row_id

# Import WhatsApp integration
from twilio_whatsapp_integration import setup_twilio_whatsapp_routes
from razorpay_integration import setup_razorpay_routes

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'medicos_secret_key_2024'
CORS(app)

# Google Drive API configuration
SCOPES = ['https://www.googleapis.com/auth/drive.file']
SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), 'credentials.json')
GOOGLE_DRIVE_FOLDER_ID = '1HUQ_O8mSB0jrirZarLOy1ct8fYW1B-PE'  # Replace with your actual folder ID from Google Drive

# Database connection is now handled by database_config.py

def init_database():
    """Initialize database tables if they don't exist"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = get_cursor(connection)
            
            # Read and execute PostgreSQL schema
            with open('postgresql_schema.sql', 'r') as file:
                schema_sql = file.read()
                # Split by semicolon and execute each statement
                statements = schema_sql.split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement and not statement.startswith('--'):
                        execute_query(cursor, statement)
            
            connection.commit()
            cursor.close()
            connection.close()
            print("✅ Database initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
            
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

# WhatsApp integration (Twilio only)
setup_twilio_whatsapp_routes(app)

# Unified WhatsApp endpoint (Twilio only)
@app.route('/api/send-receipt/<int:sale_id>', methods=['POST'])
def send_receipt_unified(sale_id):
    """Send receipt via Twilio WhatsApp"""
    try:
        from twilio_whatsapp_integration import TwilioWhatsAppReceiptSender
        sender = TwilioWhatsAppReceiptSender()
        result = sender.send_receipt(sale_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# WhatsApp Management API Endpoints
@app.route('/api/test-twilio-connection', methods=['POST'])
def test_twilio_connection():
    try:
        from twilio_whatsapp_integration import TwilioWhatsAppReceiptSender
        sender = TwilioWhatsAppReceiptSender()
        
        # Test basic client initialization
        if sender.client:
            return jsonify({
                "success": True,
                "message": "Twilio client initialized successfully",
                "account_sid": sender.account_sid[:10] + "..." if sender.account_sid else "Not set"
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to initialize Twilio client"
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Twilio connection error: {str(e)}"
        }), 500

@app.route('/api/whatsapp-stats', methods=['GET'])
def get_whatsapp_stats():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get Twilio receipts count
        cursor.execute("""
            SELECT COUNT(*) as count FROM sales 
            WHERE whatsapp_receipt_sent = TRUE AND whatsapp_provider = 'twilio'
        """)
        twilio_receipts = cursor.fetchone()['count']
        
        # Get total receipts (all providers)
        cursor.execute("""
            SELECT COUNT(*) as count FROM sales 
            WHERE whatsapp_receipt_sent = TRUE
        """)
        total_receipts = cursor.fetchone()['count']
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "success": True,
            "twilio_receipts": twilio_receipts,
            "total_receipts": total_receipts
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error getting WhatsApp stats: {str(e)}"
        }), 500

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
    
    # Setup routes
    setup_razorpay_routes(app)
    
    print("🚀 MEDicos Pharmacy Management System Backend")
    print("📊 Database initialized with sample data")
    print("🔐 Default admin credentials: admin1/admin123 or admin2/admin123")
    print("👥 Sample staff credentials: staff1/staff123, staff2/staff123, staff3/staff123")
    print("📱 WhatsApp receipt integration enabled (Twilio)")
    print("💳 Razorpay payment integration enabled")
    print("🌐 Server starting on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)