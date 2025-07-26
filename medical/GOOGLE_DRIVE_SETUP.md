# Google Drive API Setup Guide

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Drive API"
   - Click on it and press "Enable"

## Step 2: Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in the details:
   - Name: `medicos-pharmacy-drive`
   - Description: `Service account for prescription uploads`
4. Click "Create and Continue"
5. Skip the optional steps and click "Done"

## Step 3: Generate JSON Key

1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Click "Create"
6. Download the JSON file and rename it to `credentials.json`
7. Place it in the `medical` folder (same directory as `app.py`)

## Step 4: Share Google Drive Folder

1. Go to your Google Drive
2. Navigate to the folder where you want to store prescriptions
3. Right-click on the folder and select "Share"
4. Add the service account email (found in the JSON file under `client_email`)
5. Give it "Editor" permissions
6. Copy the folder ID from the URL:
   - URL format: `https://drive.google.com/drive/u/3/folders/FOLDER_ID`
   - The FOLDER_ID is the long string after `/folders/`

## Step 5: Update Configuration

1. Open `app.py`
2. Find this line:
   ```python
   GOOGLE_DRIVE_FOLDER_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
   ```
3. Replace the folder ID with your actual folder ID

## Step 6: Test the Setup

1. Restart the Flask server
2. Try uploading a prescription file
3. Check if it appears in your Google Drive folder

## Troubleshooting

### Error: "Google Drive credentials not configured"
- Make sure `credentials.json` is in the same folder as `app.py`
- Check that the file name is exactly `credentials.json`

### Error: "Permission denied"
- Make sure you shared the folder with the service account email
- Check that the service account has "Editor" permissions

### Error: "Folder not found"
- Verify the folder ID is correct
- Make sure the folder exists and is accessible

## File Structure

Your `medical` folder should look like this:
```
medical/
├── app.py
├── credentials.json          # Google Drive service account key
├── GOOGLE_DRIVE_SETUP.md     # This file
├── requirements.txt
├── index.html
├── auth-admin.html
├── staff_dashboard.html
├── admin_dashboard.html
└── ... (other files)
``` 