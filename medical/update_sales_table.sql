-- Update sales table for Razorpay integration
-- Remove doctor_phone field and add new payment-related fields

USE medicos_pharmacy;

-- Remove doctor_phone column
ALTER TABLE sales DROP COLUMN doctor_phone;

-- Add new columns for Razorpay integration
ALTER TABLE sales ADD COLUMN rate_per_tablet DECIMAL(10,2) AFTER quantity_sold;
ALTER TABLE sales ADD COLUMN payment_id VARCHAR(100) AFTER sold_by;
ALTER TABLE sales ADD COLUMN order_id VARCHAR(100) AFTER payment_id;
ALTER TABLE sales ADD COLUMN payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending' AFTER order_id;
ALTER TABLE sales ADD COLUMN payment_method VARCHAR(50) DEFAULT 'razorpay' AFTER payment_status;

-- Update existing records to set default values
UPDATE sales SET rate_per_tablet = unit_price WHERE rate_per_tablet IS NULL;
UPDATE sales SET payment_status = 'completed' WHERE payment_status IS NULL;

-- Add indexes for better performance
CREATE INDEX idx_sales_payment_id ON sales(payment_id);
CREATE INDEX idx_sales_order_id ON sales(order_id);
CREATE INDEX idx_sales_payment_status ON sales(payment_status);

-- Update the sales_summary view to include new fields
DROP VIEW IF EXISTS sales_summary;
CREATE VIEW sales_summary AS
SELECT 
    s.sale_id,
    s.sale_date,
    s.customer_name,
    s.customer_phone,
    m.medicine_name,
    s.quantity_sold,
    s.rate_per_tablet,
    s.total_amount,
    s.doctor_name,
    st.full_name as sold_by_name,
    s.payment_status,
    s.payment_method,
    s.prescription_photo_url
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
JOIN staff st ON s.sold_by = st.staff_id
ORDER BY s.sale_date DESC; 