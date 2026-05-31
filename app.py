from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import ipaddress

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('warranty.db')
    conn.row_factory = sqlite3.Row
    return conn

# 1. Danh sách IP đơn bị chặn (ưu tiên cao nhất)
BLACKLIST_IPS = [
    '10.71.199.150',  # IP test bị chặn
]

# 2. Dải IP được PHÉP truy cập (Whitelist - chỉ các mạng này mới vào được)
ALLOWED_RANGES = [
    '10.71.0.0/16',      # Cho phép toàn bộ dải 10.71.x.x
    '192.168.0.0/16',  # Cho phép toàn bộ dải 192.168.x.x
    '127.0.0.0/8',     # Cho phép localhost (để test local)
]

# 3. Dải IP bị CHẶN (Blacklist range - nếu có)
BLACKLIST_RANGES = [
    # '10.71.0.0/16',
]

def is_ip_in_range(ip, ranges):
    """Kiểm tra IP có nằm trong danh sách các dải không"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        for range_str in ranges:
            if ip_obj in ipaddress.ip_network(range_str, strict=False):
                return True
    except:
        pass
    return False

@app.before_request
def check_access():
    """Chỉ cho phép IP trong dải 10.x và 192.168.x mới được truy cập"""
    client_ip = request.remote_addr
    forwarded_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    
    # Lấy IP thật (qua proxy)
    real_ip = forwarded_ip if forwarded_ip else client_ip
    
    print(f"[ACCESS] IP: {real_ip} - Path: {request.path}")
    
    # 1. Kiểm tra blacklist IP đơn
    if real_ip in BLACKLIST_IPS:
        print(f"[BLOCKED] IP {real_ip} in blacklist")
        return "⚠️ Truy cập bị chặn. IP của bạn nằm trong danh sách đen.", 403
    
    # 2. Kiểm tra blacklist range (nếu có)
    if is_ip_in_range(real_ip, BLACKLIST_RANGES):
        print(f"[BLOCKED] IP {real_ip} in blacklisted range")
        return "⚠️ Truy cập bị chặn. Dải IP của bạn không được phép.", 403
    
    # 3. Kiểm tra whitelist - CHỈ CHO PHÉP IP trong dải 10.x và 192.168.x
    if not is_ip_in_range(real_ip, ALLOWED_RANGES):
        print(f"[BLOCKED] IP {real_ip} not in allowed ranges")
        return f"""
        <h2>⚠️ Truy cập bị từ chối</h2>
        <p>Hệ thống chỉ cho phép truy cập từ mạng nội bộ (10.71.x.x hoặc 192.168.x.x).</p>
        <p>IP của bạn: <strong>{real_ip}</strong></p>
        <p>Vui lòng kết nối qua mạng 10.71.x.x hoặc mạng 192.168.x.x để sử dụng dịch vụ.</p>
        """, 403
    
    # 4. Cho phép truy cập
    print(f"[ALLOWED] IP {real_ip} is allowed")
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_warranty', methods=['POST'])
def check_warranty():
    serial = request.form.get('serial')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE imei = ?", (serial,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'product_name': result['product_name'],
            'brand': result['brand'],
            'model': result['model'],
            'color': result['color'],
            'storage': result['storage'],
            'purchase_date': result['purchase_date'],
            'warranty_end_date': result['warranty_end_date'],
            'price': result['price'],
            'store_location': result['store_location'],
            'warranty_months': result['warranty_months'],
            'status': 'Còn bảo hành' if result['warranty_months'] > 0 else 'Hết bảo hành'
        })
    else:
        return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404

@app.route('/stats')
def stats():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE status = 'active'")
    total_products = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT customer_phone) FROM products")
    total_customers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE warranty_end_date > date('now')")
    active_warranty = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT brand) FROM products")
    total_brands = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'total_products': total_products,
        'total_customers': total_customers,
        'active_warranty': active_warranty,
        'total_brands': total_brands
    })

# Endpoint kiểm tra IP hiện tại
@app.route('/my-ip')
def show_my_ip():
    client_ip = request.remote_addr
    forwarded_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    real_ip = forwarded_ip if forwarded_ip else client_ip
    
    return jsonify({
        'remote_addr': client_ip,
        'forwarded_ip': forwarded_ip,
        'real_ip': real_ip,
        'is_allowed': is_ip_in_range(real_ip, ALLOWED_RANGES),
        'is_blocked': real_ip in BLACKLIST_IPS or is_ip_in_range(real_ip, BLACKLIST_RANGES),
        'allowed_ranges': ALLOWED_RANGES,
        'blacklist_ips': BLACKLIST_IPS,
        'blacklist_ranges': BLACKLIST_RANGES
    })

if __name__ == '__main__':
    # Kiểm tra database
    if not os.path.exists('warranty.db'):
        print("📦 Database not found! Running init_db.py...")
        os.system("python init_db.py")
        print("🌱 Run 'python seed.py' to add sample data!")
    
    app.run(host='0.0.0.0', port=5000)