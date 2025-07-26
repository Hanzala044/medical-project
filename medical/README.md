# MEDicos Pharmacy Management System

A comprehensive pharmacy management system built with modern web technologies for managing medicines, sales, and staff operations.

## 🏥 Features

### **Admin Dashboard**
- **Medicine Management**: Full CRUD operations for medicines
- **Inventory Tracking**: Batch numbers, expiry dates, quantities
- **Dashboard Analytics**: Real-time statistics and insights
- **User Management**: Staff registration and management

### **Staff Dashboard**
- **Sales Recording**: Process customer purchases
- **Medicine Selection**: Choose from available inventory
- **Prescription Upload**: Google Drive integration for prescription photos
- **Doctor Information**: Track prescribing doctors
- **Digital Clock**: Real-time time and date display

### **Authentication System**
- **Admin Login**: Secure admin access with role-based permissions
- **Staff Registration**: New staff member registration
- **Session Management**: Secure login/logout functionality

### **Database Features**
- **MySQL Database**: Robust relational database design
- **Sample Data**: Pre-loaded with sample medicines and users
- **Stored Procedures**: Optimized database operations
- **Views**: Common query views for reporting

## 🛠️ Technology Stack

### **Frontend**
- **HTML5**: Semantic markup
- **CSS3**: Tailwind CSS for styling
- **JavaScript**: Modern ES6+ features
- **Lucide Icons**: Beautiful icon library

### **Backend**
- **Python Flask**: Lightweight web framework
- **MySQL**: Relational database
- **Google Drive API**: File upload integration

### **Database**
- **MySQL 8.0+**: Primary database
- **Stored Procedures**: Optimized operations
- **Foreign Keys**: Data integrity
- **Indexes**: Performance optimization

## 📋 Prerequisites

Before running the application, ensure you have:

1. **Python 3.8+** installed
2. **MySQL 8.0+** installed and running
3. **Google Cloud Console** account (for Drive API)
4. **Modern web browser** (Chrome, Firefox, Safari, Edge)

## 🚀 Installation & Setup

### 1. **Clone the Repository**
```bash
git clone <repository-url>
cd medical
```

### 2. **Install Python Dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Database Setup**

#### **Option A: Using the SQL Script**
```bash
mysql -u root -p < database_schema.sql
```

#### **Option B: Manual Setup**
1. Create MySQL database:
```sql
CREATE DATABASE medicos_pharmacy;
```

2. Update database configuration in `app.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'medicos_pharmacy'
}
```

### 4. **Google Drive API Setup**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Download the JSON credentials file
   - Rename to `credentials.json` and place in project root

5. Share your Google Drive folder with the service account email

### 5. **Configuration**

Update the following files as needed:

#### **Database Configuration** (`app.py`)
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_mysql_username',
    'password': 'your_mysql_password',
    'database': 'medicos_pharmacy'
}
```

#### **Google Drive Configuration** (`app.py`)
```python
SERVICE_ACCOUNT_FILE = 'credentials.json'  # Path to your credentials file
```

## 🏃‍♂️ Running the Application

### 1. **Start the Backend Server**
```bash
python app.py
```

The server will start on `http://localhost:5000`

### 2. **Access the Frontend**

Open your web browser and navigate to:
- **Landing Page**: `http://localhost:5000/index.html`
- **Admin Login**: `http://localhost:5000/auth-admin.html`
- **Staff Login**: `http://localhost:5000/auth-admin.html` (Staff tab)

## 👤 Default Credentials

### **Admin Accounts**
- **Username**: `admin1` | **Password**: `admin123`
- **Username**: `admin2` | **Password**: `admin123`

### **Staff Accounts**
- **Username**: `staff1` | **Password**: `staff123`
- **Username**: `staff2` | **Password**: `staff123`
- **Username**: `staff3` | **Password**: `staff123`

## 📊 Database Schema

### **Tables**

1. **`admins`** - Admin user accounts
2. **`staff`** - Staff user accounts
3. **`medicines`** - Medicine inventory
4. **`sales`** - Sales transactions

### **Key Fields**

#### **Medicines Table**
- `medicine_name` - Name of the medicine
- `batch_number` - Unique batch identifier
- `expiry_date` - Expiration date
- `date_of_purchase` - Purchase date
- `quantity_available` - Current stock
- `unit_price` - Price per unit

#### **Sales Table**
- `medicine_id` - Reference to medicine
- `quantity_sold` - Quantity sold
- `doctor_name` - Prescribing doctor
- `doctor_phone` - Doctor's contact
- `prescription_photo_url` - Google Drive URL
- `customer_name` - Customer name
- `customer_phone` - Customer contact

## 🔧 API Endpoints

### **Authentication**
- `POST /api/login` - User login
- `POST /api/register` - Staff registration
- `POST /api/logout` - User logout

### **Medicines (Admin)**
- `GET /api/medicines` - Get all medicines
- `POST /api/medicines` - Add new medicine
- `PUT /api/medicines/{id}` - Update medicine
- `DELETE /api/medicines/{id}` - Delete medicine

### **Sales (Staff)**
- `GET /api/sales` - Get all sales
- `POST /api/sales` - Record new sale
- `GET /api/medicines/available` - Get available medicines

### **File Upload**
- `POST /api/upload-prescription` - Upload prescription to Google Drive

### **Dashboard**
- `GET /api/dashboard/stats` - Get dashboard statistics

## 🎯 Usage Guide

### **For Admins**

1. **Login** with admin credentials
2. **Add Medicines**:
   - Click "Add Medicine" button
   - Fill in all required fields
   - Submit the form

3. **Manage Inventory**:
   - View all medicines in the table
   - Edit or delete medicines as needed
   - Monitor expiry dates and stock levels

4. **View Analytics**:
   - Check dashboard statistics
   - Monitor sales and revenue

### **For Staff**

1. **Login** with staff credentials
2. **Record Sales**:
   - Click "Add Sale" button
   - Select medicine from dropdown
   - Enter quantity and customer details
   - Upload prescription photo (optional)
   - Submit the sale

3. **View Sales History**:
   - Check the sales table
   - Search for specific sales
   - View prescription photos

## 🔒 Security Features

- **Password Hashing**: Secure password storage using bcrypt
- **Session Management**: Secure user sessions
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Protection**: Parameterized queries
- **File Upload Security**: Secure file handling

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🐛 Troubleshooting

### **Common Issues**

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify database credentials in `app.py`
   - Ensure database exists

2. **Google Drive Upload Fails**
   - Verify `credentials.json` file exists
   - Check Google Drive API is enabled
   - Ensure service account has proper permissions

3. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`
   - Or kill existing process using port 5000

4. **CORS Errors**
   - Ensure backend is running on correct port
   - Check browser console for specific errors

### **Logs and Debugging**

Enable debug mode in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

Check console output for detailed error messages.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Developer

**Mohammed Hanzala**
- **GitHub**: [Hanzala044](https://github.com/Hanzala044/)
- **LinkedIn**: [Mohammed Hanzala](https://www.linkedin.com/in/mohammed-hanzala-0ab14424a/)
- **Instagram**: [@mohd_.hanzala](https://www.instagram.com/mohd_.hanzala/)
- **Twitter**: [@Arabian263](https://x.com/Arabian263)

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact the developer directly
- Check the troubleshooting section above

---

**MEDicos Pharmacy Management System** - Making healthcare management efficient and reliable since 2018! 🏥💊 