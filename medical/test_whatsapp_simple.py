#!/usr/bin/env python3
"""
Simple WhatsApp Integration Test
Tests only Twilio WhatsApp functionality
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from twilio_whatsapp_integration import TwilioWhatsAppReceiptSender
        print("✅ Twilio WhatsApp integration imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Twilio WhatsApp integration: {e}")
        return False
    
    try:
        from app import app
        print("✅ Flask app imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Flask app: {e}")
        return False
    
    return True

def test_twilio_client():
    """Test Twilio client initialization"""
    print("\n🔍 Testing Twilio client...")
    
    try:
        from twilio_whatsapp_integration import TwilioWhatsAppReceiptSender
        sender = TwilioWhatsAppReceiptSender()
        
        if sender.client:
            print("✅ Twilio client initialized successfully")
            print(f"   Account SID: {sender.account_sid[:10]}...")
            print(f"   From WhatsApp: {sender.from_whatsapp}")
            return True
        else:
            print("❌ Twilio client initialization failed")
            return False
    except Exception as e:
        print(f"❌ Error initializing Twilio client: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from twilio_whatsapp_integration import TwilioWhatsAppReceiptSender
        sender = TwilioWhatsAppReceiptSender()
        connection = sender.connect_database()
        
        if connection:
            print("✅ Database connection successful")
            connection.close()
            return True
        else:
            print("❌ Database connection failed")
            return False
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return False

def test_flask_routes():
    """Test if Flask routes are properly registered"""
    print("\n🔍 Testing Flask routes...")
    
    try:
        from app import app
        
        # Check if routes exist
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        
        required_routes = [
            '/api/send-receipt/<int:sale_id>',
            '/api/send-receipt-twilio/<int:sale_id>',
            '/api/twilio-status/<int:sale_id>',
            '/api/test-twilio-connection',
            '/api/whatsapp-stats'
        ]
        
        missing_routes = []
        for route in required_routes:
            if route not in routes:
                missing_routes.append(route)
        
        if not missing_routes:
            print("✅ All required WhatsApp routes are registered")
            return True
        else:
            print(f"❌ Missing routes: {missing_routes}")
            return False
    except Exception as e:
        print(f"❌ Error testing Flask routes: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 WhatsApp Integration Test (Twilio Only)")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_twilio_client,
        test_database_connection,
        test_flask_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WhatsApp integration is ready.")
        print("\n📱 Next steps:")
        print("1. Start the server: python app.py")
        print("2. Access admin dashboard: http://localhost:5000/admin_dashboard.html")
        print("3. Test WhatsApp functionality in staff dashboard")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 