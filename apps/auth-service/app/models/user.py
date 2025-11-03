"""
User model
"""
from datetime import datetime
from typing import Optional, Dict, Any
import bcrypt


class User:
    """User model for authentication"""
    
    def __init__(self, id: Optional[int] = None, username: str = '', 
                 email: str = '', password_hash: str = '',
                 full_name: str = '', is_active: bool = True,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.full_name = full_name
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
    
    def set_password(self, password: str):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verify password"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self, include_sensitive=False) -> Dict[str, Any]:
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'User':
        """Create User from database row"""
        return cls(
            id=row.get('id'),
            username=row.get('username', ''),
            email=row.get('email', ''),
            password_hash=row.get('password_hash', ''),
            full_name=row.get('full_name', ''),
            is_active=row.get('is_active', True),
            created_at=row.get('created_at')
        )
    
    def __repr__(self) -> str:
        return f"<User {self.id}: {self.username}>"
