"""
Authentication service - user management and authentication logic
"""
import logging
from typing import Optional, Dict, Any
from flask_jwt_extended import create_access_token, create_refresh_token

from app.models.user import User
from app.services.database import DatabaseService


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
        self.logger = logging.getLogger(__name__)
    
    def init_users_table(self) -> bool:
        """Initialize users table"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        full_name VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes
                cur.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
                cur.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
                
                self.logger.info("Users table initialized")
            return True
        except Exception as e:
            self.logger.error(f"Error initializing users table: {e}")
            return False
    
    def register_user(self, username: str, email: str, password: str, 
                      full_name: str = '') -> Optional[User]:
        """Register a new user"""
        try:
            # Check if user exists
            if self.get_user_by_username(username):
                self.logger.warning(f"Username {username} already exists")
                return None
            
            if self.get_user_by_email(email):
                self.logger.warning(f"Email {email} already exists")
                return None
            
            # Create user
            user = User(username=username, email=email, full_name=full_name)
            user.set_password(password)
            
            with self.db.get_cursor() as cur:
                cur.execute(
                    '''INSERT INTO users (username, email, password_hash, full_name)
                       VALUES (%s, %s, %s, %s)
                       RETURNING id, username, email, password_hash, full_name, is_active, created_at''',
                    (user.username, user.email, user.password_hash, user.full_name)
                )
                row = cur.fetchone()
                user = User.from_db_row(row)
                self.logger.info(f"User {username} registered successfully")
                return user
        except Exception as e:
            self.logger.error(f"Error registering user: {e}")
            raise
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, str]]:
        """Authenticate user and return JWT tokens"""
        try:
            user = self.get_user_by_username(username)
            
            if not user:
                self.logger.warning(f"User {username} not found")
                return None
            
            if not user.is_active:
                self.logger.warning(f"User {username} is inactive")
                return None
            
            if not user.check_password(password):
                self.logger.warning(f"Invalid password for user {username}")
                return None
            
            # Generate tokens
            identity = {'user_id': user.id, 'username': user.username}
            access_token = create_access_token(identity=identity)
            refresh_token = create_refresh_token(identity=identity)
            
            self.logger.info(f"User {username} authenticated successfully")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_dict()
            }
        except Exception as e:
            self.logger.error(f"Error authenticating user: {e}")
            raise
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    'SELECT * FROM users WHERE username = %s',
                    (username,)
                )
                row = cur.fetchone()
                return User.from_db_row(row) if row else None
        except Exception as e:
            self.logger.error(f"Error fetching user by username: {e}")
            raise
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    'SELECT * FROM users WHERE email = %s',
                    (email,)
                )
                row = cur.fetchone()
                return User.from_db_row(row) if row else None
        except Exception as e:
            self.logger.error(f"Error fetching user by email: {e}")
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        try:
            with self.db.get_cursor() as cur:
                cur.execute(
                    'SELECT * FROM users WHERE id = %s',
                    (user_id,)
                )
                row = cur.fetchone()
                return User.from_db_row(row) if row else None
        except Exception as e:
            self.logger.error(f"Error fetching user by ID: {e}")
            raise
