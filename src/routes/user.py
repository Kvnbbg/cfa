"""User routes for CFA API."""
from functools import wraps

from flask import Blueprint, jsonify, request, g

from werkzeug.security import check_password_hash

from ..models import User

user_bp = Blueprint('user', __name__)


def require_auth(func):
    """Decorator ensuring that the requester provides a valid JWT token."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or malformed'}), 401

        token = auth_header.split(' ', 1)[1].strip()
        user = User.verify_token(token) if token else None
        if not user:
            return jsonify({'error': 'Invalid or expired token'}), 401

        g.current_user = user
        return func(*args, **kwargs)

    return wrapper


@user_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint."""

    data = request.get_json(silent=True) or {}

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = user.generate_token()
    if isinstance(token, bytes):  # PyJWT < 2.0 returns bytes
        token = token.decode('utf-8')
        
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role.value
        }
    })


@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile endpoint."""
    user = g.current_user
    return jsonify(user.to_dict()), 200
