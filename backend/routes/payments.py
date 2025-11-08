"""Payment processing routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.models import db, User, Transaction, PaymentMethod, Wallet, AuditLog, Refund
from datetime import datetime
from decimal import Decimal
import json

bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@bp.route('/process', methods=['POST'])
@jwt_required()
def process_payment():
    """Process a payment transaction"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('amount'):
            return jsonify({'error': 'Amount is required'}), 400
        
        amount = Decimal(str(data['amount']))
        
        # Validate amount
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
        
        # Create transaction
        transaction = Transaction(
            user_id=current_user_id,
            amount=amount,
            currency=data.get('currency', 'USD'),
            type='payment',
            description=data.get('description'),
            status='processing',
            gateway='stripe',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            extra_data=json.dumps(data.get('metadata', {}))
        )
        
        if data.get('payment_method_id'):
            payment_method = PaymentMethod.query.get(data['payment_method_id'])
            if not payment_method or payment_method.user_id != current_user_id:
                return jsonify({'error': 'Invalid payment method'}), 400
            transaction.payment_method_id = payment_method.id
        
        db.session.add(transaction)
        db.session.flush()
        
        # Simulate payment processing
        # In production, this would integrate with actual payment gateway (Stripe, PayPal, etc.)
        import random
        success = random.random() > 0.1  # 90% success rate for demo
        
        if success:
            transaction.status = 'completed'
            transaction.completed_at = datetime.utcnow()
            transaction.gateway_transaction_id = f'txn_{transaction.id[:8]}'
            
            # Update wallet balance
            wallet = Wallet.query.filter_by(
                user_id=current_user_id,
                currency=transaction.currency
            ).first()
            
            if not wallet:
                wallet = Wallet(
                    user_id=current_user_id,
                    currency=transaction.currency,
                    balance=Decimal('0.00'),
                    available_balance=Decimal('0.00'),
                    pending_balance=Decimal('0.00')
                )
                db.session.add(wallet)
            
            wallet.balance += amount
            wallet.available_balance += amount
            
        else:
            transaction.status = 'failed'
            transaction.gateway_response = 'Payment declined'
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user_id,
            action='payment_processed',
            resource_type='transaction',
            resource_id=transaction.id,
            details=f'Amount: {amount} {transaction.currency}, Status: {transaction.status}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment processed',
            'transaction': transaction.to_dict()
        }), 200 if success else 400
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get user's transaction history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # Build query
        query = Transaction.query.filter_by(user_id=current_user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # Order by creation date (newest first)
        query = query.order_by(Transaction.created_at.desc())
        
        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/transactions/<transaction_id>', methods=['GET'])
@jwt_required()
def get_transaction(transaction_id):
    """Get a specific transaction"""
    try:
        current_user_id = get_jwt_identity()
        
        transaction = Transaction.query.filter_by(
            id=transaction_id,
            user_id=current_user_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        return jsonify(transaction.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/refund', methods=['POST'])
@jwt_required()
def request_refund():
    """Request a refund for a transaction"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('transaction_id'):
            return jsonify({'error': 'Transaction ID is required'}), 400
        
        # Get transaction
        transaction = Transaction.query.filter_by(
            id=data['transaction_id'],
            user_id=current_user_id
        ).first()
        
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        if transaction.status != 'completed':
            return jsonify({'error': 'Only completed transactions can be refunded'}), 400
        
        # Check if already refunded
        existing_refund = Refund.query.filter_by(
            transaction_id=transaction.id,
            status='completed'
        ).first()
        
        if existing_refund:
            return jsonify({'error': 'Transaction already refunded'}), 400
        
        # Create refund
        refund_amount = Decimal(str(data.get('amount', transaction.amount)))
        
        if refund_amount > transaction.amount:
            return jsonify({'error': 'Refund amount cannot exceed transaction amount'}), 400
        
        refund = Refund(
            transaction_id=transaction.id,
            amount=refund_amount,
            reason=data.get('reason', 'Customer request'),
            status='processing'
        )
        
        db.session.add(refund)
        db.session.flush()
        
        # Process refund (simulated)
        refund.status = 'completed'
        refund.completed_at = datetime.utcnow()
        refund.gateway_refund_id = f'ref_{refund.id[:8]}'
        
        # Update transaction status
        transaction.status = 'refunded'
        
        # Update wallet balance
        wallet = Wallet.query.filter_by(
            user_id=current_user_id,
            currency=transaction.currency
        ).first()
        
        if wallet:
            wallet.balance -= refund_amount
            wallet.available_balance -= refund_amount
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user_id,
            action='refund_processed',
            resource_type='refund',
            resource_id=refund.id,
            details=f'Transaction: {transaction.id}, Amount: {refund_amount}',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Refund processed successfully',
            'refund': refund.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/methods', methods=['GET'])
@jwt_required()
def get_payment_methods():
    """Get user's payment methods"""
    try:
        current_user_id = get_jwt_identity()
        
        payment_methods = PaymentMethod.query.filter_by(
            user_id=current_user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'payment_methods': [pm.to_dict() for pm in payment_methods]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/methods', methods=['POST'])
@jwt_required()
def add_payment_method():
    """Add a new payment method"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('type'):
            return jsonify({'error': 'Payment method type is required'}), 400
        
        # Create payment method
        payment_method = PaymentMethod(
            user_id=current_user_id,
            type=data['type'],
            provider=data.get('provider'),
            last_four=data.get('last_four'),
            expiry_month=data.get('expiry_month'),
            expiry_year=data.get('expiry_year'),
            is_default=data.get('is_default', False),
            billing_address=data.get('billing_address')
        )
        
        # If this is set as default, unset other defaults
        if payment_method.is_default:
            PaymentMethod.query.filter_by(
                user_id=current_user_id,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(payment_method)
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user_id,
            action='payment_method_added',
            resource_type='payment_method',
            resource_id=payment_method.id,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(audit)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Payment method added successfully',
            'payment_method': payment_method.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
