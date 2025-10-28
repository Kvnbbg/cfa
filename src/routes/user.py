"""User routes for CFA API."""
from functools import wraps

from flask import Blueprint, jsonify, request, g


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
