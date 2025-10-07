from src.models.base import BaseModel, DiscountType, db
from datetime import datetime

class Coupon(BaseModel):
    """Coupons de réduction et promotions"""
    __tablename__ = 'coupons'
    
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Type et valeur de réduction
    discount_type = db.Column(db.Enum(DiscountType), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Conditions d'utilisation
    minimum_amount = db.Column(db.Numeric(10, 2), default=0)
    maximum_discount = db.Column(db.Numeric(10, 2))  # Plafond pour les pourcentages
    
    # Limites d'utilisation
    usage_limit = db.Column(db.Integer)  # Nombre max d'utilisations
    used_count = db.Column(db.Integer, default=0)
    
    # Période de validité
    valid_from = db.Column(db.DateTime)
    valid_until = db.Column(db.DateTime)
    
    # Statut
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def is_valid(self):
        """Vérifie si le coupon est valide"""
        now = datetime.utcnow()
        
        # Vérifier le statut
        if not self.is_active:
            return False
        
        # Vérifier les dates
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        
        # Vérifier les limites d'utilisation
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        return True
    
    @property
    def remaining_uses(self):
        """Nombre d'utilisations restantes"""
        if self.usage_limit:
            return max(0, self.usage_limit - self.used_count)
        return None  # Illimité
    
    def calculate_discount(self, amount):
        """Calcule la réduction pour un montant donné"""
        if not self.is_valid or amount < self.minimum_amount:
            return 0
        
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = (amount * self.discount_value) / 100
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
        else:  # FIXED_AMOUNT
            discount = min(self.discount_value, amount)
        
        return discount
    
    def use_coupon(self):
        """Marque le coupon comme utilisé"""
        if not self.is_valid:
            raise ValueError("Coupon invalide")
        
        self.used_count += 1
        
        # Log de l'utilisation
        from src.models.log import Log
        Log.log_system_action(
            action="coupon_used",
            entity_type="coupon",
            entity_id=self.id,
            meta_data={
                "code": self.code,
                "used_count": self.used_count,
                "remaining_uses": self.remaining_uses
            }
        )
    
    def to_dict(self):
        """Convertit le coupon en dictionnaire"""
        return {
            'id': self.id,
            'code': self.code,
            'description': self.description,
            'discount_type': self.discount_type.value,
            'discount_value': float(self.discount_value) if self.discount_value else None,
            'minimum_amount': float(self.minimum_amount) if self.minimum_amount else None,
            'maximum_discount': float(self.maximum_discount) if self.maximum_discount else None,
            'usage_limit': self.usage_limit,
            'used_count': self.used_count,
            'remaining_uses': self.remaining_uses,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'is_active': self.is_active,
            'is_valid': self.is_valid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Coupon {self.code}>'

