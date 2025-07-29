#!/usr/bin/env python3
"""
Test script for MEDicos Medical Chatbot Initialization
This script tests the chatbot setup and identifies any issues
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

def test_chatbot_api():
    """Test the chatbot API endpoints"""
    print("🔍 Testing Chatbot API...")
    
    base_url = "http://localhost:5001/api/chatbot"
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test 2: Chat Endpoint
    print("\n2️⃣ Testing Chat Endpoint...")
    try:
        test_message = "What is paracetamol used for?"
        response = requests.post(
            f"{base_url}/chat",
            json={"message": test_message},
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working")
            print(f"   Response received: {len(data.get('response', ''))} characters")
            if data.get('medicine_info'):
                print("   Medicine info included")
            else:
                print("   No medicine info (normal for general questions)")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat endpoint error: {e}")
        return False
    
    # Test 3: Medicine Search
    print("\n3️⃣ Testing Medicine Search...")
    try:
        response = requests.get(f"{base_url}/medicines?q=paracetamol", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Medicine search working")
            if data.get('medicine_info'):
                print("   Medicine info found")
            else:
                print("   No medicine info found")
        else:
            print(f"❌ Medicine search failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Medicine search error: {e}")
    
    # Test 4: Chat History
    print("\n4️⃣ Testing Chat History...")
    try:
        response = requests.get(f"{base_url}/history", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat history endpoint working")
            history_count = len(data.get('history', []))
            print(f"   History entries: {history_count}")
        else:
            print(f"❌ Chat history failed: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Chat history error: {e}")
    
    return True

def test_frontend_integration():
    """Test frontend chatbot integration"""
    print("\n🔍 Testing Frontend Integration...")
    
    # Check if chatbot.js exists
    if not os.path.exists("js/chatbot.js"):
        print("❌ chatbot.js not found in js/ directory")
        return False
    
    print("✅ chatbot.js file found")
    
    # Check if chatbot is included in HTML files
    html_files = ["index.html", "about.html", "gallery.html"]
    chatbot_included = []
    
    for html_file in html_files:
        if os.path.exists(html_file):
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if 'js/chatbot.js' in content:
                        chatbot_included.append(html_file)
                        print(f"✅ {html_file}: chatbot.js included")
                    else:
                        print(f"⚠️ {html_file}: chatbot.js not included")
            except Exception as e:
                print(f"❌ Error reading {html_file}: {e}")
    
    return len(chatbot_included) > 0

def test_environment():
    """Test environment setup"""
    print("\n🔍 Testing Environment...")
    
    # Check .env file
    if os.path.exists(".env"):
        print("✅ .env file found")
        try:
            with open(".env", 'r') as f:
                env_content = f.read()
                if "OPENAI_API_KEY" in env_content:
                    print("✅ OPENAI_API_KEY found in .env")
                else:
                    print("⚠️ OPENAI_API_KEY not found in .env")
                
                if "GOOGLE_API_KEY" in env_content:
                    print("✅ GOOGLE_API_KEY found in .env")
                else:
                    print("⚠️ GOOGLE_API_KEY not found in .env")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    else:
        print("⚠️ .env file not found")
    
    # Check requirements
    if os.path.exists("requirements.txt"):
        print("✅ requirements.txt found")
        required_packages = [
            "flask", "flask-cors", "openai", "google-generativeai", 
            "requests", "python-dotenv"
        ]
        
        try:
            with open("requirements.txt", 'r') as f:
                content = f.read()
                for package in required_packages:
                    if package in content:
                        print(f"✅ {package} in requirements.txt")
                    else:
                        print(f"⚠️ {package} not in requirements.txt")
        except Exception as e:
            print(f"❌ Error reading requirements.txt: {e}")
    else:
        print("⚠️ requirements.txt not found")

def test_browser_console():
    """Test browser console for errors"""
    print("\n🔍 Browser Console Test Instructions...")
    print("1. Open your browser's Developer Tools (F12)")
    print("2. Go to the Console tab")
    print("3. Check for any JavaScript errors")
    print("4. Look for messages about chatbot initialization")
    print("5. Test the chatbot button functionality")

def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 MEDicos Chatbot Initialization Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test environment first
    test_environment()
    
    # Test frontend integration
    frontend_ok = test_frontend_integration()
    
    # Test API (only if server is running)
    print("\n" + "=" * 60)
    print("🚀 Testing Chatbot API (requires server to be running)")
    print("=" * 60)
    
    try:
        api_ok = test_chatbot_api()
    except Exception as e:
        print(f"❌ API test failed: {e}")
        print("💡 Make sure to start the chatbot server first:")
        print("   python start_chatbot.py")
        api_ok = False
    
    # Provide instructions
    print("\n" + "=" * 60)
    print("📋 Test Results Summary")
    print("=" * 60)
    
    if frontend_ok:
        print("✅ Frontend integration: OK")
    else:
        print("❌ Frontend integration: Issues found")
    
    if api_ok:
        print("✅ API endpoints: OK")
    else:
        print("❌ API endpoints: Issues found")
    
    print("\n🔧 Troubleshooting Steps:")
    print("1. Start the chatbot server: python start_chatbot.py")
    print("2. Check browser console for JavaScript errors")
    print("3. Verify .env file has API keys")
    print("4. Install dependencies: pip install -r requirements.txt")
    print("5. Check if ports 5000 and 5001 are available")
    
    test_browser_console()
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 