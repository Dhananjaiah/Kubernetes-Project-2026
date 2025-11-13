"""
Order service - business logic for order operations
"""
import logging
from typing import List, Optional, Dict
import requests

from app.models.order import Order, OrderItem, OrderStatus
from app.services.database import DatabaseService


class OrderService:
    """Service for order operations"""
    
    def __init__(self, db_service: DatabaseService, product_service_url: str, inventory_service_url: str):
        self.db = db_service
        self.product_service_url = product_service_url
        self.inventory_service_url = inventory_service_url
        self.logger = logging.getLogger(__name__)
    
    def init_tables(self) -> bool:
        """Initialize order tables"""
        try:
            with self.db.get_cursor() as cur:
                # Orders table
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        status VARCHAR(20) DEFAULT 'pending',
                        total_amount DECIMAL(10, 2) NOT NULL,
                        shipping_address TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Order items table
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS order_items (
                        id SERIAL PRIMARY KEY,
                        order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
                        product_id INTEGER NOT NULL,
                        product_name VARCHAR(255),
                        quantity INTEGER NOT NULL,
                        price DECIMAL(10, 2) NOT NULL
                    )
                ''')
                
                # Indexes
                cur.execute('CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id)')
                
                self.logger.info("Order tables initialized")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing tables: {e}")
            return False
    
    def create_order(self, user_id: Optional[int], items: List[Dict], shipping_address: str) -> Optional[Order]:
        """Create a new order"""
        try:
            # Calculate total and validate products
            total_amount = 0.0
            validated_items = []
            
            for item in items:
                product_id = item['product_id']
                quantity = item['quantity']
                
                # Fetch product details
                try:
                    response = requests.get(f"{self.product_service_url}/api/products/{product_id}", timeout=5)
                    if response.status_code != 200:
                        self.logger.warning(f"Product {product_id} not found")
                        return None
                    
                    product = response.json()
                    price = product['price']
                    product_name = product['name']
                    
                    validated_items.append({
                        'product_id': product_id,
                        'product_name': product_name,
                        'quantity': quantity,
                        'price': price
                    })
                    
                    total_amount += price * quantity
                except Exception as e:
                    self.logger.error(f"Error fetching product {product_id}: {e}")
                    return None
            
            # Create order
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''INSERT INTO orders (user_id, status, total_amount, shipping_address)
                       VALUES (%s, %s, %s, %s)
                       RETURNING id, user_id, status, total_amount, shipping_address, created_at, updated_at''',
                    (user_id, OrderStatus.PENDING, total_amount, shipping_address)
                )
                row = cur.fetchone()
                order = Order.from_db_row(row)
                
                # Create order items
                for item in validated_items:
                    cur.execute(
                        '''INSERT INTO order_items (order_id, product_id, product_name, quantity, price)
                           VALUES (%s, %s, %s, %s, %s)
                           RETURNING id, order_id, product_id, product_name, quantity, price''',
                        (order.id, item['product_id'], item['product_name'], item['quantity'], item['price'])
                    )
                    item_row = cur.fetchone()
                    order.items.append(OrderItem.from_db_row(item_row))
                
                self.logger.info(f"Created order {order.id}")
                return order
        except Exception as e:
            self.logger.error(f"Error creating order: {e}")
            raise
    
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Get order by ID with items"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('SELECT * FROM orders WHERE id = %s', (order_id,))
                row = cur.fetchone()
                
                if not row:
                    return None
                
                order = Order.from_db_row(row)
                
                # Get order items
                cur.execute('SELECT * FROM order_items WHERE order_id = %s', (order_id,))
                items = cur.fetchall()
                order.items = [OrderItem.from_db_row(item) for item in items]
                
                return order
        except Exception as e:
            self.logger.error(f"Error fetching order {order_id}: {e}")
            raise
    
    def get_orders_by_user(self, user_id: int) -> List[Order]:
        """Get all orders for a user"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC', (user_id,))
                rows = cur.fetchall()
                
                orders = []
                for row in rows:
                    order = Order.from_db_row(row)
                    
                    # Get order items
                    cur.execute('SELECT * FROM order_items WHERE order_id = %s', (order.id,))
                    items = cur.fetchall()
                    order.items = [OrderItem.from_db_row(item) for item in items]
                    
                    orders.append(order)
                
                return orders
        except Exception as e:
            self.logger.error(f"Error fetching orders for user {user_id}: {e}")
            raise
    
    def update_order_status(self, order_id: int, status: str) -> Optional[Order]:
        """Update order status"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''UPDATE orders SET status = %s, updated_at = CURRENT_TIMESTAMP
                       WHERE id = %s
                       RETURNING id, user_id, status, total_amount, shipping_address, created_at, updated_at''',
                    (status, order_id)
                )
                row = cur.fetchone()
                
                if row:
                    order = Order.from_db_row(row)
                    self.logger.info(f"Updated order {order_id} status to {status}")
                    return order
                return None
        except Exception as e:
            self.logger.error(f"Error updating order {order_id}: {e}")
            raise
