"""
Order and OrderItem models
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration"""
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


class OrderItem:
    """Order item model"""
    
    def __init__(self, id: Optional[int] = None, order_id: Optional[int] = None,
                 product_id: int = 0, product_name: str = '', quantity: int = 0,
                 price: float = 0.0):
        self.id = id
        self.order_id = order_id
        self.product_id = product_id
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price),
            'subtotal': float(self.price * self.quantity)
        }
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'OrderItem':
        return cls(
            id=row.get('id'),
            order_id=row.get('order_id'),
            product_id=row.get('product_id'),
            product_name=row.get('product_name', ''),
            quantity=row.get('quantity', 0),
            price=float(row.get('price', 0.0))
        )


class Order:
    """Order model"""
    
    def __init__(self, id: Optional[int] = None, user_id: Optional[int] = None,
                 status: str = OrderStatus.PENDING, total_amount: float = 0.0,
                 shipping_address: str = '', created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None, items: Optional[List[OrderItem]] = None):
        self.id = id
        self.user_id = user_id
        self.status = status
        self.total_amount = total_amount
        self.shipping_address = shipping_address
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.items = items or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'total_amount': float(self.total_amount),
            'shipping_address': self.shipping_address,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'items': [item.to_dict() for item in self.items]
        }
    
    @classmethod
    def from_db_row(cls, row: Dict[str, Any]) -> 'Order':
        return cls(
            id=row.get('id'),
            user_id=row.get('user_id'),
            status=row.get('status', OrderStatus.PENDING),
            total_amount=float(row.get('total_amount', 0.0)),
            shipping_address=row.get('shipping_address', ''),
            created_at=row.get('created_at'),
            updated_at=row.get('updated_at')
        )
    
    def __repr__(self) -> str:
        return f"<Order {self.id}: {self.status}>"
