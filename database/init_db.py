import sqlite3

conn = sqlite3.connect('warranty.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imei TEXT UNIQUE NOT NULL,
        product_name TEXT,
        purchase_date TEXT,
        warranty_months INTEGER
    )
''')

products = [
    ('LAPTOP-DELL-001', 'Dell XPS 15', '2026-05-01', 12),
    ('IPHONE15-ABC', 'iPhone 15 Pro', '2026-04-12', 24),
    ('PHONE-IPHONE-15', 'iPhone 15 Plus', '2026-05-20', 24),
    ('SAMSUNG-S24-001', 'Samsung Galaxy S24', '2026-03-15', 12),
    ('LENOVO-T14-002', 'Lenovo ThinkPad T14', '2026-02-28', 18)
]

cursor.executemany('INSERT OR IGNORE INTO products (imei, product_name, purchase_date, warranty_months) VALUES (?,?,?,?)', products)

conn.commit()
conn.close()
print("Database created successfully!")