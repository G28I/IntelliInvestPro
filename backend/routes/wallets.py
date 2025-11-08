"""Wallet management routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Wallet, Transaction, AuditLog
from decimal import Decimal
from datetime import datetime
import json

bp = Blueprint('wallets', __name__, url_prefix='/api/wallets')

@bp.route('/', methods=['GET'])
@jwt_required()
def get_wallets():
    """Get user's wallets"""
    try:
        current_user_id = get_jwt_identity()
        
        wallets = Wallet.query.filter_by(user_id=current_user_id).all()
        
        return jsonify({
            'wallets': [w.to_dict() for w in wallets]
        }), 200
        
    except Exception as e:
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500

@bp.route('/<currency>', methods=['GET'])
@jwt_required()
def get_wallet(currency):
    """Get a specific wallet by currency"""
    try:
        current_user_id = get_jwt_identity()
        
        wallet = Wallet.query.filter_by(
            user_id=current_user_id,
            currency=currency.upper()
        ).first()
        
        if not wallet:
            wallet = Wallet(
                user_id=current_user_id,
                currency=currency.upper(),
                balance=Decimal('0.00'),
                available_balance=Decimal('0.00'),
                pending_balance=Decimal('0.00')
            )
            db.session.add(wallet)
            db.session.commit()
        
        return jsonify(wallet.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500

@bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    """Transfer funds to another user"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('recipient_email') or not data.get('amount'):
            return jsonify({'error': 'Recipient email and amount are required'}), 400
        
        amount = Decimal(str(data['amount']))
        currency = data.get('currency', 'USD')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Get sender wallet
        sender_wallet = Wallet.query.filter_by(
            user_id=current_user_id,
            currency=currency
        ).first()
        
        if not sender_wallet or sender_wallet.available_balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # Get recipient
        recipient = User.query.filter_by(email=data['recipient_email']).first()
        
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404
        
        if recipient.id == current_user_id:
            return jsonify({'error': 'Cannot transfer to yourself'}), 400
        
        # Get or create recipient wallet
        recipient_wallet = Wallet.query.filter_by(
            user_id=recipient.id,
            currency=currency
        ).first()
        
        if not recipient_wallet:
            recipient_wallet = Wallet(
                user_id=recipient.id,
                currency=currency,
                balance=Decimal('0.00'),
                available_balance=Decimal('0.00'),
                pending_balance=Decimal('0.00')
            )
            db.session.add(recipient_wallet)
        
        # Create transfer transactions
        sender_txn = Transaction(
            user_id=current_user_id,
            amount=-amount,
            currency=currency,
            type='transfer',
            description=f'Transfer to {recipient.email}',
            status='completed',
            completed_at=datetime.utcnow(),
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            extra_data=json.dumps({'recipient_id': recipient.id})
        )
        
        recipient_txn = Transaction(
            user_id=recipient.id,
            amount=amount,
            currency=currency,
            type='transfer',
            description=f'Transfer from {User.query.get(current_user_id).email}',
            status='completed',
            completed_at=datetime.utcnow(),
            extra_data=json.dumps({'sender_id': current_user_id})
        )
        
        # Update wallet balances
        sender_wallet.balance -= amount
        sender_wallet.available_balance -= amount
        recipient_wallet.balance += amount
        recipient_wallet.available_balance += amount
        
        db.session.add(sender_txn)
        db.session.add(recipient_txn)
        
        # Create audit logs
        audit_sender = AuditLog(
            user_id=current_user_id,
            action='transfer_sent',
            resource_type='transaction',
            resource_id=sender_txn.id,
            details=f'Amount: {amount} {currency} to {recipient.email}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        audit_recipient = AuditLog(
            user_id=recipient.id,
            action='transfer_received',
            resource_type='transaction',
            resource_id=recipient_txn.id,
            details=f'Amount: {amount} {currency} from {User.query.get(current_user_id).email}'
        )
        
        db.session.add(audit_sender)
        db.session.add(audit_recipient)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Transfer completed successfully',
            'transaction': sender_txn.to_dict(),
            'new_balance': float(sender_wallet.available_balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500

@bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    """Withdraw funds from wallet"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('amount'):
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = Decimal(str(data['amount']))
        currency = data.get('currency', 'USD')
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Get wallet
        wallet = Wallet.query.filter_by(
            user_id=current_user_id,
            currency=currency
        ).first()
        
        if not wallet or wallet.available_balance < amount:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # Create withdrawal transaction
        transaction = Transaction(
            user_id=current_user_id,
            amount=-amount,
            currency=currency,
            type='withdrawal',
            description=data.get('description', 'Withdrawal'),
            status='processing',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        db.session.add(transaction)
        db.session.flush()
        
        # Process withdrawal (simulated)
        transaction.status = 'completed'
        transaction.completed_at = datetime.utcnow()
        
        # Update wallet balance
        wallet.balance -= amount
        wallet.available_balance -= amount
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user_id,
            action='withdrawal_processed',
            resource_type='transaction',
            resource_id=transaction.id,
            details=f'Amount: {amount} {currency}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Withdrawal processed successfully',
            'transaction': transaction.to_dict(),
            'new_balance': float(wallet.available_balance)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        import logging; logging.error(f'Error: {str(e)}'); return jsonify({'error': 'An error occurred. Please try again.'}), 500
