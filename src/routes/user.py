"""User routes for CFA API."""
from functools import wraps

from flask import Blueprint, jsonify, request, g

from ..models import User

user_bp = Blueprint('user', __name__)

AUTH_HEADER_PREFIX = 'Bearer '
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_INTERNAL_SERVER_ERROR = 500


def error_response(message, status_code):
    """Return a standardized JSON error response."""
    return jsonify({'error': message}), status_code


def require_auth(func):
    """Ensure the requester provides a valid JWT token before proceeding."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith(AUTH_HEADER_PREFIX):
            return error_response('Authorization header missing or malformed', HTTP_UNAUTHORIZED)

        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return error_response('Invalid or expired token', HTTP_UNAUTHORIZED)

        try:
            user = User.verify_token(token)
        except Exception:
            return error_response('Invalid or expired token', HTTP_UNAUTHORIZED)
        if not user:
            return error_response('Invalid or expired token', HTTP_UNAUTHORIZED)

        g.current_user = user
        return func(*args, **kwargs)

    return wrapper


@user_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and return a JWT with profile details."""
    data = request.get_json(silent=True)
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return error_response('Invalid request payload', HTTP_BAD_REQUEST)

    email = data.get('email')
    password = data.get('password')
    if isinstance(email, str):
        email = email.strip()
    if isinstance(password, str):
        password = password.strip()

    if not email or not password:
        return error_response('Missing email or password', HTTP_BAD_REQUEST)

    try:
        user = User.query.filter_by(email=email).first()
    except Exception:
        return error_response('Unable to authenticate at this time', HTTP_INTERNAL_SERVER_ERROR)
    if not user or not user.check_password(password):
        return error_response('Invalid email or password', HTTP_UNAUTHORIZED)

    try:
        token = user.generate_token()
    except Exception:
        return error_response('Unable to authenticate at this time', HTTP_INTERNAL_SERVER_ERROR)
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    if not token:
        return error_response('Unable to authenticate at this time', HTTP_INTERNAL_SERVER_ERROR)
    role_value = user.role.value if getattr(user, 'role', None) else None
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': role_value
        }
    })


@user_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Return the authenticated user's profile."""
    user = g.current_user
    if not user:
        return error_response('Invalid or expired token', HTTP_UNAUTHORIZED)
    return jsonify(user.to_dict()), 200
