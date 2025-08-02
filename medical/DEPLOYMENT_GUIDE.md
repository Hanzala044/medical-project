# 🚀 MEDicos Pharmacy - Deployment Guide

## 📋 **Overview**
This guide will help you deploy your MEDicos Pharmacy Management System to free hosting platforms that support long-term hosting without expiry.

## 🎯 **Recommended Hosting Platforms**

### **1. Railway (Recommended)**
- ✅ **Free tier**: $5/month credit (sufficient for small apps)
- ✅ **Long-term**: No expiry on free tier
- ✅ **Database**: PostgreSQL included
- ✅ **Easy deployment**: Direct GitHub integration
- ✅ **SSL**: Automatic HTTPS

### **2. Render**
- ✅ **Free tier**: Available with limitations
- ✅ **Database**: PostgreSQL included
- ✅ **Long-term**: No expiry
- ✅ **Easy setup**: GitHub integration

## 🔧 **Pre-Deployment Setup**

### **Step 1: Install PostgreSQL Dependencies**
```bash
pip install psycopg2-binary
```

### **Step 2: Test Local PostgreSQL Setup**
```bash
python test_postgresql.py
```

### **Step 3: Update Environment Variables**
Create a `.env` file for local testing:
```env
DB_TYPE=postgresql
POSTGRES_HOST=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=medicos_pharmacy
POSTGRES_PORT=5432
```

## 🚀 **Railway Deployment (Recommended)**

### **Step 1: Sign Up for Railway**
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Create a new project

### **Step 2: Connect GitHub Repository**
1. Click "Deploy from GitHub repo"
2. Select your `medical-project` repository
3. Choose the `main` branch

### **Step 3: Add PostgreSQL Database**
1. Click "New" → "Database" → "PostgreSQL"
2. Railway will automatically provide connection details
3. Copy the connection details for environment variables

### **Step 4: Configure Environment Variables**
In your Railway project settings, add these environment variables:

```env
DB_TYPE=postgresql
POSTGRES_HOST=${POSTGRES_HOST}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_PORT=${POSTGRES_PORT}
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

### **Step 5: Configure Build Settings**
Set the following in Railway:
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`
- **Root Directory**: `medical`

### **Step 6: Deploy**
1. Railway will automatically deploy when you push to GitHub
2. Monitor the deployment logs
3. Your app will be available at the provided URL

## 🌐 **Render Deployment (Alternative)**

### **Step 1: Sign Up for Render**
1. Go to [render.com](https://render.com)
2. Sign up with your GitHub account
3. Create a new Web Service

### **Step 2: Connect Repository**
1. Connect your GitHub repository
2. Choose the `main` branch
3. Set root directory to `medical`

### **Step 3: Configure Service**
- **Name**: `medicos-pharmacy`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

### **Step 4: Add PostgreSQL Database**
1. Create a new PostgreSQL database
2. Copy connection details
3. Add environment variables

### **Step 5: Environment Variables**
Add these environment variables in Render:
```env
DB_TYPE=postgresql
POSTGRES_HOST=${POSTGRES_HOST}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_PORT=${POSTGRES_PORT}
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

## 🔒 **Security Configuration**

### **Environment Variables for Production**
Make sure to set these in your hosting platform:

```env
# Database
DB_TYPE=postgresql
POSTGRES_HOST=${provided_by_hosting}
POSTGRES_USER=${provided_by_hosting}
POSTGRES_PASSWORD=${provided_by_hosting}
POSTGRES_DB=${provided_by_hosting}
POSTGRES_PORT=${provided_by_hosting}

# Flask
FLASK_ENV=production
SECRET_KEY=your_secure_secret_key_here

# External APIs (keep your actual keys)
RAZORPAY_KEY_ID=rzp_test_zPJXCKox2LJ0s0
RAZORPAY_KEY_SECRET=54as6NgzRsakRww7nuHW8naU
TWILIO_ACCOUNT_SID=ACadb4fd9708b8688cabb851d62af1aeab
TWILIO_AUTH_TOKEN=e8179bebe56e5e3eb61bff73616c6e16
GOOGLE_API_KEY=65d87663e049b9db9568b7f17d77cc9c30759541
```

## 🧪 **Testing Deployment**

### **Step 1: Check Application Health**
1. Visit your deployed URL
2. Check if the homepage loads
3. Test admin login: `admin1` / `admin123`

### **Step 2: Test Database Connection**
1. Go to admin dashboard
2. Check if data loads properly
3. Test staff login: `staff1` / `staff123`

### **Step 3: Test Core Features**
1. Medicine management
2. Sales recording
3. WhatsApp integration
4. Payment processing

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**
- Check environment variables
- Verify PostgreSQL is running
- Test connection locally first

#### **2. Import Errors**
- Ensure all dependencies are in `requirements.txt`
- Check Python version compatibility
- Verify file paths

#### **3. Static Files Not Loading**
- Check static folder configuration
- Verify file permissions
- Test locally first

### **Debug Commands**
```bash
# Test database locally
python test_postgresql.py

# Test Flask app locally
python app.py

# Check requirements
pip list
```

## 📊 **Monitoring & Maintenance**

### **Railway Monitoring**
- Check deployment logs
- Monitor resource usage
- Set up alerts for errors

### **Render Monitoring**
- View service logs
- Monitor performance
- Check database connections

## 🎯 **Next Steps After Deployment**

1. **Set up custom domain** (optional)
2. **Configure SSL certificates** (automatic on most platforms)
3. **Set up monitoring and alerts**
4. **Create backup strategy**
5. **Test all functionality thoroughly**

## 📞 **Support**

If you encounter issues:
1. Check the deployment logs
2. Test locally first
3. Verify environment variables
4. Check platform documentation

---

**Created by: Mohammed Hanzala**  
**System: MEDicos Pharmacy Management**  
**Last Updated: August 2024** 