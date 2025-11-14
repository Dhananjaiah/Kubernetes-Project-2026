"""
Inventory service - stock management logic
"""
import logging
from typing import Optional, List

from app.models.inventory import InventoryItem
from app.services.database import DatabaseService


class InventoryService:
    """Service for inventory operations"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.logger = logging.getLogger(__name__)
    
    def init_tables(self) -> bool:
        """Initialize inventory table"""
        try:
            with self.db.get_cursor() as cur:
                # Check if table exists first to avoid SERIAL sequence conflicts
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'inventory'
                    )
                """)
                table_exists = cur.fetchone()['exists']
                
                if not table_exists:
                    cur.execute('''
                        CREATE TABLE inventory (
                            id SERIAL PRIMARY KEY,
                            product_id INTEGER UNIQUE NOT NULL,
                            quantity INTEGER NOT NULL DEFAULT 0,
                            reserved INTEGER NOT NULL DEFAULT 0,
                            available INTEGER GENERATED ALWAYS AS (quantity - reserved) STORED,
                            warehouse_location VARCHAR(100),
                            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    self.logger.info("Inventory table created")
                else:
                    self.logger.info("Inventory table already exists")
                
                # Create index (idempotent with IF NOT EXISTS)
                cur.execute('CREATE INDEX IF NOT EXISTS idx_inventory_product_id ON inventory(product_id)')
                
                self.logger.info("Inventory table initialized")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing tables: {e}")
            return False
    
    def get_inventory_by_product_id(self, product_id: int) -> Optional[InventoryItem]:
        """Get inventory for a product"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('SELECT * FROM inventory WHERE product_id = %s', (product_id,))
                row = cur.fetchone()
                return InventoryItem.from_db_row(row) if row else None
        except Exception as e:
            self.logger.error(f"Error fetching inventory: {e}")
            raise
    
    def get_all_inventory(self) -> List[InventoryItem]:
        """Get all inventory items"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('SELECT * FROM inventory ORDER BY product_id')
                rows = cur.fetchall()
                return [InventoryItem.from_db_row(row) for row in rows]
        except Exception as e:
            self.logger.error(f"Error fetching inventory: {e}")
            raise
    
    def update_inventory(self, product_id: int, quantity: int, warehouse_location: str = '') -> Optional[InventoryItem]:
        """Update or create inventory"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''INSERT INTO inventory (product_id, quantity, warehouse_location)
                       VALUES (%s, %s, %s)
                       ON CONFLICT (product_id) DO UPDATE
                       SET quantity = EXCLUDED.quantity,
                           warehouse_location = COALESCE(EXCLUDED.warehouse_location, inventory.warehouse_location),
                           last_updated = CURRENT_TIMESTAMP
                       RETURNING id, product_id, quantity, reserved, available, warehouse_location, last_updated''',
                    (product_id, quantity, warehouse_location)
                )
                row = cur.fetchone()
                item = InventoryItem.from_db_row(row)
                self.logger.info(f"Updated inventory for product {product_id}")
                return item
        except Exception as e:
            self.logger.error(f"Error updating inventory: {e}")
            raise
    
    def reserve_inventory(self, product_id: int, quantity: int) -> bool:
        """Reserve inventory for an order"""
        try:
            with self.db.get_cursor() as cur:
                # Check availability
                cur.execute('SELECT available FROM inventory WHERE product_id = %s', (product_id,))
                row = cur.fetchone()
                
                if not row or row['available'] < quantity:
                    self.logger.warning(f"Insufficient inventory for product {product_id}")
                    return False
                
                # Reserve
                cur.execute(
                    '''UPDATE inventory 
                       SET reserved = reserved + %s, last_updated = CURRENT_TIMESTAMP
                       WHERE product_id = %s''',
                    (quantity, product_id)
                )
                self.logger.info(f"Reserved {quantity} units for product {product_id}")
                return True
        except Exception as e:
            self.logger.error(f"Error reserving inventory: {e}")
            raise
    
    def release_inventory(self, product_id: int, quantity: int) -> bool:
        """Release reserved inventory"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''UPDATE inventory 
                       SET reserved = GREATEST(reserved - %s, 0), last_updated = CURRENT_TIMESTAMP
                       WHERE product_id = %s''',
                    (quantity, product_id)
                )
                self.logger.info(f"Released {quantity} units for product {product_id}")
                return True
        except Exception as e:
            self.logger.error(f"Error releasing inventory: {e}")
            raise
    
    def adjust_inventory(self, product_id: int, adjustment: int) -> Optional[InventoryItem]:
        """Adjust inventory quantity (can be positive or negative)"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''UPDATE inventory 
                       SET quantity = GREATEST(quantity + %s, 0), last_updated = CURRENT_TIMESTAMP
                       WHERE product_id = %s
                       RETURNING id, product_id, quantity, reserved, available, warehouse_location, last_updated''',
                    (adjustment, product_id)
                )
                row = cur.fetchone()
                if row:
                    item = InventoryItem.from_db_row(row)
                    self.logger.info(f"Adjusted inventory for product {product_id} by {adjustment}")
                    return item
                return None
        except Exception as e:
            self.logger.error(f"Error adjusting inventory: {e}")
            raise
