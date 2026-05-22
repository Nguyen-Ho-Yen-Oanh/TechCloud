from flask import Flask, request, render_template, jsonify
import sqlite3
import os

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('warranty.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_warranty', methods=['POST'])
def check_warranty():
    serial = request.form.get('serial')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM products WHERE imei = ?", (serial,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        return jsonify({
            'product': result['product_name'],
            'purchase_date': result['purchase_date'],
            'warranty_months': result['warranty_months'],
            'status': 'Còn bảo hành' if result['warranty_months'] > 0 else 'Hết bảo hành'
        })
    else:
        return jsonify({'error': 'Không tìm thấy sản phẩm'}), 404

if __name__ == '__main__':
    # Tạo database nếu chưa có
    if not os.path.exists('warranty.db'):
        exec(open('init_db.py').read())
    app.run(host='0.0.0.0', port=5000)