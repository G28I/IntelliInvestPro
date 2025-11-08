"""User management routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, AuditLog

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'phone' in data:
            user.phone = data['phone']
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user_id,
            action='profile_updated',
            resource_type='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Current and new passwords are required'}), 400
        
        # Verify current password
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Current password is incorrect'}), 401
        
        # Update password
        user.set_password(data['new_password'])
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user_id,
            action='password_changed',
            resource_type='user',
            resource_id=user.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500
