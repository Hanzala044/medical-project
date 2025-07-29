#!/usr/bin/env python3
"""
Test script for the Medical Chatbot API
Run this script to test the chatbot functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5001/api/chatbot"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health Check Passed")
            print(f"   Status: {data['status']}")
            print(f"   Services: {data['services']}")
            return True
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        return False

def test_medicine_search():
    """Test medicine search functionality"""
    print("\n🔍 Testing Medicine Search...")
    
    test_medicines = ["paracetamol", "ibuprofen", "amoxicillin", "nonexistent_medicine"]
    
    for medicine in test_medicines:
        try:
            response = requests.get(f"{BASE_URL}/medicines", params={"q": medicine})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Medicine Search for '{medicine}': Success")
                if data.get('medicine_info'):
                    info = data['medicine_info']
                    if 'generic_name' in info:
                        print(f"   Generic Name: {info['generic_name']}")
                    if 'uses' in info:
                        print(f"   Uses: {', '.join(info['uses'])}")
                else:
                    print(f"   No information found")
            else:
                print(f"❌ Medicine Search for '{medicine}': Failed ({response.status_code})")
        except Exception as e:
            print(f"❌ Medicine Search Error for '{medicine}': {e}")

def test_chat_functionality():
    """Test chat functionality"""
    print("\n🔍 Testing Chat Functionality...")
    
    test_messages = [
        "What is paracetamol used for?",
        "What are the side effects of ibuprofen?",
        "How much amoxicillin should I take?",
        "What is the dosage for aspirin?",
        "Tell me about vitamin C"
    ]
    
    for message in test_messages:
        try:
            print(f"\n📝 Testing: '{message}'")
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Chat Response: Success")
                print(f"   Response: {data['response'][:100]}...")
                if data.get('medicine_info'):
                    print(f"   Medicine Info: Available")
                print(f"   Timestamp: {data['timestamp']}")
            else:
                print(f"❌ Chat Response: Failed ({response.status_code})")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Chat Error: {e}")
        
        # Small delay between requests
        time.sleep(1)

def test_chat_history():
    """Test chat history functionality"""
    print("\n🔍 Testing Chat History...")
    try:
        response = requests.get(f"{BASE_URL}/history")
        if response.status_code == 200:
            data = response.json()
            history = data.get('history', [])
            print(f"✅ Chat History: Success")
            print(f"   Messages in history: {len(history)}")
            if history:
                latest = history[-1]
                print(f"   Latest message: {latest.get('user_message', 'N/A')}")
        else:
            print(f"❌ Chat History: Failed ({response.status_code})")
    except Exception as e:
        print(f"❌ Chat History Error: {e}")

def test_error_handling():
    """Test error handling"""
    print("\n🔍 Testing Error Handling...")
    
    # Test empty message
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": ""},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            print("✅ Empty message handling: Correct")
        else:
            print(f"❌ Empty message handling: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Empty message test error: {e}")
    
    # Test missing message parameter
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 400:
            print("✅ Missing message parameter handling: Correct")
        else:
            print(f"❌ Missing message parameter handling: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Missing message parameter test error: {e}")
    
    # Test invalid medicine search
    try:
        response = requests.get(f"{BASE_URL}/medicines")
        if response.status_code == 400:
            print("✅ Missing query parameter handling: Correct")
        else:
            print(f"❌ Missing query parameter handling: Expected 400, got {response.status_code}")
    except Exception as e:
        print(f"❌ Missing query parameter test error: {e}")

def test_performance():
    """Test performance with multiple requests"""
    print("\n🔍 Testing Performance...")
    
    start_time = time.time()
    successful_requests = 0
    total_requests = 5
    
    for i in range(total_requests):
        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json={"message": f"Test message {i+1}"},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                successful_requests += 1
            time.sleep(0.5)  # Small delay
        except Exception as e:
            print(f"❌ Performance test error: {e}")
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"✅ Performance Test Results:")
    print(f"   Total requests: {total_requests}")
    print(f"   Successful requests: {successful_requests}")
    print(f"   Duration: {duration:.2f} seconds")
    print(f"   Average response time: {duration/total_requests:.2f} seconds")
    print(f"   Success rate: {(successful_requests/total_requests)*100:.1f}%")

def main():
    """Run all tests"""
    print("🚀 Starting Medical Chatbot Tests")
    print("=" * 50)
    
    # Check if server is running
    print("🔍 Checking if chatbot server is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Chatbot server is running")
        else:
            print("❌ Chatbot server is not responding correctly")
            print("   Please start the chatbot server first:")
            print("   python chatbot_api.py")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to chatbot server")
        print("   Please start the chatbot server first:")
        print("   python chatbot_api.py")
        return
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return
    
    # Run tests
    test_health_check()
    test_medicine_search()
    test_chat_functionality()
    test_chat_history()
    test_error_handling()
    test_performance()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")

if __name__ == "__main__":
    main() 