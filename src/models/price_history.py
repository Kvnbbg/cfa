from src.models.base import BaseModel, db
from sqlalchemy import JSON

class PriceHistory(BaseModel):
    """Historique des changements de prix"""
    __tablename__ = 'price_history'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    old_price = db.Column(db.Numeric(10, 2))
    new_price = db.Column(db.Numeric(10, 2), nullable=False)
    change_reason = db.Column(db.String(255))
    algorithm_used = db.Column(db.String(100))
    market_data = db.Column(JSON)  # Données de marché utilisées pour le calcul
    
    @property
    def price_change(self):
        """Calcule le changement de prix"""
        if self.old_price:
            return self.new_price - self.old_price
        return 0
    
    @property
    def price_change_percentage(self):
        """Calcule le pourcentage de changement"""
        if self.old_price and self.old_price > 0:
            return ((self.new_price - self.old_price) / self.old_price) * 100
        return 0
    
    def to_dict(self):
        """Convertit l'historique en dictionnaire"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'old_price': float(self.old_price) if self.old_price else None,
            'new_price': float(self.new_price) if self.new_price else None,
            'price_change': float(self.price_change),
            'price_change_percentage': round(self.price_change_percentage, 2),
            'change_reason': self.change_reason,
            'algorithm_used': self.algorithm_used,
            'market_data': self.market_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<PriceHistory {self.product_id}: {self.old_price} -> {self.new_price}>'


class CompetitorPrice(BaseModel):
    """Prix des concurrents pour analyse de marché"""
    __tablename__ = 'competitor_prices'
    
    product_name = db.Column(db.String(255), nullable=False)
    competitor_name = db.Column(db.String(100), nullable=False)
    competitor_price = db.Column(db.Numeric(10, 2), nullable=False)
    competitor_url = db.Column(db.Text)
    our_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), index=True)
    scraped_at = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        """Convertit le prix concurrent en dictionnaire"""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'competitor_name': self.competitor_name,
            'competitor_price': float(self.competitor_price) if self.competitor_price else None,
            'competitor_url': self.competitor_url,
            'our_product_id': self.our_product_id,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<CompetitorPrice {self.competitor_name}: {self.competitor_price}>'

