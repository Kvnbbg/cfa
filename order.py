from src.models.base import BaseModel, OrderStatus, PaymentStatus, db
from sqlalchemy import JSON
import uuid

class Order(BaseModel):
    """Modèle commande avec gestion des paiements"""
    __tablename__ = 'orders'
    
    # Identifiants
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Montants
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0)
    shipping_amount = db.Column(db.Numeric(10, 2), default=0)
    discount_amount = db.Column(db.Numeric(10, 2), default=0)
    final_amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    
    # Statuts
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    
    # Intégrations Stripe
    stripe_payment_intent_id = db.Column(db.Text)
    stripe_session_id = db.Column(db.Text)
    
    # Adresses (stockées en JSON)
    shipping_address = db.Column(JSON)
    billing_address = db.Column(JSON)
    
    # Livraison
    tracking_number = db.Column(db.String(100))
    notes = db.Column(db.Text)
    
    # Relations
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.order_number:
            self.order_number = self.generate_order_number()
    
    @staticmethod
    def generate_order_number():
        """Génère un numéro de commande unique"""
        return f"CFA-{uuid.uuid4().hex[:8].upper()}"
    
    @property
    def item_count(self):
        """Nombre total d'articles dans la commande"""
        return sum(item.quantity for item in self.items)
    
    @property
    def can_be_cancelled(self):
        """Vérifie si la commande peut être annulée"""
        return self.status in [OrderStatus.PENDING, OrderStatus.CONFIRMED]
    
    @property
    def is_paid(self):
        """Vérifie si la commande est payée"""
        return self.payment_status == PaymentStatus.PAID
    
    def calculate_totals(self):
        """Recalcule les totaux de la commande"""
        self.total_amount = sum(item.total_price for item in self.items)
        self.final_amount = self.total_amount + self.tax_amount + self.shipping_amount - self.discount_amount
    
    def add_item(self, product, quantity, unit_price=None):
        """Ajoute un article à la commande"""
        if unit_price is None:
            unit_price = product.effective_price
        
        # Vérifier si l'article existe déjà
        existing_item = next((item for item in self.items if item.product_id == product.id), None)
        
        if existing_item:
            existing_item.quantity += quantity
            existing_item.total_price = existing_item.quantity * existing_item.unit_price
        else:
            item = OrderItem(
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=quantity * unit_price,
                product_snapshot=product.to_dict()
            )
            self.items.append(item)
        
        self.calculate_totals()
    
    def remove_item(self, product_id):
        """Retire un article de la commande"""
        self.items = [item for item in self.items if item.product_id != product_id]
        self.calculate_totals()
    
    def to_dict(self, include_items=True):
        """Convertit la commande en dictionnaire"""
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'tax_amount': float(self.tax_amount) if self.tax_amount else None,
            'shipping_amount': float(self.shipping_amount) if self.shipping_amount else None,
            'discount_amount': float(self.discount_amount) if self.discount_amount else None,
            'final_amount': float(self.final_amount) if self.final_amount else None,
            'currency': self.currency,
            'status': self.status.value,
            'payment_status': self.payment_status.value,
            'shipping_address': self.shipping_address,
            'billing_address': self.billing_address,
            'tracking_number': self.tracking_number,
            'notes': self.notes,
            'item_count': self.item_count,
            'can_be_cancelled': self.can_be_cancelled,
            'is_paid': self.is_paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data
    
    def __repr__(self):
        return f'<Order {self.order_number}>'


class OrderItem(BaseModel):
    """Article de commande"""
    __tablename__ = 'order_items'
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Snapshot du produit au moment de la commande
    product_snapshot = db.Column(JSON)
    
    def to_dict(self):
        """Convertit l'article en dictionnaire"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unit_price': float(self.unit_price) if self.unit_price else None,
            'total_price': float(self.total_price) if self.total_price else None,
            'product_snapshot': self.product_snapshot,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'

