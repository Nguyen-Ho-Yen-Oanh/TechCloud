import sqlite3
import random
from datetime import datetime, timedelta
import os

# Cấu hình
NUM_PRODUCTS = 100  # Số lượng sản phẩm muốn tạo
DB_NAME = 'warranty.db'

# Danh sách sản phẩm mẫu (định dạng chuẩn: tên_sản_phẩm, model, giá)
PRODUCT_TEMPLATES = [
    # Apple
    ('iPhone 15 Pro Max', 'iPhone 15 Pro Max', 33990000),
    ('iPhone 15 Pro', 'iPhone 15 Pro', 28990000),
    ('iPhone 15 Plus', 'iPhone 15 Plus', 24990000),
    ('iPhone 14', 'iPhone 14', 19990000),
    ('MacBook Pro M3', 'MacBook Pro', 39990000),
    ('MacBook Air M2', 'MacBook Air', 25990000),
    ('iPad Pro M4', 'iPad Pro', 24990000),
    ('iPad Air', 'iPad Air', 18990000),
    ('AirPods Pro 2', 'AirPods Pro', 5990000),
    ('AirPods Max', 'AirPods Max', 12990000),
    ('Apple Watch Ultra', 'Watch Ultra', 15990000),
    
    # Samsung
    ('Galaxy S24 Ultra', 'S24 Ultra', 30990000),
    ('Galaxy S24 Plus', 'S24 Plus', 25990000),
    ('Galaxy Z Fold5', 'Z Fold5', 40990000),
    ('Galaxy Z Flip5', 'Z Flip5', 25990000),
    ('Tab S9 Ultra', 'Tab S9 Ultra', 27990000),
    ('Tab S9+', 'Tab S9+', 21990000),
    ('Galaxy Buds2 Pro', 'Buds2 Pro', 4490000),
    ('Galaxy Watch 6', 'Watch 6', 8990000),
    
    # Xiaomi
    ('14T Pro', '14T Pro', 13990000),
    ('13T Pro', '13T Pro', 11990000),
    ('Redmi Note 13 Pro', 'Note 13 Pro', 8990000),
    ('Pad 6', 'Pad 6', 8990000),
    ('Mi Band 8', 'Band 8', 899000),
    
    # OPPO
    ('Find X7 Ultra', 'Find X7', 24990000),
    ('Find N3 Flip', 'Find N3', 19990000),
    ('Reno11 Pro', 'Reno11', 11990000),
    
    # Vivo
    ('X100 Pro', 'X100', 19990000),
    ('V30 Pro', 'V30', 12990000),
    
    # Google
    ('Pixel 8 Pro', 'Pixel 8 Pro', 26990000),
    ('Pixel 8', 'Pixel 8', 19990000),
    ('Pixel Fold', 'Pixel Fold', 35990000),
    
    # OnePlus
    ('OnePlus 12', '12', 20990000),
    ('OnePlus 12R', '12R', 16990000),
    ('OnePlus Open', 'Open', 39990000),
    
    # Dell
    ('Dell XPS 15', 'XPS 15', 45990000),
    ('Dell XPS 13', 'XPS 13', 35990000),
    ('Dell Inspiron 14', 'Inspiron 14', 17990000),
    ('Dell Latitude 5440', 'Latitude 5440', 28990000),
    
    # HP
    ('HP EliteBook 1040', 'EliteBook 1040', 32990000),
    ('HP Pavilion 15', 'Pavilion 15', 18990000),
    ('HP Spectre x360', 'Spectre x360', 34990000),
    ('HP Victus 16', 'Victus 16', 22990000),
    
    # Lenovo
    ('Lenovo ThinkPad T14', 'ThinkPad T14', 25990000),
    ('Lenovo Legion 5 Pro', 'Legion 5', 27990000),
    ('Lenovo Yoga 9i', 'Yoga 9i', 29990000),
    ('Lenovo IdeaPad 5', 'IdeaPad 5', 14990000),
    
    # ASUS
    ('ASUS ROG Strix G16', 'ROG Strix', 28990000),
    ('ASUS TUF A15', 'TUF A15', 24990000),
    ('ASUS Zenbook 14', 'Zenbook 14', 21990000),
    ('ASUS Vivobook 15', 'Vivobook 15', 15990000),
    
    # Acer
    ('Acer Predator Helios 16', 'Predator Helios', 42990000),
    ('Acer Swift 3', 'Swift 3', 17990000),
    ('Acer Aspire 5', 'Aspire 5', 13990000),
    
    # MSI
    ('MSI Stealth 14', 'Stealth 14', 35990000),
    ('MSI Katana 15', 'Katana 15', 28990000),
    
    # Microsoft
    ('Surface Laptop 6', 'Surface Laptop', 31990000),
    ('Surface Pro 10', 'Surface Pro', 27990000),
    
    # Sony
    ('Sony WH-1000XM5', 'WH-1000XM5', 8990000),
    ('Sony WF-1000XM5', 'WF-1000XM5', 5990000),
    
    # JBL
    ('JBL Live Pro 2', 'Live Pro 2', 3990000),
    ('JBL Tune 230NC', 'Tune 230NC', 2490000),
]

