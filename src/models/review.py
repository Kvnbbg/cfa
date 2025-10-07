from src.models.base import BaseModel, db

class Review(BaseModel):
    """Avis et évaluations des produits"""
    __tablename__ = 'reviews'
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 étoiles
    title = db.Column(db.String(255))
    comment = db.Column(db.Text)
    verified_purchase = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    
    # Contrainte pour s'assurer que la note est entre 1 et 5
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='rating_range'),
    )
    
    @property
    def is_positive(self):
        """Vérifie si l'avis est positif (4-5 étoiles)"""
        return self.rating >= 4
    
    @property
    def is_negative(self):
        """Vérifie si l'avis est négatif (1-2 étoiles)"""
        return self.rating <= 2
    
    def to_dict(self, include_user=False):
        """Convertit l'avis en dictionnaire"""
        data = {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'title': self.title,
            'comment': self.comment,
            'verified_purchase': self.verified_purchase,
            'is_approved': self.is_approved,
            'is_positive': self.is_positive,
            'is_negative': self.is_negative,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_user and self.author:
            data['author'] = {
                'id': self.author.id,
                'full_name': self.author.full_name,
                'first_name': self.author.first_name
            }
        
        return data
    
    def __repr__(self):
        return f'<Review {self.rating}/5 for Product {self.product_id}>'

