from src.models.base import BaseModel, db
from sqlalchemy import JSON

class Log(BaseModel):
    """Système de logs pour audit et traçabilité"""
    __tablename__ = 'logs'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(50), index=True)  # 'product', 'order', 'user', etc.
    entity_id = db.Column(db.Integer, index=True)
    
    # Valeurs avant et après modification
    old_values = db.Column(JSON)
    new_values = db.Column(JSON)
    
    # Informations de contexte
    ip_address = db.Column(db.String(45))  # Support IPv6
    user_agent = db.Column(db.Text)
    meta_data = db.Column(JSON)  # Données supplémentaires
    level = db.Column(db.String(20), default='INFO')  # INFO, WARNING, ERROR, CRITICAL
    
    @staticmethod
    def log_action(user_id, action, entity_type=None, entity_id=None, 
                   old_values=None, new_values=None, meta_data=None, 
                   ip_address=None, user_agent=None, level='INFO'):
        """Méthode utilitaire pour créer un log"""
        log = Log(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_values=old_values,
            new_values=new_values,
            meta_data=meta_data,
            ip_address=ip_address,
            user_agent=user_agent,
            level=level
        )
        db.session.add(log)
        return log
    
    @staticmethod
    def log_user_action(user_id, action, **kwargs):
        """Log d'action utilisateur"""
        return Log.log_action(user_id, action, entity_type='user', entity_id=user_id, **kwargs)
    
    @staticmethod
    def log_product_action(user_id, action, product_id, **kwargs):
        """Log d'action sur un produit"""
        return Log.log_action(user_id, action, entity_type='product', entity_id=product_id, **kwargs)
    
    @staticmethod
    def log_order_action(user_id, action, order_id, **kwargs):
        """Log d'action sur une commande"""
        return Log.log_action(user_id, action, entity_type='order', entity_id=order_id, **kwargs)
    
    @staticmethod
    def log_system_action(action, **kwargs):
        """Log d'action système (sans utilisateur)"""
        return Log.log_action(None, action, **kwargs)
    
    def to_dict(self, include_user=False):
        """Convertit le log en dictionnaire"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'meta_data': self.meta_data,
            'level': self.level,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_user and self.user:
            data['user'] = {
                'id': self.user.id,
                'email': self.user.email,
                'full_name': self.user.full_name
            }
        
        return data
    
    def __repr__(self):
        return f'<Log {self.action} by User {self.user_id}>'