# Danh sách mẫu
COLORS = ['Đen', 'Trắng', 'Xám', 'Bạc', 'Vàng Gold', 'Hồng', 'Xanh Dương', 'Xanh Lá', 'Tím', 'Đỏ', 'Cam', 'Xanh Mint']
STORAGES = ['64GB', '128GB', '256GB', '512GB', '1TB', '2TB', '512GB SSD', '1TB SSD', '2TB SSD']
LOCATIONS = ['Hà Nội', 'TP.HCM', 'Đà Nẵng', 'Hải Phòng', 'Cần Thơ', 'Biên Hòa', 'Nha Trang', 'Huế', 'Bình Dương', 'Vũng Tàu', 'Đà Lạt', 'Hạ Long']
STATUSES = ['active', 'active', 'active', 'active', 'expired', 'active', 'active', 'active']  # 75% active

# Họ tên mẫu
FIRST_NAMES = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Vũ', 'Đặng', 'Bùi', 'Đỗ', 'Hồ', 'Võ', 'Phùng', 'Trịnh', 'Ngô', 'Mai', 'Đinh', 'Lưu', 'Lý', 'Tạ', 'Chu', 'Đoàn', 'Lương']
MIDDLE_NAMES = ['Văn', 'Thị', 'Đức', 'Minh', 'Thanh', 'Ngọc', 'Hữu', 'Quang', 'Tuấn', 'Hồng', 'Kim', 'Bảo', 'Gia', 'Hoài', 'Xuân', 'Anh', 'Phương', 'Mỹ', 'Công', 'Quốc']
LAST_NAMES = ['An', 'Bình', 'Hoa', 'Mai', 'Lan', 'Hùng', 'Dũng', 'Cường', 'Linh', 'Thảo', 'Hương', 'Trang', 'Huyền', 'Phúc', 'Khoa', 'Đạt', 'Quân', 'Nam', 'Việt', 'Long', 'Thịnh', 'Phát']

