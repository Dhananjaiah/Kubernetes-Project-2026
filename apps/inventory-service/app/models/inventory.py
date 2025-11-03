"""
Inventory model
"""
from datetime import datetime
from typing import Optional, Dict, Any


class InventoryItem:
    """Inventory item model"""
    
    def __init__(self, id: Optional[int] = None, product_id: int = 0,
                 quantity: int = 0, reserved: int = 0, available: int = 0,
                 warehouse_location: str = '', last_updated: Optional[datetime] = None):
        self.id = id
        self.product_id = product_id
        self.quantity = quantity
        self.reserved = reserved
        self.available = available or (quantity - reserved)
        self.warehouse_location = warehouse_location
        self.last_updated = last_updated or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'reserved': self.reserved,
            'available': self.available,
            'warehouse_location': self.warehouse_location,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'InventoryItem':
        return cls(
            id=row.get('id'),
            product_id=row.get('product_id'),
            quantity=row.get('quantity', 0),
            reserved=row.get('reserved', 0),
            available=row.get('available', 0),
            warehouse_location=row.get('warehouse_location', ''),
            last_updated=row.get('last_updated')
        )
    
    def __repr__(self) -> str:
        return f"<InventoryItem product_id={self.product_id}, available={self.available}>"
