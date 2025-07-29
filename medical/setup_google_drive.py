#!/usr/bin/env python3
"""
Google Drive Setup Script for MEDicos Pharmacy Management System
This script helps you set up Google Drive integration for prescription uploads.
"""

import os
import json

def create_credentials_template():
    """Create a template credentials.json file"""
    template = {
        "type": "service_account",
        "project_id": "your-project-id",
        "private_key_id": "your-private-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n",
        "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
        "client_id": "your-client-id",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
    }
    
    with open('credentials.json', 'w') as f:
        json.dump(template, f, indent=2)
    
    print("✅ Created credentials.json template")
    print("📝 Please replace the placeholder values with your actual Google Drive API credentials")

def check_credentials():
    """Check if credentials.json exists and is valid"""
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found")
        return False
    
    try:
        with open('credentials.json', 'r') as f:
            creds = json.load(f)
        
        # Check if it's still the template
        if creds.get('project_id') == 'your-project-id':
            print("⚠️ credentials.json still contains template values")
            return False
        
        print("✅ credentials.json found and appears to be configured")
        return True
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Google Drive Setup for MEDicos Pharmacy")
    print("=" * 50)
    
    if check_credentials():
        print("\n✅ Google Drive is already configured!")
        return
    
    print("\n📋 Setting up Google Drive integration...")
    print("\nTo get your Google Drive API credentials:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing one")
    print("3. Enable Google Drive API")
    print("4. Create a Service Account")
    print("5. Download the JSON credentials file")
    print("6. Rename it to 'credentials.json' and place it in this directory")
    print("7. Share your Google Drive folder with the service account email")
    
    create_credentials = input("\nWould you like to create a credentials.json template? (y/n): ")
    if create_credentials.lower() == 'y':
        create_credentials_template()
        print("\n📝 Next steps:")
        print("1. Replace the placeholder values in credentials.json with your actual credentials")
        print("2. Update the GOOGLE_DRIVE_FOLDER_ID in app.py with your folder ID")
        print("3. Restart the application")
    else:
        print("\n📝 Please manually create credentials.json with your Google Drive API credentials")

if __name__ == "__main__":
    main() 