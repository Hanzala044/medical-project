#!/usr/bin/env python3
"""
Test script for PostgreSQL database connection and setup
"""

import os
from database_config import get_db_connection, get_cursor, execute_query, fetch_all, fetch_one

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    
    try:
        connection = get_db_connection()
        if connection:
            print("✅ Database connection successful!")
            cursor = get_cursor(connection)
            
            # Test basic query
            execute_query(cursor, "SELECT version()")
            version = fetch_one(cursor)
            print(f"📊 Database version: {version[0] if version else 'Unknown'}")
            
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ Database connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing database connection: {e}")
        return False

def test_schema_setup():
    """Test if tables exist"""
    print("\n🔍 Testing schema setup...")
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = get_cursor(connection)
            
            # Check if tables exist
            tables = ['admins', 'staff', 'medicines', 'sales']
            
            for table in tables:
                execute_query(cursor, f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                exists = fetch_one(cursor)
                if exists and exists[0]:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' does not exist")
            
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ Cannot test schema - no database connection!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing schema: {e}")
        return False

def test_sample_data():
    """Test if sample data exists"""
    print("\n🔍 Testing sample data...")
    
    try:
        connection = get_db_connection()
        if connection:
            cursor = get_cursor(connection)
            
            # Check admin count
            execute_query(cursor, "SELECT COUNT(*) FROM admins")
            admin_count = fetch_one(cursor)
            print(f"👥 Admins: {admin_count[0] if admin_count else 0}")
            
            # Check staff count
            execute_query(cursor, "SELECT COUNT(*) FROM staff")
            staff_count = fetch_one(cursor)
            print(f"👨‍💼 Staff: {staff_count[0] if staff_count else 0}")
            
            # Check medicines count
            execute_query(cursor, "SELECT COUNT(*) FROM medicines")
            medicine_count = fetch_one(cursor)
            print(f"💊 Medicines: {medicine_count[0] if medicine_count else 0}")
            
            cursor.close()
            connection.close()
            return True
        else:
            print("❌ Cannot test data - no database connection!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing sample data: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 PostgreSQL Database Test Suite")
    print("=" * 40)
    
    # Test connection
    connection_ok = test_database_connection()
    
    if connection_ok:
        # Test schema
        schema_ok = test_schema_setup()
        
        if schema_ok:
            # Test data
            data_ok = test_sample_data()
            
            print("\n" + "=" * 40)
            if connection_ok and schema_ok and data_ok:
                print("🎉 All tests passed! PostgreSQL setup is ready.")
            else:
                print("⚠️ Some tests failed. Check the output above.")
        else:
            print("\n⚠️ Schema test failed. Run init_database() first.")
    else:
        print("\n❌ Database connection failed. Check your configuration.")

if __name__ == "__main__":
    main() 