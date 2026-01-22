import logging
import os
import secrets
from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from .models import db
from .routes.user import user_bp

from .models import (
    User, Product, Order, OrderItem, PriceHistory,
    CompetitorPrice, Review, Log, Coupon
)

logger = logging.getLogger(__name__)

DEFAULT_ENV = 'development'
ENV_PRODUCTION = 'production'
DEFAULT_POOL_RECYCLE_SECONDS = 300
DEFAULT_HSTS_MAX_AGE_SECONDS = 31536000
DEFAULT_CORS_ORIGINS = ''
ADMIN_EMAIL_ENV = 'DEFAULT_ADMIN_EMAIL'
ADMIN_PASSWORD_ENV = 'DEFAULT_ADMIN_PASSWORD'

def create_app():
    """Factory pour créer l'application Flask"""
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    app = Flask(
        __name__,
        static_folder=static_dir,
        static_url_path='/static'
    )

    # Configuration
    env = os.environ.get('FLASK_ENV', os.environ.get('ENV', DEFAULT_ENV)).lower()
    secret_key = os.environ.get('SECRET_KEY')
    if env == ENV_PRODUCTION and not secret_key:
        raise RuntimeError('SECRET_KEY must be set for production environments')
    if not secret_key:
        secret_key = secrets.token_hex(32)
        logger.warning('SECRET_KEY not set; generated a temporary key for non-production use.')
    app.config['SECRET_KEY'] = secret_key
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = (
            f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', DEFAULT_DATABASE_FILENAME)}"
        )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': DEFAULT_POOL_RECYCLE_SECONDS,
    }

    # Activation de CORS pour permettre les requêtes cross-origin
    cors_origins = os.environ.get('CORS_ORIGINS', DEFAULT_CORS_ORIGINS)
    if cors_origins:
        origins = [origin.strip() for origin in cors_origins.split(',') if origin.strip()]
    else:
        origins = ['*'] if env != ENV_PRODUCTION else []
    if env == ENV_PRODUCTION and not origins:
        logger.warning('CORS_ORIGINS is empty in production; no cross-origin requests will be allowed.')
    CORS(app, origins=origins)

    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = env == 'production'

    db.init_app(app)

    app.register_blueprint(user_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()

        # Création d'un utilisateur admin par défaut si nécessaire (only when not in production)
        if env != ENV_PRODUCTION:
            admin_email = os.environ.get(ADMIN_EMAIL_ENV, 'admin@cfa.com').strip()
            admin_password = os.environ.get(ADMIN_PASSWORD_ENV)
            if not admin_password:
                logger.info(
                    'Skipping default admin creation because the default admin password is not set.'
                )
            
            elif not admin_email:
                logger.warning('Skipping default admin creation because admin email is empty.')
            else:
                admin = User.query.filter_by(email=admin_email).first()
                if not admin:
                    from src.models.base import UserRole
                    admin = User(
                        email=admin_email,
                        password=admin_password,
                        first_name='Admin',
                        last_name='CFA',
                        role=UserRole.ADMIN
                    )
                    db.session.add(admin)
                    db.session.commit()
                    logger.info('Default admin user created for %s.', admin_email)

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
            response.headers.setdefault(
                'Strict-Transport-Security',
                f'max-age={DEFAULT_HSTS_MAX_AGE_SECONDS}; includeSubDomains'
            )
        return response

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        """Servir les fichiers statiques et l'application frontend"""
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        requested_path = os.path.normpath(os.path.join(static_folder_path, path)) if path else None
        index_path = os.path.join(static_folder_path, 'index.html')

        if path and requested_path and requested_path.startswith(static_folder_path) and os.path.exists(requested_path):
            return send_from_directory(static_folder_path, path)

        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')

        return "index.html not found", 404

    @app.route('/health')
    def health_check():
        """Point de contrôle de santé de l'application"""
        return {
            'status': 'healthy',
            'app': 'Caraïbes-France-Asie',
            'version': DEFAULT_HEALTH_VERSION,
            'database': 'connected'
        }

    return app
