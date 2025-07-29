-- =====================================================
-- MEDicos Pharmacy Database Management Scripts
-- Created by: Mohammed Hanzala
-- =====================================================

-- Use the database
USE medicos_pharmacy;

-- =====================================================
-- 1. VIEW ALL SALES RECORDS WITH IMAGES
-- =====================================================

-- View all sales with prescription images
SELECT 
    s.sale_id,
    s.sale_date,
    m.medicine_name,
    s.customer_name,
    s.customer_phone,
    s.quantity_sold,
    s.total_amount,
    s.doctor_name,
    s.doctor_phone,
    s.prescription_photo_url,
    st.full_name as sold_by_name
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
JOIN staff st ON s.sold_by = st.staff_id
ORDER BY s.sale_date DESC;

-- =====================================================
-- 2. VIEW SALES WITH IMAGES ONLY
-- =====================================================

-- View sales that have prescription images
SELECT 
    s.sale_id,
    s.sale_date,
    m.medicine_name,
    s.customer_name,
    s.quantity_sold,
    s.total_amount,
    s.prescription_photo_url,
    st.full_name as sold_by_name
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
JOIN staff st ON s.sold_by = st.staff_id
WHERE s.prescription_photo_url IS NOT NULL 
    AND s.prescription_photo_url != ''
ORDER BY s.sale_date DESC;

-- =====================================================
-- 3. VIEW SALES BY STAFF MEMBER
-- =====================================================

-- View sales grouped by staff member
SELECT 
    st.full_name as staff_name,
    COUNT(s.sale_id) as total_sales,
    SUM(s.total_amount) as total_revenue,
    COUNT(CASE WHEN s.prescription_photo_url IS NOT NULL THEN 1 END) as sales_with_images
FROM sales s
JOIN staff st ON s.sold_by = st.staff_id
GROUP BY st.staff_id, st.full_name
ORDER BY total_revenue DESC;

-- =====================================================
-- 4. VIEW MEDICINES INVENTORY
-- =====================================================

-- View all medicines with expiry status
SELECT 
    medicine_id,
    medicine_name,
    batch_number,
    quantity_available,
    unit_price,
    manufacturer,
    category,
    expiry_date,
    CASE 
        WHEN expiry_date < CURDATE() THEN 'EXPIRED'
        WHEN expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'EXPIRING SOON'
        ELSE 'VALID'
    END as expiry_status
FROM medicines
ORDER BY expiry_date;

-- =====================================================
-- 5. VIEW STAFF MEMBERS
-- =====================================================

-- View all staff members
SELECT 
    staff_id,
    full_name,
    email,
    phone,
    position,
    hire_date,
    last_login,
    is_active
FROM staff
ORDER BY staff_id;

-- =====================================================
-- 6. VIEW ADMINS
-- =====================================================

-- View all administrators
SELECT 
    admin_id,
    full_name,
    email,
    phone,
    last_login,
    is_active
FROM admins
ORDER BY admin_id;

-- =====================================================
-- 7. SALES SUMMARY BY DATE
-- =====================================================

-- View daily sales summary
SELECT 
    DATE(s.sale_date) as sale_date,
    COUNT(s.sale_id) as total_sales,
    SUM(s.total_amount) as daily_revenue,
    COUNT(CASE WHEN s.prescription_photo_url IS NOT NULL THEN 1 END) as sales_with_images
FROM sales s
GROUP BY DATE(s.sale_date)
ORDER BY sale_date DESC;

-- =====================================================
-- 8. TOP SELLING MEDICINES
-- =====================================================

-- View top selling medicines
SELECT 
    m.medicine_name,
    COUNT(s.sale_id) as times_sold,
    SUM(s.quantity_sold) as total_quantity_sold,
    SUM(s.total_amount) as total_revenue
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
GROUP BY m.medicine_id, m.medicine_name
ORDER BY total_revenue DESC;

-- =====================================================
-- 9. CUSTOMER PURCHASE HISTORY
-- =====================================================

-- View customer purchase history
SELECT 
    s.customer_name,
    s.customer_phone,
    COUNT(s.sale_id) as total_purchases,
    SUM(s.total_amount) as total_spent,
    MAX(s.sale_date) as last_purchase
FROM sales s
WHERE s.customer_name IS NOT NULL
GROUP BY s.customer_name, s.customer_phone
ORDER BY total_spent DESC;

-- =====================================================
-- 10. DOCTOR PRESCRIPTION ANALYSIS
-- =====================================================

-- View prescriptions by doctor
SELECT 
    s.doctor_name,
    s.doctor_phone,
    COUNT(s.sale_id) as prescriptions_written,
    COUNT(CASE WHEN s.prescription_photo_url IS NOT NULL THEN 1 END) as prescriptions_with_images
