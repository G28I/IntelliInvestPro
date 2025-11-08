# IntelliPay - World-Class Payments Application

A modern, secure, and feature-rich payment processing platform built with Flask and vanilla JavaScript.

## 🌟 Features

### Core Payment Features
- **Secure Payment Processing**: Process payments with bank-level encryption
- **Multi-Payment Methods**: Support for credit cards, bank accounts, and digital wallets
- **Transaction History**: Complete audit trail of all transactions
- **Real-time Balance Updates**: Instant wallet balance updates
- **Refund Processing**: Easy refund management for transactions

### User Management
- **Secure Authentication**: JWT-based authentication system
- **User Profiles**: Comprehensive user profile management
- **Password Security**: Strong password requirements and secure hashing
- **Account Verification**: Email verification support

### Wallet System
- **Multi-Currency Support**: Handle multiple currencies (USD, EUR, etc.)
- **P2P Transfers**: Transfer funds between users instantly
- **Withdrawal Management**: Withdraw funds to bank accounts
- **Balance Tracking**: Available, pending, and total balance tracking

### Security Features
- **Encryption**: All sensitive data encrypted at rest and in transit
- **Audit Logging**: Complete audit trail of all activities
- **Rate Limiting**: Protection against brute force attacks
- **CORS Support**: Secure cross-origin resource sharing
- **JWT Authentication**: Secure token-based authentication

### Advanced Features
- **Transaction Analytics**: Detailed transaction reporting
- **Payment Gateway Integration**: Ready for Stripe, PayPal integration
- **Webhook Support**: Real-time payment status updates
- **Fraud Detection**: Basic fraud prevention mechanisms
- **API Documentation**: RESTful API with comprehensive endpoints

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/G28I/IntelliInvestPro.git
cd IntelliInvestPro
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (optional):
```bash
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret
export STRIPE_SECRET_KEY=your-stripe-key
```

4. Initialize the database:
```bash
cd backend
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all()"
```

5. Run the application:
```bash
python app.py
```

6. Open your browser and navigate to:
- Backend API: `http://localhost:5000`
- Frontend: Open `frontend/index.html` in your browser

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

#### Get Current User
```
GET /api/auth/me
Authorization: Bearer <token>
```

### Payment Endpoints

#### Process Payment
```
POST /api/payments/process
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100.00,
  "currency": "USD",
  "description": "Payment description"
}
```

#### Get Transactions
```
GET /api/payments/transactions?page=1&per_page=20
Authorization: Bearer <token>
```

#### Request Refund
```
POST /api/payments/refund
Authorization: Bearer <token>
Content-Type: application/json

{
  "transaction_id": "txn-id",
  "amount": 50.00,
  "reason": "Customer request"
}
```

### Wallet Endpoints

#### Get Wallet
```
GET /api/wallets/USD
Authorization: Bearer <token>
```

#### Transfer Funds
```
POST /api/wallets/transfer
Authorization: Bearer <token>
Content-Type: application/json

{
  "recipient_email": "recipient@example.com",
  "amount": 100.00,
  "currency": "USD"
}
```

#### Withdraw Funds
```
POST /api/wallets/withdraw
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100.00,
  "currency": "USD",
  "description": "Bank withdrawal"
}
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run tests with coverage:
```bash
pytest tests/ --cov=backend --cov-report=html
```

## 🏗️ Project Structure

```
IntelliInvestPro/
├── backend/
│   ├── app.py              # Flask application factory
│   ├── models.py           # Database models
│   └── routes/
│       ├── auth.py         # Authentication routes
│       ├── payments.py     # Payment processing routes
│       ├── users.py        # User management routes
│       └── wallets.py      # Wallet management routes
├── frontend/
│   ├── index.html          # Main UI
│   └── app.js              # Frontend JavaScript
├── config/
│   └── config.py           # Application configuration
├── tests/
│   └── test_app.py         # Test suite
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔒 Security Considerations

- **Never commit secrets**: Use environment variables for sensitive data
- **Password Requirements**: Minimum 8 characters with uppercase, lowercase, and digits
- **Token Expiration**: Access tokens expire in 1 hour, refresh tokens in 30 days
- **HTTPS Only**: Use HTTPS in production
- **Input Validation**: All inputs are validated and sanitized
- **SQL Injection Protection**: Using SQLAlchemy ORM prevents SQL injection
- **XSS Protection**: All outputs are escaped

## 📊 Database Schema

### Users
- User authentication and profile information
- Password hashing with Werkzeug
- Account status tracking

### Transactions
- Payment records with full audit trail
- Support for payments, transfers, refunds, withdrawals
- Gateway integration metadata

### Wallets
- Multi-currency balance management
- Available, pending, and total balances
- Real-time balance updates

### Payment Methods
- Stored payment method information
- Support for cards, bank accounts, digital wallets
- PCI-compliant data handling

### Audit Logs
- Complete activity tracking
- User actions and system events
- IP address and user agent logging

## 🌐 Deployment

### Production Checklist
- [ ] Set strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Enable HTTPS/SSL
- [ ] Set up payment gateway (Stripe, PayPal)
- [ ] Configure email service for notifications
- [ ] Set up monitoring and logging
- [ ] Enable rate limiting
- [ ] Configure CORS for production domain
- [ ] Set up backups
- [ ] Implement DDoS protection

### Environment Variables
```bash
SECRET_KEY=<strong-secret-key>
JWT_SECRET_KEY=<jwt-secret-key>
DATABASE_URL=postgresql://user:pass@localhost/payments
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxx
FLASK_ENV=production
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask framework for the backend
- SQLAlchemy for database management
- JWT for secure authentication
- Stripe for payment gateway inspiration

## 📞 Support

For support, email support@intellipay.example.com or open an issue in the repository.

---

**Built with ❤️ for the modern payment ecosystem**
