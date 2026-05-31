from flask import Flask, request, render_template, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import sqlite3
import os

app = Flask(__name__)
# Giới hạn mặc định: mỗi IP được 100 request/phút, tối đa 10 request/giây
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per minute", "10 per second"]
)

def get_db():
    conn = sqlite3.connect('warranty.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@limiter.limit("200 per minute")  # Trang chủ: 200 request/phút/IP
def index():
    return render_template('index.html')

@app.route('/check_warranty', methods=['POST'])
@limiter.limit("30 per minute")   # API tra cứu: 30 lần/phút/IP (chặn brute force)
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
@limiter.limit("60 per minute")   # API thống kê: 60 lần/phút/IP
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

# Danh sách IP bị chặn (có thể lưu vào file hoặc database)
BLACKLIST_IPS = [
    '10.71.199.150',  # IP của máy tấn công
    # '123.456.789.0',  # Ví dụ IP cần chặn
    # '111.222.333.444',
]

@app.before_request
def block_ip():
    """Chặn các IP nằm trong blacklist"""
    client_ip = request.remote_addr
    if client_ip in BLACKLIST_IPS:
        return "⚠️ Truy cập bị chặn. Liên hệ admin để được hỗ trợ.", 403

# ========== XỬ LÝ LỖI QUÁ TẢI (Rate Limit Exceeded) ==========
@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Khi người dùng vượt quá giới hạn request"""
    return jsonify({
        'error': 'Quá nhiều request! Vui lòng thử lại sau 1 phút.',
        'retry_after': 60
    }), 429

if __name__ == '__main__':
    # Kiểm tra database
    if not os.path.exists('warranty.db'):
        print("📦 Database not found! Running init_db.py...")
        os.system("python init_db.py")
        print("🌱 Run 'python seed.py' to add sample data!")
    
    app.run(host='0.0.0.0', port=5000)