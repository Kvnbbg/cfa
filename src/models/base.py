from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class UserRole(Enum):
    BUYER = "buyer"
    SELLER = "seller"
    ADMIN = "admin"

class ProductCategory(Enum):
    FOOD = "food"
    SPICES = "spices"
    HERBS = "herbs"
    ALCOHOL = "alcohol"
    DRINKS = "drinks"
    MEDICAL_HERBS = "medical_herbs"

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

class DiscountType(Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"

class BaseModel(db.Model):
    """Modèle de base avec timestamps automatiques"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

