import razorpay
import hashlib
import hmac
import json
from flask import request, jsonify, session
import mysql.connector
from datetime import datetime

# Razorpay configuration
# Your actual Razorpay test keys
RAZORPAY_KEY_ID = 'rzp_test_zPJXCKox2LJ0s0'
RAZORPAY_KEY_SECRET = '54as6NgzRsakRww7nuHW8naU'

# Set to False to use real Razorpay API
USE_MOCK_RAZORPAY = False

# Initialize Razorpay client
if USE_MOCK_RAZORPAY:
    # Mock client for testing without real keys
    class MockRazorpayClient:
        def __init__(self, auth):
            self.key_id, self.key_secret = auth
            print(f"🔧 Using Mock Razorpay Client (Key ID: {self.key_id})")
        
        def order(self):
            return self
        
        def create(self, data):
            order_id = f"order_mock_{int(datetime.now().timestamp())}"
            return {
                'id': order_id,
                'amount': data['amount'],
                'currency': data['currency'],
                'receipt': data.get('receipt', 'mock_receipt')
            }
        
        def utility(self):
            return self
        
        def verify_payment_signature(self, data):
            # Mock verification - always returns True
            print("🔧 Mock payment signature verification")
            return True
        
        def payment(self):
            return self
        
        def fetch(self, payment_id):
            return {
                'id': payment_id,
                'status': 'captured',
                'amount': 5000,
                'currency': 'INR'
            }

    client = MockRazorpayClient(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    # Real Razorpay client
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'medicos_pharmacy'
}

def setup_razorpay_routes(app):
    """Setup Razorpay payment routes"""
    
    @app.route('/api/create-razorpay-order', methods=['POST'])
    def create_razorpay_order():
        """Create a new Razorpay order"""
        try:
            data = request.get_json()
            amount = data.get('amount')  # Amount in paise
            currency = data.get('currency', 'INR')
            receipt = data.get('receipt')
            notes = data.get('notes', {})
            
            # Create order
            order_data = {
                'amount': amount,
                'currency': currency,
                'receipt': receipt,
                'notes': notes
            }
            
            order = client.order.create(data=order_data)
            
            return jsonify({
                'success': True,
                'id': order['id'],
                'amount': order['amount'],
                'currency': order['currency'],
                'key_id': RAZORPAY_KEY_ID
            })
            
        except Exception as e:
            print(f"Error creating Razorpay order: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/verify-razorpay-payment', methods=['POST'])
    def verify_razorpay_payment():
        """Verify Razorpay payment and save sale record"""
        try:
            data = request.get_json()
            payment_id = data.get('payment_id')
            order_id = data.get('order_id')
            signature = data.get('signature')
            form_data = data.get('form_data', {})
            
            # Get current staff ID from session
            sold_by = session.get('user_id', 1)  # Default to 1 if not in session
            
            # Verify payment signature
            try:
                client.utility.verify_payment_signature({
                    'razorpay_payment_id': payment_id,
                    'razorpay_order_id': order_id,
                    'razorpay_signature': signature
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': 'Payment signature verification failed'
                }), 400
            
            # Get payment details
            payment = client.payment.fetch(payment_id)
            
            if payment['status'] != 'captured':
                return jsonify({
                    'success': False,
                    'error': 'Payment not completed'
                }), 400
            
            # Save sale record to database
            sale_id = save_sale_record(form_data, payment_id, order_id, sold_by)
            
            if sale_id:
                return jsonify({
                    'success': True,
                    'sale_id': sale_id,
                    'payment_id': payment_id,
                    'message': 'Payment verified and sale recorded successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to save sale record'
                }), 500
                
        except Exception as e:
            print(f"Error verifying payment: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

def save_sale_record(form_data, payment_id, order_id, sold_by=1):
    """Save sale record to database"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # sold_by is now passed as parameter from the calling function
        
        # Get medicine details to get unit_price
        medicine_query = "SELECT unit_price FROM medicines WHERE medicine_id = %s"
        cursor.execute(medicine_query, (form_data.get('medicine_id'),))
        medicine_result = cursor.fetchone()
        unit_price = medicine_result[0] if medicine_result else form_data.get('rate_per_tablet', 0)
        
        # Insert sale record
        insert_query = """
        INSERT INTO sales (
            medicine_id, quantity_sold, unit_price, total_amount, sale_date, 
            customer_name, customer_phone, doctor_name, sold_by,
            payment_id, order_id, rate_per_tablet
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        values = (
            form_data.get('medicine_id'),
            form_data.get('quantity_sold'),
            unit_price,
            form_data.get('total_amount'),
            datetime.now(),
            form_data.get('customer_name'),
            form_data.get('customer_phone'),
            form_data.get('doctor_name'),
            sold_by,
            payment_id,
            order_id,
            form_data.get('rate_per_tablet')
        )
        
        cursor.execute(insert_query, values)
        sale_id = cursor.lastrowid
        
        # Update medicine stock
        update_stock_query = """
        UPDATE medicines 
        SET quantity_available = quantity_available - %s 
        WHERE medicine_id = %s
        """
        cursor.execute(update_stock_query, (form_data.get('quantity_sold'), form_data.get('medicine_id')))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return sale_id
        
    except Exception as e:
        print(f"Error saving sale record: {e}")
        return None

def generate_payment_receipt(sale_data, payment_data):
    """Generate payment receipt text for WhatsApp"""
    receipt_text = f"""
🏥 *MEDicos Pharmacy - Payment Receipt*

📅 Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
💰 Payment ID: {payment_data.get('payment_id', 'N/A')}

👤 *Customer Details:*
Name: {sale_data.get('customer_name', 'N/A')}
Phone: {sale_data.get('customer_phone', 'N/A')}

💊 *Medicine Details:*
Quantity: {sale_data.get('quantity_sold', 'N/A')} tablets
Rate per Tablet: ₹{sale_data.get('rate_per_tablet', 'N/A')}
Total Amount: ₹{sale_data.get('total_amount', 'N/A')}

💳 *Payment Status:* ✅ PAID
Payment Method: Razorpay

🏥 *MEDicos Pharmacy*
Thank you for your purchase!
    """
    return receipt_text.strip() 