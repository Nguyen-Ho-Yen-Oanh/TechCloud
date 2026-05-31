from flask import Flask, request, render_template, jsonify
import sqlite3
import os
import ipaddress

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('warranty.db')
    conn.row_factory = sqlite3.Row
    return conn

# 1. IP đơn bị chặn (kẻ tấn công)
BLACKLIST_IPS = [
    # '10.71.199.150',  # Không chặn nữa
]

# 2. Dải IP được PHÉP truy cập (Tất cả IP Việt Nam)
# Tham khảo dải IP các nhà mạng Việt Nam (nguồn: VNNIC)
ALLOWED_RANGES = [
    # Viettel
    '113.160.0.0/11',
    '115.72.0.0/13',
    '118.68.0.0/14',
    '125.234.0.0/15',
    '203.162.0.0/15',
    '171.251.0.0/16',
    
    # Mobifone
    '14.160.0.0/12',
    '14.176.0.0/12',
    '27.64.0.0/12',
    '27.72.0.0/13',
    
    # VinaPhone
    '27.64.0.0/12',
    '27.72.0.0/13',
    '42.112.0.0/13',
    '42.118.0.0/16',
    '42.119.0.0/16',
    '42.120.0.0/15',
    
    # FPT Telecom
    '58.186.0.0/15',
    '123.16.0.0/12',
    '123.24.0.0/13',
    
    # VNPT
    '117.0.0.0/12',
    '118.68.0.0/14',
    '171.224.0.0/13',
    '171.232.0.0/13',
    
    # CMC Telecom
    '203.210.0.0/15',
    
    # SCTV
    '113.161.0.0/16',
    
    # Localhost (để test)
    '127.0.0.0/8',
    '10.0.0.0/8',      
    '192.168.0.0/16',
]

BLACKLIST_RANGES = [
    # '113.160.1.0/24',
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

def is_vietnam_ip(ip):
    """Kiểm tra có phải IP Việt Nam không"""
    return is_ip_in_range(ip, ALLOWED_RANGES)

@app.before_request
def check_access():
    """Chỉ cho phép IP Việt Nam truy cập, chặn IP quốc tế"""
    client_ip = request.remote_addr
    forwarded_ip = request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
    
    # Lấy IP thật (qua proxy)
    real_ip = forwarded_ip if forwarded_ip else client_ip
    
    print(f"[ACCESS] IP: {real_ip} - Path: {request.path}")
    
    # 1. Kiểm tra blacklist IP đơn
    if real_ip in BLACKLIST_IPS:
        print(f"[BLOCKED] IP {real_ip} in blacklist")
        return "⚠️ Truy cập bị chặn. IP của bạn nằm trong danh sách đen.", 403
    
    # 2. Kiểm tra blacklist range
    if is_ip_in_range(real_ip, BLACKLIST_RANGES):
        print(f"[BLOCKED] IP {real_ip} in blacklisted range")
        return "⚠️ Truy cập bị chặn. Dải IP của bạn không được phép.", 403
    
    # 3. Kiểm tra có phải IP Việt Nam không
    if not is_vietnam_ip(real_ip):
        print(f"[BLOCKED] IP {real_ip} is not in Vietnam ranges")
        return """
        <h2>⚠️ Truy cập bị từ chối</h2>
        <p>Dịch vụ chỉ khả dụng tại Việt Nam.</p>
        <p>IP của bạn: <strong>{}</strong></p>
        <p>Vui lòng sử dụng mạng Internet tại Việt Nam (Viettel, Mobifone, VinaPhone, FPT, VNPT...)</p>
        <p><a href="/my-ip">Xem chi tiết IP của bạn</a></p>
        """.format(real_ip), 403
    
    # 4. Cho phép truy cập
    print(f"[ALLOWED] IP {real_ip} is in Vietnam")
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
    
    # Xác định nhà mạng gần đúng
    carrier = "Không xác định"
    if is_ip_in_range(real_ip, ['113.160.0.0/11', '115.72.0.0/13', '118.68.0.0/14', '125.234.0.0/15']):
        carrier = "Viettel"
    elif is_ip_in_range(real_ip, ['14.160.0.0/12', '14.176.0.0/12', '27.64.0.0/12']):
        carrier = "Mobifone"
    elif is_ip_in_range(real_ip, ['27.72.0.0/13', '42.112.0.0/13']):
        carrier = "VinaPhone"
    elif is_ip_in_range(real_ip, ['58.186.0.0/15', '123.16.0.0/12']):
        carrier = "FPT Telecom"
    elif is_ip_in_range(real_ip, ['117.0.0.0/12']):
        carrier = "VNPT"
    
    return jsonify({
        'remote_addr': client_ip,
        'forwarded_ip': forwarded_ip,
        'real_ip': real_ip,
        'carrier': carrier,
        'is_vietnam': is_vietnam_ip(real_ip),
        'is_blocked': real_ip in BLACKLIST_IPS or is_ip_in_range(real_ip, BLACKLIST_RANGES),
        'message': "✅ IP Việt Nam - Được phép truy cập" if is_vietnam_ip(real_ip) else "❌ IP quốc tế - Bị chặn"
    })

if __name__ == '__main__':
    # Kiểm tra database
    if not os.path.exists('warranty.db'):
        print("📦 Database not found! Running init_db.py...")
        os.system("python init_db.py")
        print("🌱 Run 'python seed.py' to add sample data!")
    
    app.run(host='0.0.0.0', port=5000)