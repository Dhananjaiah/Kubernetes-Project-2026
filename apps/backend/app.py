from flask import Flask, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv('DB_HOST', 'postgres-service')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'ecommerce')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')

def get_db_connection():
    """Get database connection with retry logic"""
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                cursor_factory=RealDictCursor
            )
            return conn
        except psycopg2.OperationalError as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise e

def init_db():
    """Initialize database with sample data"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create products table if not exists
        cur.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                price DECIMAL(10, 2) NOT NULL,
                stock INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if products exist
        cur.execute('SELECT COUNT(*) FROM products')
        count = cur.fetchone()['count']
        
        if count == 0:
            # Insert sample products
            products = [
                ('Laptop Pro', 'High-performance laptop for professionals', 1299.99, 15),
                ('Wireless Mouse', 'Ergonomic wireless mouse with precision tracking', 29.99, 50),
                ('Mechanical Keyboard', 'RGB mechanical keyboard with cherry switches', 149.99, 30),
                ('USB-C Hub', '7-in-1 USB-C hub with HDMI and ethernet', 49.99, 40),
                ('Webcam HD', '1080p HD webcam with auto-focus', 79.99, 25),
                ('Monitor 27"', '4K IPS monitor with HDR support', 399.99, 20)
            ]
            
            for product in products:
                cur.execute(
                    'INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)',
                    product
                )
        
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, name, description, price, stock FROM products ORDER BY id')
        products = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify(products), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT id, name, description, price, stock FROM products WHERE id = %s', (product_id,))
        product = cur.fetchone()
        cur.close()
        conn.close()
        
        if product:
            return jsonify(product), 200
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        db_status = 'connected'
    except Exception as e:
        db_status = f'disconnected: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'service': 'backend',
        'database': db_status,
        'environment': os.getenv('ENVIRONMENT', 'development')
    }), 200

@app.route('/api/stats')
def stats():
    """Get database statistics"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT COUNT(*) as total_products, SUM(stock) as total_stock FROM products')
        stats = cur.fetchone()
        cur.close()
        conn.close()
        
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize database on startup
if __name__ == '__main__':
    print("Initializing database...")
    time.sleep(5)  # Wait for database to be ready
    if init_db():
        print("Database initialized successfully")
    else:
        print("Warning: Database initialization failed")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
