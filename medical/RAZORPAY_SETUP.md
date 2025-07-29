# Razorpay Integration Setup Guide

## Overview
This guide will help you set up Razorpay payment integration for the MEDicos Pharmacy Management System.

## Prerequisites
1. A Razorpay account (sign up at https://razorpay.com)
2. Python 3.7+ installed
3. MySQL database running

## Step 1: Install Dependencies
```bash
pip install razorpay==1.4.1
```

## Step 2: Get Razorpay API Keys
1. Log in to your Razorpay Dashboard
2. Go to Settings → API Keys
3. Generate a new API key pair
4. Copy your **Key ID** and **Key Secret**

## Step 3: Update Configuration
Edit `medical/razorpay_integration.py` and replace the placeholder values:

```python
# Replace these with your actual Razorpay test keys
RAZORPAY_KEY_ID = 'rzp_test_YOUR_ACTUAL_KEY_ID'
RAZORPAY_KEY_SECRET = 'YOUR_ACTUAL_KEY_SECRET'
```

## Step 4: Update Database Schema
Run the database update script:

```bash
mysql -u root -p < update_sales_table.sql
```

Or execute the SQL commands manually in your MySQL client.

## Step 5: Test the Integration
1. Start the Flask server: `python app.py`
2. Log in to the staff dashboard
3. Fill out the medicine sale form
4. Click "Pay with Razorpay"
5. Complete the payment using Razorpay's test mode

## Test Mode Features
- Use test card numbers: 4111 1111 1111 1111
- Any future expiry date
- Any 3-digit CVV
- Any OTP (e.g., 123456)

## Production Setup
For production:
1. Switch to live mode in Razorpay dashboard
2. Update API keys to live keys
3. Ensure proper SSL certificate
4. Test thoroughly with small amounts

## Payment Flow
1. User fills medicine sale form
2. Clicks "Pay with Razorpay"
3. Razorpay modal opens
4. User completes payment
5. Payment is verified on backend
6. Sale record is saved to database
7. WhatsApp receipt is sent automatically

## Troubleshooting
- **Payment fails**: Check API keys and network connection
- **Database errors**: Ensure MySQL is running and schema is updated
- **Modal doesn't open**: Check browser console for JavaScript errors

## Security Notes
- Never commit API keys to version control
- Use environment variables in production
- Implement proper error handling
- Validate all payment data on backend

## Support
For Razorpay-specific issues, contact Razorpay support.
For application issues, check the Flask server logs. 