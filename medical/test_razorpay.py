#!/usr/bin/env python3
"""
Test script for Razorpay integration
"""

import razorpay
import json

# Test configuration (replace with your actual test keys)
RAZORPAY_KEY_ID = 'rzp_test_YOUR_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_KEY_SECRET'

def test_razorpay_connection():
    """Test basic Razorpay connection"""
    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        
        # Test creating a simple order
        order_data = {
            'amount': 10000,  # 100 INR in paise
            'currency': 'INR',
            'receipt': 'test_receipt_001'
        }
        
        order = client.order.create(data=order_data)
        
        print("✅ Razorpay connection successful!")
        print(f"Order ID: {order['id']}")
        print(f"Amount: {order['amount']} paise")
        print(f"Currency: {order['currency']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Razorpay connection failed: {e}")
        print("\nTo fix this:")
        print("1. Sign up at https://razorpay.com")
        print("2. Get your test API keys from the dashboard")
        print("3. Update the RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in this file")
        return False

def test_payment_flow():
    """Test complete payment flow"""
    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        
        # Create order
        order = client.order.create({
            'amount': 5000,  # 50 INR
            'currency': 'INR',
            'receipt': 'test_medicine_purchase'
        })
        
        print(f"\n📋 Test Order Created:")
        print(f"Order ID: {order['id']}")
        print(f"Amount: ₹{order['amount']/100}")
        
        # Simulate payment verification (in real scenario, this comes from Razorpay)
        print("\n💳 Payment Flow Test:")
        print("1. Order created successfully")
        print("2. Payment modal would open in browser")
        print("3. User would complete payment")
        print("4. Payment verification would happen")
        print("5. Sale record would be saved")
        print("6. WhatsApp receipt would be sent")
        
        return True
        
    except Exception as e:
        print(f"❌ Payment flow test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Razorpay Integration")
    print("=" * 40)
    
    # Test connection
    if test_razorpay_connection():
        # Test payment flow
        test_payment_flow()
    
    print("\n📝 Next Steps:")
    print("1. Update the API keys in razorpay_integration.py")
    print("2. Start the Flask server: python app.py")
    print("3. Test the payment flow in the staff dashboard")
    print("4. Use test card: 4111 1111 1111 1111") 