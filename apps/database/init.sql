-- Initialize ecommerce database

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_price ON products(price);

-- Insert sample data
INSERT INTO products (name, description, price, stock) VALUES
    ('Laptop Pro', 'High-performance laptop for professionals', 1299.99, 15),
    ('Wireless Mouse', 'Ergonomic wireless mouse with precision tracking', 29.99, 50),
    ('Mechanical Keyboard', 'RGB mechanical keyboard with cherry switches', 149.99, 30),
    ('USB-C Hub', '7-in-1 USB-C hub with HDMI and ethernet', 49.99, 40),
    ('Webcam HD', '1080p HD webcam with auto-focus', 79.99, 25),
    ('Monitor 27"', '4K IPS monitor with HDR support', 399.99, 20)
ON CONFLICT DO NOTHING;
