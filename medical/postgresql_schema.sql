-- PostgreSQL Schema for MEDicos Pharmacy Management System
-- This file contains all the table creation scripts for PostgreSQL

-- Create database (run this separately if needed)
-- CREATE DATABASE medicos_pharmacy;

-- Enable UUID extension for better ID management
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Admins table
CREATE TABLE IF NOT EXISTS admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Staff table
CREATE TABLE IF NOT EXISTS staff (
    staff_id SERIAL PRIMARY KEY,
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

-- Medicines table
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id SERIAL PRIMARY KEY,
    medicine_name VARCHAR(200) NOT NULL,
    batch_number VARCHAR(50) UNIQUE NOT NULL,
    expiry_date DATE NOT NULL,
    date_of_purchase DATE NOT NULL,
    quantity_available INTEGER NOT NULL DEFAULT 0,
    unit_price DECIMAL(10,2) NOT NULL,
    manufacturer VARCHAR(200),
    category VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (created_by) REFERENCES staff(staff_id) ON DELETE SET NULL
);

-- Sales table with WhatsApp tracking
CREATE TABLE IF NOT EXISTS sales (
    sale_id SERIAL PRIMARY KEY,
    medicine_id INTEGER NOT NULL,
    quantity_sold INTEGER NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_name VARCHAR(100),
    customer_phone VARCHAR(20),
    doctor_name VARCHAR(100),
    sold_by INTEGER NOT NULL,
    payment_id VARCHAR(100),
    order_id VARCHAR(100),
    rate_per_tablet DECIMAL(10,2),
    -- WhatsApp tracking columns
    whatsapp_receipt_sent BOOLEAN DEFAULT FALSE,
    whatsapp_message_id VARCHAR(100),
    receipt_sent_date TIMESTAMP NULL,
    whatsapp_provider VARCHAR(50) DEFAULT 'twilio',
    FOREIGN KEY (medicine_id) REFERENCES medicines(medicine_id) ON DELETE CASCADE,
    FOREIGN KEY (sold_by) REFERENCES staff(staff_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_medicines_batch_number ON medicines(batch_number);
CREATE INDEX IF NOT EXISTS idx_medicines_expiry_date ON medicines(expiry_date);
CREATE INDEX IF NOT EXISTS idx_sales_sale_date ON sales(sale_date);
CREATE INDEX IF NOT EXISTS idx_sales_customer_phone ON sales(customer_phone);
CREATE INDEX IF NOT EXISTS idx_sales_whatsapp_sent ON sales(whatsapp_receipt_sent);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_medicines_updated_at 
    BEFORE UPDATE ON medicines 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user
INSERT INTO admins (username, password, full_name, email, phone) 
VALUES ('admin1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO', 'Admin User', 'admin@medicos.com', '+1234567890')
ON CONFLICT (username) DO NOTHING;

-- Insert default staff users
INSERT INTO staff (username, password, full_name, email, phone, position, hire_date) 
VALUES 
    ('staff1', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO', 'Staff Member 1', 'staff1@medicos.com', '+1234567891', 'Sales Executive', '2024-01-01'),
    ('staff2', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO', 'Staff Member 2', 'staff2@medicos.com', '+1234567892', 'Pharmacist', '2024-01-01'),
    ('staff3', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iQeO', 'Staff Member 3', 'staff3@medicos.com', '+1234567893', 'Cashier', '2024-01-01')
ON CONFLICT (username) DO NOTHING;

-- Insert sample medicines
INSERT INTO medicines (medicine_name, batch_number, expiry_date, date_of_purchase, quantity_available, unit_price, manufacturer, category, description) 
VALUES 
    ('Paracetamol 500mg', 'BATCH001', '2025-12-31', '2024-01-01', 100, 5.00, 'ABC Pharma', 'Pain Relief', 'Fever and pain relief tablets'),
    ('Amoxicillin 250mg', 'BATCH002', '2025-06-30', '2024-01-01', 50, 15.00, 'XYZ Pharma', 'Antibiotics', 'Broad spectrum antibiotic'),
    ('Omeprazole 20mg', 'BATCH003', '2025-09-30', '2024-01-01', 75, 25.00, 'DEF Pharma', 'Gastric', 'Acid reflux medication')
ON CONFLICT (batch_number) DO NOTHING; 