import sqlite3
import random
from datetime import datetime, timedelta
import os

# Cấu hình
NUM_PRODUCTS = 100
DB_NAME = 'warranty.db'  # Tạo trong thư mục hiện tại

# Danh sách sản phẩm mẫu
PRODUCT_TEMPLATES = [
    ('iPhone 15 Pro Max', 'iPhone 15 Pro Max', 33990000),
    ('iPhone 15 Pro', 'iPhone 15 Pro', 28990000),
    ('Galaxy S24 Ultra', 'S24 Ultra', 30990000),
    ('MacBook Pro M3', 'MacBook Pro', 39990000),
    ('Dell XPS 15', 'XPS 15', 45990000),
    ('iPad Pro M4', 'iPad Pro', 24990000),
    ('AirPods Pro 2', 'AirPods Pro', 5990000),
    ('Samsung Tab S9 Ultra', 'Tab S9 Ultra', 27990000),
    ('Xiaomi 14T Pro', '14T Pro', 13990000),
    ('ASUS ROG Strix G16', 'ROG Strix', 28990000),
    ('Lenovo ThinkPad T14', 'ThinkPad T14', 25990000),
    ('HP EliteBook 1040', 'EliteBook 1040', 32990000),
    ('Google Pixel 8 Pro', 'Pixel 8 Pro', 26990000),
    ('OnePlus 12', '12', 20990000),
    ('OPPO Find X7 Ultra', 'Find X7', 24990000),
]

COLORS = ['Đen', 'Trắng', 'Xám', 'Bạc', 'Xanh Dương', 'Tím', 'Vàng']
STORAGES = ['128GB', '256GB', '512GB', '1TB', '2TB']
LOCATIONS = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ']

FIRST_NAMES = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đặng', 'Bùi']
MIDDLE_NAMES = ['Văn', 'Thị', 'Minh', 'Thanh', 'Hữu', 'Quang', 'Ngọc']
LAST_NAMES = ['An', 'Bình', 'Hoa', 'Mai', 'Lan', 'Hùng', 'Dũng', 'Linh']

def random_date():
    start = datetime(2024, 1, 1)
    end = datetime(2026, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_phone():
    return f"09{random.randint(10000000, 99999999)}"

def random_customer_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(MIDDLE_NAMES)} {random.choice(LAST_NAMES)}"

def random_email(name):
    name_clean = name.replace(' ', '.').lower()
    return f"{name_clean}@gmail.com"

def generate_product(index):
    template = random.choice(PRODUCT_TEMPLATES)
    product_name, model, base_price = template
    brand = product_name.split()[0]
    
    imei = f"{brand.upper()}-{model.replace(' ', '-')}-{index:04d}"
    purchase_date = random_date()
    warranty_months = random.choice([12, 18, 24])
    warranty_end = purchase_date + timedelta(days=warranty_months * 30)
    price = int(base_price * random.uniform(0.85, 1.15))
    
    return (
        imei, product_name, brand, model,
        random.choice(COLORS), random.choice(STORAGES),
        random_customer_name(), random_phone(), random_email(random_customer_name()),
        purchase_date.strftime('%Y-%m-%d'), warranty_months, warranty_end.strftime('%Y-%m-%d'),
        price, random.choice(LOCATIONS),
        'active'
    )

def seed_database():
    print(f"🌱 Đang tạo {NUM_PRODUCTS} sản phẩm...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ nếu có
    cursor.execute("DELETE FROM products")
    
    # Tạo sản phẩm
    products = []
    for i in range(1, NUM_PRODUCTS + 1):
        product = generate_product(i)
        products.append(product)
        
        if i % 20 == 0:
            print(f"   Đã tạo {i}/{NUM_PRODUCTS} sản phẩm...")
    
    # Insert vào database
    cursor.executemany('''
        INSERT INTO products 
        (imei, product_name, brand, model, color, storage, customer_name, 
         customer_phone, customer_email, purchase_date, warranty_months, 
         warranty_end_date, price, store_location, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', products)
    
    conn.commit()
    
    # Thống kê
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    cursor.execute("SELECT imei, product_name FROM products LIMIT 10")
    samples = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ Thành công! Đã tạo {count} sản phẩm.")
    print("\n📱 10 IMEI mẫu để test:")
    for imei, name in samples:
        print(f"   - {imei} ({name})")
    
    return True

if __name__ == '__main__':
    seed_database()