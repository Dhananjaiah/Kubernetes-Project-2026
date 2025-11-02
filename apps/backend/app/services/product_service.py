"""
Product service - business logic for product operations
"""
import logging
from typing import List, Optional

from app.models.product import Product
from app.services.database import DatabaseService


class ProductService:
    """Service for product-related operations"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.logger = logging.getLogger(__name__)
    
    def get_all_products(self) -> List[Product]:
        """Get all products from database"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('SELECT id, name, description, price, stock, created_at FROM products ORDER BY id')
                rows = cur.fetchall()
                products = [Product.from_db_row(row) for row in rows]
                self.logger.info(f"Retrieved {len(products)} products")
                return products
        except Exception as e:
            self.logger.error(f"Error fetching products: {e}")
            raise
    
    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get a specific product by ID"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    'SELECT id, name, description, price, stock, created_at FROM products WHERE id = %s',
                    (product_id,)
                )
                row = cur.fetchone()
                if row:
                    product = Product.from_db_row(row)
                    self.logger.info(f"Retrieved product {product_id}")
                    return product
                else:
                    self.logger.warning(f"Product {product_id} not found")
                    return None
        except Exception as e:
            self.logger.error(f"Error fetching product {product_id}: {e}")
            raise
    
    def get_stats(self) -> dict:
        """Get product statistics"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('SELECT COUNT(*) as total_products, SUM(stock) as total_stock FROM products')
                stats = cur.fetchone()
                self.logger.info("Retrieved product stats")
                return dict(stats)
        except Exception as e:
            self.logger.error(f"Error fetching stats: {e}")
            raise
    
    def create_product(self, name: str, description: str, price: float, stock: int) -> Product:
        """Create a new product"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''INSERT INTO products (name, description, price, stock) 
                       VALUES (%s, %s, %s, %s) RETURNING id, name, description, price, stock, created_at''',
                    (name, description, price, stock)
                )
                row = cur.fetchone()
                product = Product.from_db_row(row)
                self.logger.info(f"Created product {product.id}")
                return product
        except Exception as e:
            self.logger.error(f"Error creating product: {e}")
            raise
    
    def update_product(self, product_id: int, name: str = None, description: str = None, 
                       price: float = None, stock: int = None) -> Optional[Product]:
        """Update an existing product"""
        try:
            # Build dynamic update query
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if description is not None:
                updates.append("description = %s")
                params.append(description)
            if price is not None:
                updates.append("price = %s")
                params.append(price)
            if stock is not None:
                updates.append("stock = %s")
                params.append(stock)
            
            if not updates:
                return self.get_product_by_id(product_id)
            
            params.append(product_id)
            query = f"UPDATE products SET {', '.join(updates)} WHERE id = %s RETURNING id, name, description, price, stock, created_at"
            
            with self.db.get_cursor() as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                if row:
                    product = Product.from_db_row(row)
                    self.logger.info(f"Updated product {product_id}")
                    return product
                else:
                    self.logger.warning(f"Product {product_id} not found for update")
                    return None
        except Exception as e:
            self.logger.error(f"Error updating product {product_id}: {e}")
            raise
    
    def delete_product(self, product_id: int) -> bool:
        """Delete a product"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('DELETE FROM products WHERE id = %s', (product_id,))
                deleted = cur.rowcount > 0
                if deleted:
                    self.logger.info(f"Deleted product {product_id}")
                else:
                    self.logger.warning(f"Product {product_id} not found for deletion")
                return deleted
        except Exception as e:
            self.logger.error(f"Error deleting product {product_id}: {e}")
            raise
