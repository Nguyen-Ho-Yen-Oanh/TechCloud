from flask import Flask, request, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('warranty.db')
    conn.row_factory = sqlite3.Row
    return conn

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

if __name__ == '__main__':
    # Kiểm tra database
    if not os.path.exists('warranty.db'):
        print("📦 Database not found! Running init_db.py...")
        os.system("python init_db.py")
        print("🌱 Run 'python seed.py' to add sample data!")
    
    app.run(host='0.0.0.0', port=5000)

    