FROM sales s
WHERE s.doctor_name IS NOT NULL
GROUP BY s.doctor_name, s.doctor_phone
ORDER BY prescriptions_written DESC;

-- =====================================================
-- 11. LOW STOCK ALERTS
-- =====================================================

-- View medicines with low stock
SELECT 
    medicine_id,
    medicine_name,
    quantity_available,
    unit_price,
    expiry_date
FROM medicines
WHERE quantity_available <= 50
ORDER BY quantity_available;

-- =====================================================
-- 12. EXPIRING MEDICINES
-- =====================================================

-- View medicines expiring soon
SELECT 
    medicine_id,
    medicine_name,
    quantity_available,
    expiry_date,
    DATEDIFF(expiry_date, CURDATE()) as days_until_expiry
FROM medicines
WHERE expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY)
    AND quantity_available > 0
ORDER BY expiry_date;

-- =====================================================
-- 13. RECENT SALES WITH IMAGES (Last 7 days)
-- =====================================================

-- View recent sales with prescription images
SELECT 
    s.sale_id,
    s.sale_date,
    m.medicine_name,
    s.customer_name,
    s.quantity_sold,
    s.total_amount,
    s.prescription_photo_url,
    st.full_name as sold_by_name
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
JOIN staff st ON s.sold_by = st.staff_id
WHERE s.sale_date >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    AND s.prescription_photo_url IS NOT NULL
ORDER BY s.sale_date DESC;

-- =====================================================
-- 14. DATABASE STATISTICS
-- =====================================================

-- View overall database statistics
SELECT 
    'Total Sales' as metric,
    COUNT(*) as value
FROM sales
UNION ALL
SELECT 
    'Sales with Images',
    COUNT(CASE WHEN prescription_photo_url IS NOT NULL THEN 1 END)
FROM sales
UNION ALL
SELECT 
    'Total Medicines',
    COUNT(*)
FROM medicines
UNION ALL
SELECT 
    'Active Staff',
    COUNT(*)
FROM staff
WHERE is_active = 1
UNION ALL
SELECT 
    'Active Admins',
    COUNT(*)
FROM admins
WHERE is_active = 1
UNION ALL
SELECT 
    'Total Revenue',
    CONCAT('$', FORMAT(SUM(total_amount), 2))
FROM sales;

-- =====================================================
-- 15. CREATE VIEWS FOR EASY ACCESS
-- =====================================================

-- Create view for sales with images
CREATE OR REPLACE VIEW sales_with_images AS
SELECT 
    s.sale_id,
    s.sale_date,
    m.medicine_name,
    s.customer_name,
    s.customer_phone,
    s.quantity_sold,
    s.total_amount,
    s.doctor_name,
    s.doctor_phone,
    s.prescription_photo_url,
    st.full_name as sold_by_name
FROM sales s
JOIN medicines m ON s.medicine_id = m.medicine_id
JOIN staff st ON s.sold_by = st.staff_id
WHERE s.prescription_photo_url IS NOT NULL;

-- Create view for medicine inventory status
CREATE OR REPLACE VIEW medicine_inventory_status AS
SELECT 
    medicine_id,
    medicine_name,
    batch_number,
    quantity_available,
    unit_price,
    manufacturer,
    category,
    expiry_date,
    CASE 
        WHEN expiry_date < CURDATE() THEN 'EXPIRED'
        WHEN expiry_date <= DATE_ADD(CURDATE(), INTERVAL 30 DAY) THEN 'EXPIRING SOON'
        ELSE 'VALID'
    END as expiry_status
FROM medicines;

-- =====================================================
-- 16. USEFUL QUERIES FOR DAILY OPERATIONS
-- =====================================================

-- Today's sales
SELECT 
    COUNT(*) as today_sales,
    SUM(total_amount) as today_revenue
FROM sales 
WHERE DATE(sale_date) = CURDATE();

-- This month's sales
SELECT 
    COUNT(*) as month_sales,
    SUM(total_amount) as month_revenue
FROM sales 
WHERE MONTH(sale_date) = MONTH(CURDATE()) 
    AND YEAR(sale_date) = YEAR(CURDATE());

-- Sales by current staff member (replace 'MOHAMMED HANZALA' with actual staff name)
SELECT 
    COUNT(*) as staff_sales,
    SUM(total_amount) as staff_revenue
FROM sales s
JOIN staff st ON s.sold_by = st.staff_id
WHERE st.full_name = 'MOHAMMED HANZALA'
    AND DATE(s.sale_date) = CURDATE();

-- =====================================================
-- END OF SCRIPTS
-- =====================================================

-- To use these scripts:
-- 1. Open MySQL Workbench or phpMyAdmin
-- 2. Copy and paste any section above
-- 3. Execute the query
-- 4. For images, the prescription_photo_url column contains the image URLs
-- 5. You can click on the URLs to view the images in your browser 