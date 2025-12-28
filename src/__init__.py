import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from .models import db
from .routes.user import user_bp

# Import de tous les modèles pour s'assurer qu'ils sont enregistrés
from .models import (
    User, Product, Order, OrderItem, PriceHistory,
    CompetitorPrice, Review, Log, Coupon
)

def create_app():
    """Factory pour créer l'application Flask"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(
        __name__,
        static_folder=static_dir,
        static_url_path='/static'
    )

    # Configuration
    env = os.environ.get('FLASK_ENV', os.environ.get('ENV', 'development')).lower()
    secret_key = os.environ.get('SECRET_KEY', 'cfa-dev-secret-key-2025')
    if env == 'production' and secret_key == 'cfa-dev-secret-key-2025':
        raise RuntimeError('SECRET_KEY must be set for production environments')
    app.config['SECRET_KEY'] = secret_key
    # Prefer DATABASE_URL when provided (e.g., Railway Postgres). Otherwise fall back to local sqlite file.
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Activation de CORS pour permettre les requêtes cross-origin
    cors_origins = os.environ.get('CORS_ORIGINS', '')
    if cors_origins:
        origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    else:
        origins = ['*'] if env != 'production' else []
    CORS(app, origins=origins)

    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = env == 'production'

    # Initialisation de la base de données
    db.init_app(app)

    # Enregistrement des blueprints
    app.register_blueprint(user_bp, url_prefix='/api')

    # Création des tables
    with app.app_context():
        db.create_all()

        # Création d'un utilisateur admin par défaut si nécessaire (only when not in production)
        if env != 'production':
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

    @app.after_request
    def set_security_headers(response):
        """Add baseline security headers to all responses."""
        csp = (
            "default-src 'self'; "
            "script-src 'self' https://js.stripe.com; "
            "style-src 'self' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com data:; "
            "img-src 'self' data:; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src https://js.stripe.com https://hooks.stripe.com"
        )
        response.headers.setdefault('Content-Security-Policy', csp)
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'geolocation=(), microphone=(), camera=()')
        if env == 'production':
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Servir les fichiers statiques et l'application frontend"""
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        # Normaliser le chemin demandé et éviter toute échappée du répertoire statique
        requested_path = os.path.normpath(os.path.join(static_folder_path, path)) if path else None
        index_path = os.path.join(static_folder_path, 'index.html')

        if path and requested_path.startswith(static_folder_path) and os.path.exists(requested_path):
            return send_from_directory(static_folder_path, path)

        if os.path.exists(index_path):
            # Fallback SPA-friendly pour garantir une navigation résiliente
            return send_from_directory(static_folder_path, 'index.html')

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
