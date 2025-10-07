"""User routes for CFA API."""
from flask import Blueprint, jsonify, request
from ..models import db, User
from werkzeug.security import check_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint."""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400
        
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    token = user.generate_auth_token()
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
def get_profile():
    """Get user profile endpoint."""
    # TODO: Add auth middleware
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Missing user_id'}), 400
        
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role.value
    })