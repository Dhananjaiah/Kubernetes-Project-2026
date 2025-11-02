from flask import Flask, render_template_string, jsonify
import requests
import os

app = Flask(__name__)

BACKEND_URL = os.getenv('BACKEND_URL', 'http://backend-service:5000')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>E-Commerce Frontend</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .products {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .product-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .product-card h3 {
            color: #2c3e50;
            margin-top: 0;
        }
        .price {
            color: #27ae60;
            font-size: 1.2em;
            font-weight: bold;
        }
        .status {
            padding: 10px;
            background-color: #e8f5e9;
            border-radius: 5px;
            margin: 20px 0;
            text-align: center;
        }
        .error {
            background-color: #ffebee;
            color: #c62828;
        }
    </style>
</head>
<body>
    <h1>🛒 E-Commerce Microservices Platform</h1>
    <div class="status {{ status_class }}">
        <strong>Environment:</strong> {{ environment }}<br>
        <strong>Backend Status:</strong> {{ backend_status }}
    </div>
    <div class="products" id="products">
        {% for product in products %}
        <div class="product-card">
            <h3>{{ product.name }}</h3>
            <p>{{ product.description }}</p>
            <p class="price">${{ product.price }}</p>
            <p><strong>Stock:</strong> {{ product.stock }}</p>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    try:
        response = requests.get(f'{BACKEND_URL}/api/products', timeout=5)
        products = response.json()
        backend_status = 'Connected ✓'
        status_class = ''
    except Exception as e:
        products = []
        backend_status = f'Disconnected ✗ ({str(e)})'
        status_class = 'error'
    
    environment = os.getenv('ENVIRONMENT', 'development')
    
    return render_template_string(
        HTML_TEMPLATE,
        products=products,
        backend_status=backend_status,
        environment=environment,
        status_class=status_class
    )

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'frontend'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
