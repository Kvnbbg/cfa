"""
Modèles de base de données pour l'application CFA
"""

from src.models.base import db, BaseModel, UserRole, ProductCategory, OrderStatus, PaymentStatus, DiscountType
from src.models.user import User
from src.models.product import Product
from src.models.order import Order, OrderItem
from src.models.price_history import PriceHistory, CompetitorPrice
from src.models.review import Review
from src.models.log import Log
from src.models.coupon import Coupon

# Liste de tous les modèles pour faciliter les imports
__all__ = [
    'db',
    'BaseModel',
    'UserRole',
    'ProductCategory', 
    'OrderStatus',
    'PaymentStatus',
    'DiscountType',
    'User',
    'Product',
    'Order',
    'OrderItem',
    'PriceHistory',
    'CompetitorPrice',
    'Review',
    'Log',
    'Coupon'
]

