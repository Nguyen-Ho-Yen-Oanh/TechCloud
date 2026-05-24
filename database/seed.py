import sqlite3
import random
from datetime import datetime, timedelta
import os

# Cấu hình
NUM_PRODUCTS = 100
NUM_FIXED = 10  # 10 sản phẩm cố định
NUM_RANDOM = NUM_PRODUCTS - NUM_FIXED  # 90 sản phẩm random
DB_NAME = 'warranty.db'

# Danh sách sản phẩm mẫu cho phần random
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

# ==================== 10 SẢN PHẨM CỐ ĐỊNH (DỄ NHỚ) ====================
FIXED_PRODUCTS = [
    # iPhone
    ('IPHONE15-ABC123', 'iPhone 15 Pro Max', 'Apple', 'iPhone 15 Pro Max', 
     'Titan Đen', '256GB', 'Nguyễn Văn An', '0901234567', 'an.nguyen@email.com',
     '2026-01-15', 24, '2028-01-15', 33990000, 'Hà Nội', 'active'),
    
    ('IPHONE15-XYZ789', 'iPhone 15 Pro', 'Apple', 'iPhone 15 Pro',
     'Trắng', '128GB', 'Trần Thị Bình', '0912345678', 'binh.tran@email.com',
     '2026-02-20', 24, '2028-02-20', 28990000, 'TP.HCM', 'active'),
    
    # Samsung
    ('SAMSUNG-S24-ULTRA', 'Galaxy S24 Ultra', 'Samsung', 'S24 Ultra',
     'Tím', '512GB', 'Lê Hoàng Nam', '0923456789', 'nam.le@email.com',
     '2026-03-10', 24, '2028-03-10', 30990000, 'Đà Nẵng', 'active'),
    
    ('SAMSUNG-TAB-S9', 'Samsung Tab S9 Ultra', 'Samsung', 'Tab S9 Ultra',
     'Be', '512GB', 'Trần Hưng Đạo', '0912345678', 'dao.tran@email.com',
     '2026-02-28', 24, '2028-02-28', 27990000, 'TP.HCM', 'active'),
    
    # Laptop
    ('LAPTOP-DELL-XPS15', 'Dell XPS 15', 'Dell', 'XPS 15',
     'Bạc', '1TB SSD', 'Ngô Thị Lan', '0956789012', 'lan.ngo@email.com',
     '2025-11-10', 12, '2026-11-10', 45990000, 'Hà Nội', 'active'),
    
    ('LAPTOP-MAC-M3', 'MacBook Pro M3', 'Apple', 'MacBook Pro',
     'Xám', '512GB', 'Đỗ Minh Quân', '0967890123', 'quan.do@email.com',
     '2026-02-14', 24, '2028-02-14', 39990000, 'TP.HCM', 'active'),
    
    # Tablet
    ('IPAD-PRO-M4', 'iPad Pro M4', 'Apple', 'iPad Pro',
     'Xám', '256GB', 'Lý Thường Kiệt', '0901234567', 'kiet.ly@email.com',
     '2026-04-10', 24, '2028-04-10', 24990000, 'Hà Nội', 'active'),
    
    # Phụ kiện
    ('AIRPODS-PRO-2', 'AirPods Pro 2', 'Apple', 'AirPods Pro',
     'Trắng', '64GB', 'Võ Thị Sáu', '0923456789', 'sau.vo@email.com',
     '2026-05-01', 12, '2027-05-01', 5990000, 'Đà Nẵng', 'active'),
    
    ('GALAXY-BUDS-2', 'Samsung Galaxy Buds2 Pro', 'Samsung', 'Galaxy Buds',
     'Tím', '32GB', 'Nguyễn Thị Minh Khai', '0934567890', 'khai.nguyen@email.com',
     '2026-03-15', 12, '2027-03-15', 4490000, 'Cần Thơ', 'active'),
    
    ('XIAOMI-14T-PRO', 'Xiaomi 14T Pro', 'Xiaomi', '14T Pro',
     'Đen', '256GB', 'Phạm Thị Hoa', '0934567890', 'hoa.pham@email.com',
     '2026-04-05', 24, '2028-04-05', 13990000, 'Hải Phòng', 'active'),
]

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

def generate_random_product(index):
    """Tạo sản phẩm random"""
    template = random.choice(PRODUCT_TEMPLATES)
    product_name, model, base_price = template
    brand = product_name.split()[0]
    
    imei = f"{brand.upper()}-{model.replace(' ', '-')}-RAND{index:04d}"
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
    print(f"   📌 {NUM_FIXED} sản phẩm cố định (IMEI dễ nhớ)")
    print(f"   🎲 {NUM_RANDOM} sản phẩm ngẫu nhiên")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ nếu có
    cursor.execute("DELETE FROM products")
    
    all_products = []
    
    # 1. Thêm 10 sản phẩm cố định
    print("\n📌 Đang thêm sản phẩm cố định...")
    for product in FIXED_PRODUCTS:
        all_products.append(product)
    print(f"   ✅ Đã thêm {len(FIXED_PRODUCTS)} sản phẩm cố định")
    
    # 2. Thêm 90 sản phẩm random
    print("\n🎲 Đang thêm sản phẩm ngẫu nhiên...")
    for i in range(1, NUM_RANDOM + 1):
        product = generate_random_product(i)
        all_products.append(product)
        
        if i % 20 == 0:
            print(f"   Đã tạo {i}/{NUM_RANDOM} sản phẩm random...")
    
    # Insert toàn bộ vào database
    cursor.executemany('''
        INSERT INTO products 
        (imei, product_name, brand, model, color, storage, customer_name, 
         customer_phone, customer_email, purchase_date, warranty_months, 
         warranty_end_date, price, store_location, status)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', all_products)
    
    conn.commit()
    
    # Thống kê
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    # Lấy 10 IMEI mẫu (ưu tiên sản phẩm cố định)
    cursor.execute("SELECT imei, product_name FROM products LIMIT 15")
    samples = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ Thành công! Đã tạo {count} sản phẩm.")
    print("\n" + "="*50)
    print("📱 IMEI CỐ ĐỊNH ĐỂ TEST (copy và paste vào web):")
    print("="*50)
    for product in FIXED_PRODUCTS[:10]:
        print(f"   ✅ {product[0]} - {product[1]}")
    
    print("\n" + "="*50)
    print("🎲 MỘT SỐ IMEI RANDOM (cũng có thể test):")
    print("="*50)
    for imei, name in samples[:5]:
        if not any(imei == p[0] for p in FIXED_PRODUCTS):
            print(f"   🎲 {imei} - {name}")
    
    return True

if __name__ == '__main__':
    seed_database()