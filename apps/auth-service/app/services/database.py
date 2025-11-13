"""
Database service for connection management
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import logging
from typing import Optional
from contextlib import contextmanager

from app.config import Config


class DatabaseService:
    """Database connection and query management"""
    
    def __init__(self, config: Config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._connection = None
    
    def get_connection(self, max_retries: int = 3, retry_delay: int = 2):
        """Get database connection with retry logic"""
        for attempt in range(max_retries):
            try:
                conn = psycopg2.connect(
                    host=self.config.DB_HOST,
                    port=self.config.DB_PORT,
                    database=self.config.DB_NAME,
                    user=self.config.DB_USER,
                    password=self.config.DB_PASSWORD,
                    cursor_factory=RealDictCursor
                )
                self.logger.info("Database connection established")
                return conn
            except psycopg2.OperationalError as e:
                self.logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    self.logger.error("Failed to connect to database after all retries")
                    raise
    
    @contextmanager
    def get_cursor(self):
        """Context manager for database cursor"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Database error: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def init_database(self) -> bool:
        """Initialize database with tables and sample data"""
        try:
            with self.get_cursor() as cur:
                # Check if products table exists first to avoid SERIAL sequence conflicts
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'products'
                    )
                """)
                table_exists = cur.fetchone()['exists']
                
                if not table_exists:
                    # Create products table
                    cur.execute('''
                        CREATE TABLE products (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            price DECIMAL(10, 2) NOT NULL,
                            stock INTEGER NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    self.logger.info("Products table created")
                else:
                    self.logger.info("Products table already exists")
                
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
                    self.logger.info(f"Inserted {len(products)} sample products")
            
            self.logger.info("Database initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            return False
    
    def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            with self.get_cursor() as cur:
                cur.execute('SELECT 1')
            return True
        except Exception:
            return False
