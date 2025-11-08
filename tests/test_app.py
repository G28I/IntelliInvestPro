"""Test suite for the payments application"""
import pytest
import json
from backend.app import create_app
from backend.models import db, User, Transaction, Wallet, PaymentMethod

@pytest.fixture
def app():
    """Create test application"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers"""
    # Register user
    response = client.post('/api/auth/register', 
        json={
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'TestPass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    data = json.loads(response.data)
    token = data['access_token']
    
    return {'Authorization': f'Bearer {token}'}

class TestAuth:
    """Test authentication endpoints"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/register', 
            json={
                'email': 'newuser@example.com',
                'username': 'newuser',
                'password': 'SecurePass123'
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'access_token' in data
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_register_duplicate_email(self, client, auth_headers):
        """Test registration with duplicate email"""
        response = client.post('/api/auth/register', 
            json={
                'email': 'test@example.com',
                'username': 'anotheruser',
                'password': 'SecurePass123'
            }
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'already registered' in data['error']
    
    def test_login_success(self, client, auth_headers):
        """Test successful login"""
        response = client.post('/api/auth/login', 
            json={
                'email': 'test@example.com',
                'password': 'TestPass123'
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_login_invalid_credentials(self, client, auth_headers):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', 
            json={
                'email': 'test@example.com',
                'password': 'WrongPassword'
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, client, auth_headers):
        """Test getting current user info"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['email'] == 'test@example.com'

class TestPayments:
    """Test payment endpoints"""
    
    def test_process_payment_success(self, client, auth_headers):
        """Test successful payment processing"""
        response = client.post('/api/payments/process',
            headers=auth_headers,
            json={
                'amount': 100.00,
                'description': 'Test payment'
            }
        )
        
        data = json.loads(response.data)
        # Payment can succeed or fail (simulated), but should process
        assert response.status_code in [200, 400]
        assert 'transaction' in data
    
    def test_process_payment_invalid_amount(self, client, auth_headers):
        """Test payment with invalid amount"""
        response = client.post('/api/payments/process',
            headers=auth_headers,
            json={
                'amount': -50.00,
                'description': 'Invalid payment'
            }
        )
        
        assert response.status_code == 400
    
    def test_get_transactions(self, client, auth_headers):
        """Test getting transaction history"""
        # First make a payment
        client.post('/api/payments/process',
            headers=auth_headers,
            json={'amount': 50.00, 'description': 'Test'}
        )
        
        # Then get transactions
        response = client.get('/api/payments/transactions', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'transactions' in data
        assert len(data['transactions']) >= 1
    
    def test_add_payment_method(self, client, auth_headers):
        """Test adding payment method"""
        response = client.post('/api/payments/methods',
            headers=auth_headers,
            json={
                'type': 'card',
                'provider': 'visa',
                'last_four': '4242',
                'expiry_month': 12,
                'expiry_year': 2025
            }
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['payment_method']['type'] == 'card'

class TestWallets:
    """Test wallet endpoints"""
    
    def test_get_wallet(self, client, auth_headers):
        """Test getting wallet"""
        response = client.get('/api/wallets/USD', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['currency'] == 'USD'
        assert 'balance' in data
    
    def test_transfer_insufficient_balance(self, client, auth_headers):
        """Test transfer with insufficient balance"""
        # Create another user to transfer to
        client.post('/api/auth/register', 
            json={
                'email': 'recipient@example.com',
                'username': 'recipient',
                'password': 'RecipientPass123'
            }
        )
        
        response = client.post('/api/wallets/transfer',
            headers=auth_headers,
            json={
                'recipient_email': 'recipient@example.com',
                'amount': 1000.00
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'Insufficient balance' in data['error']

class TestAPI:
    """Test general API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_index(self, client):
        """Test index endpoint"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'online'
