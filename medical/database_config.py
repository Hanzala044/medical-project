import os
import psycopg2
from psycopg2 import Error
import mysql.connector
from mysql.connector import Error as MySQLError

# Database type - can be 'postgresql' or 'mysql'
DB_TYPE = os.getenv('DB_TYPE', 'postgresql').lower()

# PostgreSQL Configuration (for hosting)
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'database': os.getenv('POSTGRES_DB', 'medicos_pharmacy'),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

# MySQL Configuration (for local development)
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'root'),
    'database': os.getenv('MYSQL_DB', 'medicos_pharmacy')
}

def get_db_connection():
    """Create and return database connection based on DB_TYPE"""
    try:
        if DB_TYPE == 'postgresql':
            connection = psycopg2.connect(**POSTGRES_CONFIG)
            print("✅ Connected to PostgreSQL database")
        else:
            connection = mysql.connector.connect(**MYSQL_CONFIG)
            print("✅ Connected to MySQL database")
        return connection
    except (Error, MySQLError) as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def get_cursor(connection):
    """Get cursor with appropriate error handling"""
    if DB_TYPE == 'postgresql':
        return connection.cursor()
    else:
        return connection.cursor()

def execute_query(cursor, query, params=None):
    """Execute query with appropriate error handling"""
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return True
    except (Error, MySQLError) as e:
        print(f"❌ Error executing query: {e}")
        return False

def fetch_all(cursor):
    """Fetch all results"""
    return cursor.fetchall()

def fetch_one(cursor):
    """Fetch one result"""
    return cursor.fetchone()

def get_last_row_id(cursor):
    """Get last inserted row ID"""
    if DB_TYPE == 'postgresql':
        return cursor.fetchone()[0] if cursor.fetchone() else None
    else:
        return cursor.lastrowid 