def random_date(start_year=2024, end_year=2026):
    """Tạo ngày random trong khoảng thời gian"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_phone():
    """Tạo số điện thoại ngẫu nhiên"""
    return f"09{random.randint(10000000, 99999999)}"

def random_customer_name():
    """Tạo tên khách hàng ngẫu nhiên"""
    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)
    return f"{first} {middle} {last}"

def random_email(name):
    """Tạo email từ tên"""
    name_clean = name.replace(' ', '.').lower()
    name_clean = name_clean.replace('đ', 'd')
    domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'email.com', 'techcloud.vn']
    return f"{name_clean}@{random.choice(domains)}"

def generate_product(index):
    """Tạo một sản phẩm ngẫu nhiên"""
    # Chọn ngẫu nhiên một template sản phẩm
    template = random.choice(PRODUCT_TEMPLATES)
    product_name = template[0]
    model = template[1]
    base_price = template[2]
    
    # Lấy brand từ tên sản phẩm
    brand = product_name.split()[0]
    if brand == 'iPhone' or brand == 'MacBook' or brand == 'iPad' or brand == 'AirPods' or brand == 'Apple':
        brand = 'Apple'
    elif brand == 'Galaxy' or brand == 'Tab' or brand == 'Buds' or brand == 'Watch':
        brand = 'Samsung'
    elif brand == 'Redmi' or brand == 'Mi':
        brand = 'Xiaomi'
    
    # Tạo IMEI
    imei = f"{brand.upper()}-{model.replace(' ', '-')}-{index:04d}"
    
    # Ngày mua và bảo hành
    purchase_date = random_date(2024, 2026)
    warranty_months = random.choice([12, 18, 24])
    warranty_end = purchase_date + timedelta(days=warranty_months * 30)
    
    # Giá (random trong khoảng ±20% giá gốc)
    price = int(base_price * random.uniform(0.85, 1.2))
    
    # Các thuộc tính khác
    color = random.choice(COLORS)
    storage = random.choice(STORAGES)
    location = random.choice(LOCATIONS)
    status = random.choice(STATUSES)
    
    # Cập nhật status dựa trên ngày hết hạn
    if datetime.now() > warranty_end:
        status = 'expired'
    else:
        status = 'active'
    
    # Khách hàng
    customer_name = random_customer_name()
    customer_phone = random_phone()
    customer_email = random_email(customer_name)
    
    return (
        imei,
        product_name,
        brand,
        model,
        color,
        storage,
        customer_name,
        customer_phone,
        customer_email,
        purchase_date.strftime('%Y-%m-%d'),
        warranty_months,
        warranty_end.strftime('%Y-%m-%d'),
        price,
        location,
        status
    )

def seed_database(num_products=100):
    """Seed database với số lượng sản phẩm chỉ định"""
    
    # Kiểm tra database đã có bảng chưa
    if not os.path.exists(DB_NAME):
        print("❌ Database not found! Please run init_db.py first.")
        return False
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Xóa dữ liệu cũ
    confirm = input(f"⚠️  This will replace all data with {num_products} new products. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Seeding cancelled.")
        return False
    
    cursor.execute("DELETE FROM products")
    
    # Reset auto-increment
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='products'")
    
    # Generate products
    products = []
    for i in range(1, num_products + 1):
        product = generate_product(i)
        products.append(product)
        
        # Progress indicator
        if i % 20 == 0:
            print(f"📦 Generated {i}/{num_products} products...")
    
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
    
    cursor.execute("SELECT COUNT(DISTINCT brand) FROM products")
    brand_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE status = 'active'")
    active_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE status = 'expired'")
    expired_count = cursor.fetchone()[0]
    
    # Lấy 5 sản phẩm mẫu
    cursor.execute("SELECT imei, product_name FROM products LIMIT 5")
    sample_products = cursor.fetchall()
    
    conn.close()
    
    print(f"\n✅ Seeding completed successfully!")
    print(f"📊 Total products: {count}")
    print(f"🏷️  Total brands: {brand_count}")
    print(f"🟢 Active warranties: {active_count}")
    print(f"🔴 Expired warranties: {expired_count}")
    print(f"\n📝 Sample IMEI codes to test:")
    for imei, name in sample_products:
        print(f"   - {imei} ({name})")
    
    return True

if __name__ == '__main__':
    print("🌱 TECHCLOUD DATABASE SEEDER")
    print("=" * 40)
    
    # Chạy init database trước nếu cần
    if not os.path.exists(DB_NAME):
        print("📦 Database not found. Running init_db.py first...")
        os.system("python init_db.py")
    
    # Seed database
    seed_database(NUM_PRODUCTS)