import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models import db
from src.routes.user import user_bp

# Import de tous les modèles pour s'assurer qu'ils sont enregistrés
from src.models import (
    User, Product, Order, OrderItem, PriceHistory, 
    CompetitorPrice, Review, Log, Coupon
)

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'cfa-dev-secret-key-2025')
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Activation de CORS pour permettre les requêtes cross-origin
    CORS(app, origins="*")
    
    # Initialisation de la base de données
    db.init_app(app)
    
    # Enregistrement des blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    
    # Création des tables
    with app.app_context():
        db.create_all()
        
        # Création d'un utilisateur admin par défaut si nécessaire
        admin = User.query.filter_by(email='admin@cfa.com').first()
        if not admin:
            from src.models.base import UserRole
            admin = User(
                email='admin@cfa.com',
                password='admin123',
                first_name='Admin',
                last_name='CFA',
                role=UserRole.ADMIN
            )
            db.session.add(admin)
            db.session.commit()
            print("Utilisateur admin créé: admin@cfa.com / admin123")
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Servir les fichiers statiques et l'application frontend"""
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    @app.route('/health')
    def health_check():
        """Point de contrôle de santé de l'application"""
        return {
            'status': 'healthy',
            'app': 'Caraïbes-France-Asie',
            'version': '1.0.0',
            'database': 'connected'
        }
    
    return app

# Création de l'instance de l'application
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

