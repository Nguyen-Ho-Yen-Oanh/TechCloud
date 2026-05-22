from flask import Flask, request, render_template, jsonify
import mysql.connector
import os

app = Flask(__name__)

# Chỉ kết nối trong internal network (private subnet)
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'mysql-db'),  # container name = private subnet
        user=os.environ.get('DB_USER', 'warranty_user'),
        password=os.environ.get('DB_PASSWORD', 'securepass123'),
        database=os.environ.get('DB_NAME', 'warranty_db')
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_warranty', methods=['POST'])
def check_warranty():
    serial = request.form.get('serial')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT * FROM products WHERE imei = %s"
    cursor.execute(query, (serial,))
    result = cursor.fetchone()
    
    cursor.close()
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
    app.run(host='0.0.0.0', port=5000)