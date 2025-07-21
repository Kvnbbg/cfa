from src.models.base import BaseModel, ProductCategory, db
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import JSON
from datetime import date

class Product(BaseModel):
    """Modèle produit avec gestion écologique et tarification"""
    __tablename__ = 'products'
    
    # Informations de base
    name = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text)
    short_description = db.Column(db.String(500))
    
    # Origine et catégorie
    origin_country = db.Column(db.String(100), index=True)
    origin_region = db.Column(db.String(100))
    category = db.Column(db.Enum(ProductCategory), nullable=False, index=True)
    subcategory = db.Column(db.String(100))
    
    # Tarification
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    discounted_price = db.Column(db.Numeric(10, 2))
    cost_price = db.Column(db.Numeric(10, 2))  # Prix d'achat pour calcul de marge
    
    # Stock et logistique
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    min_stock_level = db.Column(db.Integer, default=5, nullable=False)
    weight = db.Column(db.Numeric(8, 2))  # Poids en kg
    unit = db.Column(db.String(20), default='kg')
    
    # Médias
    image_url = db.Column(db.Text)
    # Pour SQLite, on utilise JSON au lieu d'ARRAY
    gallery_images = db.Column(JSON)  # Liste d'URLs d'images
    
    # Vendeur
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Aspects écologiques
    ecology_score = db.Column(db.Integer, default=0)  # Score de 0 à 100
    fair_trade = db.Column(db.Boolean, default=False)
    organic = db.Column(db.Boolean, default=False)
    carbon_footprint = db.Column(db.Numeric(8, 2))  # kg CO2
    
    # Statut et visibilité
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    featured = db.Column(db.Boolean, default=False)
    
    # Métadonnées
    tags = db.Column(JSON)  # Liste de tags
    nutritional_info = db.Column(JSON)  # Informations nutritionnelles
    storage_instructions = db.Column(db.Text)
    expiry_date = db.Column(db.Date)
    
    # Relations
    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    reviews = db.relationship('Review', backref='product', lazy=True)
    price_history = db.relationship('PriceHistory', backref='product', lazy=True)
    competitor_prices = db.relationship('CompetitorPrice', backref='our_product', lazy=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.current_price:
            self.current_price = self.base_price
        if not self.gallery_images:
            self.gallery_images = []
        if not self.tags:
            self.tags = []
    
    @property
    def effective_price(self):
        """Prix effectif (avec réduction si applicable)"""
        return self.discounted_price if self.discounted_price else self.current_price
    
    @property
    def discount_percentage(self):
        """Pourcentage de réduction"""
        if self.discounted_price and self.current_price:
            return round(((self.current_price - self.discounted_price) / self.current_price) * 100, 2)
        return 0
    
    @property
    def is_low_stock(self):
        """Vérifie si le stock est faible"""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def is_in_stock(self):
        """Vérifie si le produit est en stock"""
        return self.stock_quantity > 0
    
    @property
    def average_rating(self):
        """Note moyenne du produit"""
        if self.reviews:
            return sum(review.rating for review in self.reviews) / len(self.reviews)
        return 0
    
    @property
    def review_count(self):
        """Nombre d'avis"""
        return len(self.reviews)
    
    def calculate_margin(self):
        """Calcule la marge bénéficiaire"""
        if self.cost_price:
            return ((self.effective_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    def update_price(self, new_price, reason="Manual update", algorithm_used=None):
        """Met à jour le prix et enregistre l'historique"""
        from src.models.price_history import PriceHistory
        
        # Enregistrer l'historique
        history = PriceHistory(
            product_id=self.id,
            old_price=self.current_price,
            new_price=new_price,
            change_reason=reason,
            algorithm_used=algorithm_used
        )
        db.session.add(history)
        
        # Mettre à jour le prix
        self.current_price = new_price
        self.updated_at = db.func.now()
    
    def add_stock(self, quantity, reason="Stock addition"):
        """Ajoute du stock"""
        from src.models.log import Log
        
        old_quantity = self.stock_quantity
        self.stock_quantity += quantity
        
        # Log de l'opération
        log = Log(
            user_id=None,  # Peut être défini par l'appelant
            action="stock_addition",
            entity_type="product",
            entity_id=self.id,
            old_values={"stock_quantity": old_quantity},
            new_values={"stock_quantity": self.stock_quantity},
            meta_data={"reason": reason, "quantity_added": quantity}
        )
        db.session.add(log)
    
    def remove_stock(self, quantity, reason="Stock removal"):
        """Retire du stock"""
        from src.models.log import Log
        
        if quantity > self.stock_quantity:
            raise ValueError("Quantité insuffisante en stock")
        
        old_quantity = self.stock_quantity
        self.stock_quantity -= quantity
        
        # Log de l'opération
        log = Log(
            user_id=None,
            action="stock_removal",
            entity_type="product",
            entity_id=self.id,
            old_values={"stock_quantity": old_quantity},
            new_values={"stock_quantity": self.stock_quantity},
            meta_data={"reason": reason, "quantity_removed": quantity}
        )
        db.session.add(log)
    
    def to_dict(self, include_seller=False):
        """Convertit le produit en dictionnaire"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'short_description': self.short_description,
            'origin_country': self.origin_country,
            'origin_region': self.origin_region,
            'category': self.category.value,
            'subcategory': self.subcategory,
            'base_price': float(self.base_price) if self.base_price else None,
            'current_price': float(self.current_price) if self.current_price else None,
            'discounted_price': float(self.discounted_price) if self.discounted_price else None,
            'effective_price': float(self.effective_price) if self.effective_price else None,
            'discount_percentage': self.discount_percentage,
            'stock_quantity': self.stock_quantity,
            'is_low_stock': self.is_low_stock,
            'is_in_stock': self.is_in_stock,
            'weight': float(self.weight) if self.weight else None,
            'unit': self.unit,
            'image_url': self.image_url,
            'gallery_images': self.gallery_images or [],
            'ecology_score': self.ecology_score,
            'fair_trade': self.fair_trade,
            'organic': self.organic,
            'carbon_footprint': float(self.carbon_footprint) if self.carbon_footprint else None,
            'is_active': self.is_active,
            'featured': self.featured,
            'tags': self.tags or [],
            'nutritional_info': self.nutritional_info,
            'storage_instructions': self.storage_instructions,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'average_rating': self.average_rating,
            'review_count': self.review_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_seller and self.seller:
            data['seller'] = self.seller.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<Product {self.name}>'

