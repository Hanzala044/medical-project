-- MEDicos Pharmacy Management System Database Schema
-- Created by: Mohammed Hanzala

-- Create the database
CREATE DATABASE IF NOT EXISTS medicos_pharmacy;
USE medicos_pharmacy;

-- Admin table for admin login credentials
CREATE TABLE admins (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Staff table for staff login and registration
CREATE TABLE staff (
    staff_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    position VARCHAR(50) NOT NULL,
    hire_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Medicines table for inventory management (CRUD operations)
CREATE TABLE medicines (
    medicine_id INT PRIMARY KEY AUTO_INCREMENT,
    medicine_name VARCHAR(200) NOT NULL,
    batch_number VARCHAR(50) UNIQUE NOT NULL,
    expiry_date DATE NOT NULL,
    date_of_purchase DATE NOT NULL,
    quantity_available INT NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL,
    manufacturer VARCHAR(200),
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES admins(admin_id)
);

-- Sales table for staff to record customer purchases
CREATE TABLE sales (
    sale_id INT PRIMARY KEY AUTO_INCREMENT,
    medicine_id INT NOT NULL,
    quantity_sold INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    doctor_name VARCHAR(100),
    doctor_phone VARCHAR(20),
    prescription_photo_url VARCHAR(500),
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sold_by INT NOT NULL,
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id),
    FOREIGN KEY (sold_by) REFERENCES staff(staff_id)
);

-- Sample data for admins
INSERT INTO admins (username, password, full_name, email, phone) VALUES
('admin1', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Dr. Sarah Johnson', 'admin1@medicos.com', '+1-555-0101'),
('admin2', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Mr. Michael Chen', 'admin2@medicos.com', '+1-555-0102');

-- Sample data for staff
INSERT INTO staff (username, password, full_name, email, phone, position, hire_date) VALUES
('staff1', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Ayesha Khan', 'ayesha.khan@medicos.com', '+1-555-0201', 'Senior Pharmacist', '2020-03-15'),
('staff2', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Imran Malik', 'imran.malik@medicos.com', '+1-555-0202', 'Pharmacy Manager', '2019-06-10'),
('staff3', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Sara Ahmed', 'sara.ahmed@medicos.com', '+1-555-0203', 'Junior Pharmacist', '2021-09-20');

-- Sample data for medicines
INSERT INTO medicines (medicine_name, batch_number, expiry_date, date_of_purchase, quantity_available, unit_price, manufacturer, category, description, created_by) VALUES
('Paracetamol 500mg', 'BATCH001-2024', '2026-12-31', '2024-01-15', 500, 2.50, 'ABC Pharmaceuticals', 'Pain Relief', 'Standard pain relief medication for headaches and fever', 1),
('Amoxicillin 250mg', 'BATCH002-2024', '2025-08-15', '2024-02-20', 200, 8.75, 'XYZ Labs', 'Antibiotics', 'Broad-spectrum antibiotic for bacterial infections', 1),
('Omeprazole 20mg', 'BATCH003-2024', '2026-06-30', '2024-03-10', 150, 12.00, 'MediCorp', 'Gastrointestinal', 'Proton pump inhibitor for acid reflux and ulcers', 2),
('Metformin 500mg', 'BATCH004-2024', '2025-11-20', '2024-01-30', 300, 5.25, 'HealthPharm', 'Diabetes', 'Oral diabetes medication for type 2 diabetes', 1),
('Ibuprofen 400mg', 'BATCH005-2024', '2026-09-15', '2024-02-05', 400, 3.00, 'ABC Pharmaceuticals', 'Pain Relief', 'Anti-inflammatory medication for pain and swelling', 2);

-- Sample data for sales
INSERT INTO sales (medicine_id, quantity_sold, unit_price, total_amount, doctor_name, doctor_phone, prescription_photo_url, customer_name, customer_phone, sold_by) VALUES
(1, 2, 2.50, 5.00, 'Dr. Emily Wilson', '+1-555-0301', 'https://drive.google.com/file/d/sample1.jpg', 'John Smith', '+1-555-0401', 1),
(2, 1, 8.75, 8.75, 'Dr. Robert Davis', '+1-555-0302', 'https://drive.google.com/file/d/sample2.jpg', 'Maria Garcia', '+1-555-0402', 2),
(3, 1, 12.00, 12.00, 'Dr. Lisa Thompson', '+1-555-0303', 'https://drive.google.com/file/d/sample3.jpg', 'David Brown', '+1-555-0403', 1);

-- Create indexes for better performance
CREATE INDEX idx_medicine_batch ON medicines(batch_number);
CREATE INDEX idx_medicine_expiry ON medicines(expiry_date);
CREATE INDEX idx_medicine_name ON medicines(medicine_name);
CREATE INDEX idx_sale_date ON sales(sale_date);
CREATE INDEX idx_sale_staff ON sales(sold_by);

-- Create views for common queries
CREATE VIEW medicine_inventory AS
SELECT 
    medicine_id,
    medicine_name,
    batch_number,
    expiry_date,
    date_of_purchase,
    quantity_available,
    unit_price,
    manufacturer,
    category,
    CASE 
        WHEN expiry_date < CURDATE() THEN 'Expired'
        WHEN expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'Expiring Soon'
        ELSE 'Valid'
    END as expiry_status
FROM medicines
WHERE quantity_available > 0;

CREATE VIEW sales_summary AS
SELECT 
    s.sale_id,
    m.medicine_name,
    s.quantity_sold,
    s.total_amount,
    s.doctor_name,
    s.customer_name,
    s.sale_date,
    st.full_name as sold_by_name
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
JOIN staff st ON s.sold_by = st.staff_id
ORDER BY s.sale_date DESC;

-- Create stored procedures for common operations

-- Procedure to add new medicine
DELIMITER //
CREATE PROCEDURE AddMedicine(
    IN p_medicine_name VARCHAR(200),
    IN p_batch_number VARCHAR(50),
    IN p_expiry_date DATE,
    IN p_date_of_purchase DATE,
    IN p_quantity_available INT,
    IN p_unit_price DECIMAL(10,2),
    IN p_manufacturer VARCHAR(200),
    IN p_category VARCHAR(100),
    IN p_description TEXT,
    IN p_created_by INT
)
BEGIN
    INSERT INTO medicines (
        medicine_name, batch_number, expiry_date, date_of_purchase,
        quantity_available, unit_price, manufacturer, category, description, created_by
    ) VALUES (
        p_medicine_name, p_batch_number, p_expiry_date, p_date_of_purchase,
        p_quantity_available, p_unit_price, p_manufacturer, p_category, p_description, p_created_by
    );
END //
DELIMITER ;

-- Procedure to record a sale
DELIMITER //
CREATE PROCEDURE RecordSale(
    IN p_medicine_id INT,
    IN p_quantity_sold INT,
    IN p_doctor_name VARCHAR(100),
    IN p_doctor_phone VARCHAR(20),
    IN p_prescription_photo_url VARCHAR(500),
    IN p_customer_name VARCHAR(100),
    IN p_customer_phone VARCHAR(20),
    IN p_sold_by INT
)
BEGIN
    DECLARE v_unit_price DECIMAL(10,2);
    DECLARE v_total_amount DECIMAL(10,2);
    
    -- Get unit price from medicines table
    SELECT unit_price INTO v_unit_price FROM medicines WHERE medicine_id = p_medicine_id;
    
    -- Calculate total amount
    SET v_total_amount = p_quantity_sold * v_unit_price;
    
    -- Insert sale record
    INSERT INTO sales (
        medicine_id, quantity_sold, unit_price, total_amount,
        doctor_name, doctor_phone, prescription_photo_url,
        customer_name, customer_phone, sold_by
    ) VALUES (
        p_medicine_id, p_quantity_sold, v_unit_price, v_total_amount,
        p_doctor_name, p_doctor_phone, p_prescription_photo_url,
        p_customer_name, p_customer_phone, p_sold_by
    );
    
    -- Update medicine quantity
    UPDATE medicines 
    SET quantity_available = quantity_available - p_quantity_sold
    WHERE medicine_id = p_medicine_id;
END //
DELIMITER ;

-- Show all tables
SHOW TABLES;

-- Display sample data
SELECT 'Admins' as table_name, COUNT(*) as record_count FROM admins
UNION ALL
SELECT 'Staff' as table_name, COUNT(*) as record_count FROM staff
UNION ALL
SELECT 'Medicines' as table_name, COUNT(*) as record_count FROM medicines
UNION ALL
SELECT 'Sales' as table_name, COUNT(*) as record_count FROM sales; 