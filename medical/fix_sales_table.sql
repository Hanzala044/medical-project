-- Fix sales table structure for Razorpay integration
USE medicos_pharmacy;

-- Check if columns exist and add them if they don't
-- Add rate_per_tablet column if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'medicos_pharmacy' 
     AND TABLE_NAME = 'sales' 
     AND COLUMN_NAME = 'rate_per_tablet') = 0,
    'ALTER TABLE sales ADD COLUMN rate_per_tablet DECIMAL(10,2) AFTER quantity_sold',
    'SELECT "rate_per_tablet column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add payment_id column if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'medicos_pharmacy' 
     AND TABLE_NAME = 'sales' 
     AND COLUMN_NAME = 'payment_id') = 0,
    'ALTER TABLE sales ADD COLUMN payment_id VARCHAR(100) AFTER sold_by',
    'SELECT "payment_id column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add order_id column if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'medicos_pharmacy' 
     AND TABLE_NAME = 'sales' 
     AND COLUMN_NAME = 'order_id') = 0,
    'ALTER TABLE sales ADD COLUMN order_id VARCHAR(100) AFTER payment_id',
    'SELECT "order_id column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add payment_status column if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'medicos_pharmacy' 
     AND TABLE_NAME = 'sales' 
     AND COLUMN_NAME = 'payment_status') = 0,
    'ALTER TABLE sales ADD COLUMN payment_status ENUM("pending", "completed", "failed") DEFAULT "pending" AFTER order_id',
    'SELECT "payment_status column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add payment_method column if it doesn't exist
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'medicos_pharmacy' 
     AND TABLE_NAME = 'sales' 
     AND COLUMN_NAME = 'payment_method') = 0,
    'ALTER TABLE sales ADD COLUMN payment_method VARCHAR(50) DEFAULT "razorpay" AFTER payment_status',
    'SELECT "payment_method column already exists" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Remove doctor_phone column if it exists (since we removed it from the form)
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'medicos_pharmacy' 
     AND TABLE_NAME = 'sales' 
     AND COLUMN_NAME = 'doctor_phone') > 0,
    'ALTER TABLE sales DROP COLUMN doctor_phone',
    'SELECT "doctor_phone column does not exist" as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Update existing records to set default values
UPDATE sales SET rate_per_tablet = unit_price WHERE rate_per_tablet IS NULL;
UPDATE sales SET payment_status = 'completed' WHERE payment_status IS NULL;

-- Show the final table structure
DESCRIBE sales; 