from flask_sqlalchemy import SQLAlchemy
from flask import current_app, has_app_context
from werkzeug.security import generate_password_hash, check_password_hash
from src.models.base import BaseModel, UserRole, db
import jwt
from datetime import datetime, timedelta
import os

DEFAULT_SECRET_KEY = 'cfa-dev-secret-key-2025'


def _get_secret_key():
    """Fetch the SECRET_KEY from Flask config when possible, with a safe fallback."""
    if has_app_context():
        return current_app.config.get('SECRET_KEY', DEFAULT_SECRET_KEY)
    return os.environ.get('SECRET_KEY', DEFAULT_SECRET_KEY)

class User(BaseModel):
    """Modèle utilisateur avec authentification et profils"""
    __tablename__ = 'users'
    
    # Informations de base
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Rôle et statut
    role = db.Column(db.Enum(UserRole), default=UserRole.BUYER, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # Informations de contact
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    
    # Intégrations externes
    stripe_customer_id = db.Column(db.Text)
    
    # Relations
    products = db.relationship('Product', backref='seller', lazy=True, foreign_keys='Product.seller_id')
    orders = db.relationship('Order', backref='customer', lazy=True)
    reviews = db.relationship('Review', backref='author', lazy=True)
    logs = db.relationship('Log', backref='user', lazy=True)
    
    def __init__(self, email, password, **kwargs):
        super().__init__(**kwargs)
        self.email = email
        self.set_password(password)
    
    def set_password(self, password):
        """Hash et stocke le mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe"""
        return check_password_hash(self.password_hash, password)
    
    def generate_token(self, expires_in=3600):
        """Génère un token JWT"""
        payload = {
            'user_id': self.id,
            'email': self.email,
            'role': self.role.value,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in)
        }
        return jwt.encode(payload, _get_secret_key(), algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, _get_secret_key(), algorithms=['HS256'])
            return User.query.get(payload['user_id'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @property
    def full_name(self):
        """Nom complet de l'utilisateur"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def to_dict(self, include_sensitive=False):
        """Convertit l'utilisateur en dictionnaire"""
        data = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'phone': self.phone,
            'city': self.city,
            'country': self.country,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data.update({
                'address': self.address,
                'postal_code': self.postal_code,
                'stripe_customer_id': self.stripe_customer_id
            })
        
        return data
    
    def __repr__(self):
        return f'<User {self.email}>'
