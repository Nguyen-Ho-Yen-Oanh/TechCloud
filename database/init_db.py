import sqlite3
import os

def init_database():
    """Chỉ tạo bảng nếu chưa có"""
    conn = sqlite3.connect('warranty.db')
    cursor = conn.cursor()
    
    # Tạo bảng products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            imei TEXT UNIQUE NOT NULL,
            product_name TEXT,
            brand TEXT,
            model TEXT,
            color TEXT,
            storage TEXT,
            customer_name TEXT,
            customer_phone TEXT,
            customer_email TEXT,
            purchase_date TEXT,
            warranty_months INTEGER,
            warranty_end_date TEXT,
            price REAL,
            store_location TEXT,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database schema created successfully!")

if __name__ == '__main__':
    init_database()