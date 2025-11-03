"""
Product model
"""
from datetime import datetime
from typing import Optional, List, Dict, Any


class Product:
    """Product model representing a product in the database"""
    
    def __init__(self, id: Optional[int] = None, name: str = '', 
                 description: str = '', price: float = 0.0, 
                 stock: int = 0, created_at: Optional[datetime] = None):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'stock': self.stock,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Product':
        """Create Product instance from database row"""
        return cls(
            id=row.get('id'),
            name=row.get('name', ''),
            description=row.get('description', ''),
            price=float(row.get('price', 0.0)),
            stock=row.get('stock', 0),
            created_at=row.get('created_at')
        )
    
    def __repr__(self) -> str:
        return f"<Product {self.id}: {self.name}>"
