#!/usr/bin/env python3
"""
WhatsApp Integration Test Script
Created by: Mohammed Hanzala

This script tests the WhatsApp integration functionality.
"""

import json
import os
from whatsapp_integration import WhatsAppReceiptGenerator

def test_credentials_loading():
    """Test if credentials are loaded properly"""
    print("🔍 Testing credentials loading...")
    
    generator = WhatsAppReceiptGenerator()
    
    print(f"Access Token: {'✅ Set' if generator.access_token != 'your_access_token_here' else '❌ Not set'}")
    print(f"Phone Number ID: {'✅ Set' if generator.phone_number_id != 'your_phone_number_id_here' else '❌ Not set'}")
    print(f"API Version: {generator.api_version}")
    print(f"Base URL: {generator.base_url}")
    
    return generator.access_token != 'your_access_token_here' and generator.phone_number_id != 'your_phone_number_id_here'

def test_database_connection():
    """Test database connection"""
    print("\n🗄️  Testing database connection...")
    
    generator = WhatsAppReceiptGenerator()
    connection = generator.connect_database()
    
    if connection:
        print("✅ Database connection successful!")
        connection.close()
        return True
    else:
        print("❌ Database connection failed!")
        return False

def test_sale_data_retrieval():
    """Test retrieving sale data from database"""
    print("\n📊 Testing sale data retrieval...")
    
    generator = WhatsAppReceiptGenerator()
    connection = generator.connect_database()
    
    if not connection:
        print("❌ Cannot test sale data retrieval - no database connection")
        return False
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM sales")
        result = cursor.fetchone()
        
        if result and result['count'] > 0:
            print(f"✅ Found {result['count']} sales in database")
            
            # Get first sale for testing
            cursor.execute("SELECT sale_id FROM sales LIMIT 1")
            sale = cursor.fetchone()
            if sale:
                print(f"✅ Test sale ID: {sale['sale_id']}")
                return True
        else:
            print("⚠️  No sales found in database")
            return False
            
    except Exception as e:
        print(f"❌ Error retrieving sale data: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def test_receipt_generation():
    """Test receipt image generation"""
    print("\n🖼️  Testing receipt image generation...")
    
    generator = WhatsAppReceiptGenerator()
    
    # Create sample sale data
    sample_sale = {
        'sale_id': 1,
        'sale_date': '2024-01-15 10:30:00',
        'customer_name': 'Test Customer',
        'customer_phone': '+1234567890',
        'quantity_sold': 2,
        'total_amount': 25.50,
        'doctor_name': 'Dr. Smith',
        'doctor_phone': '+0987654321',
        'medicine_name': 'Test Medicine',
        'unit_price': 12.75,
        'manufacturer': 'Test Pharma',
        'sold_by_name': 'Test Staff'
    }
    
    try:
        receipt_image = generator.generate_receipt_image(sample_sale)
        
        if receipt_image:
            print("✅ Receipt image generated successfully!")
            print(f"Image size: {len(receipt_image)} bytes")
            
            # Save test image
            with open('test_generated_receipt.png', 'wb') as f:
                f.write(receipt_image)
            print("✅ Test receipt saved as 'test_generated_receipt.png'")
            return True
        else:
            print("❌ Failed to generate receipt image")
            return False
            
    except Exception as e:
        print(f"❌ Error generating receipt: {e}")
        return False

def test_phone_number_formatting():
    """Test phone number formatting"""
    print("\n📱 Testing phone number formatting...")
    
    generator = WhatsAppReceiptGenerator()
    
    test_numbers = [
        '+1234567890',
        '1234567890',
        '+91 98765 43210',
        '9876543210',
        '+1 (555) 123-4567'
    ]
    
    for number in test_numbers:
        formatted = generator.format_phone_number(number)
        print(f"Original: {number} -> Formatted: {formatted}")
    
    print("✅ Phone number formatting test completed")
    return True

def test_whatsapp_api_connection():
    """Test WhatsApp API connection (if credentials are set)"""
    print("\n📡 Testing WhatsApp API connection...")
    
    generator = WhatsAppReceiptGenerator()
    
    if generator.access_token == 'your_access_token_here':
        print("⚠️  WhatsApp credentials not configured. Skipping API test.")
        print("   Please update whatsapp_credentials.json with your actual credentials.")
        return False
    
    try:
        import requests
        
        url = f"{generator.base_url}/{generator.phone_number_id}"
        headers = {
            'Authorization': f'Bearer {generator.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ WhatsApp API connection successful!")
            print(f"📱 Phone Number: {data.get('display_phone_number', 'N/A')}")
            print(f"🔢 Phone Number ID: {data.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ WhatsApp API connection failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp API connection error: {e}")
        return False

def run_complete_test():
    """Run all tests"""
    print("🧪 WhatsApp Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("Credentials Loading", test_credentials_loading),
        ("Database Connection", test_database_connection),
        ("Sale Data Retrieval", test_sale_data_retrieval),
        ("Receipt Generation", test_receipt_generation),
        ("Phone Number Formatting", test_phone_number_formatting),
        ("WhatsApp API Connection", test_whatsapp_api_connection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WhatsApp integration is ready.")
    elif passed >= total - 1:  # Allow one failure (usually API credentials)
        print("✅ Most tests passed! Integration is mostly ready.")
        print("   Just need to configure WhatsApp API credentials.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
    
    return passed, total

if __name__ == "__main__":
    run_complete_test() 