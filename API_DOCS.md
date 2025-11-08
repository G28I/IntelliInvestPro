# API Reference Guide

## Base URL
```
http://localhost:5000/api
```

## Authentication
All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

## Response Format
All responses are in JSON format. Successful responses include relevant data, while errors include an error message:

**Success Response:**
```json
{
  "message": "Success message",
  "data": { ... }
}
```

**Error Response:**
```json
{
  "error": "Error message"
}
```

## Endpoints

### Authentication

#### POST /api/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "is_verified": false,
    "created_at": "2025-01-01T00:00:00"
  },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

#### POST /api/auth/login
Login with existing credentials.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "user": { ... },
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

#### POST /api/auth/refresh
Refresh access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh-token>
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ..."
}
```

#### GET /api/auth/me
Get current user information.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "user-id",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

### Payments

#### POST /api/payments/process
Process a payment transaction.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "description": "Online purchase",
  "payment_method_id": "pm-id" // optional
}
```

**Response (200 OK):**
```json
{
  "message": "Payment processed",
  "transaction": {
    "id": "txn-id",
    "amount": 100.00,
    "currency": "USD",
    "status": "completed",
    "type": "payment",
    "description": "Online purchase",
    "created_at": "2025-01-01T00:00:00"
  }
}
```

#### GET /api/payments/transactions
Get transaction history with pagination.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Query Parameters:**
- `page` (optional, default: 1): Page number
- `per_page` (optional, default: 20): Items per page
- `status` (optional): Filter by status (pending, processing, completed, failed, refunded)

**Response (200 OK):**
```json
{
  "transactions": [...],
  "total": 50,
  "pages": 3,
  "current_page": 1
}
```

#### GET /api/payments/transactions/:id
Get a specific transaction.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "txn-id",
  "amount": 100.00,
  "currency": "USD",
  "status": "completed",
  ...
}
```

#### POST /api/payments/refund
Request a refund for a transaction.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "transaction_id": "txn-id",
  "amount": 100.00,
  "reason": "Customer request"
}
```

**Response (200 OK):**
```json
{
  "message": "Refund processed successfully",
  "refund": {
    "id": "ref-id",
    "transaction_id": "txn-id",
    "amount": 100.00,
    "status": "completed",
    ...
  }
}
```

#### GET /api/payments/methods
Get user's payment methods.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "payment_methods": [
    {
      "id": "pm-id",
      "type": "card",
      "provider": "visa",
      "last_four": "4242",
      "expiry_month": 12,
      "expiry_year": 2025,
      "is_default": true
    }
  ]
}
```

#### POST /api/payments/methods
Add a new payment method.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "type": "card",
  "provider": "visa",
  "last_four": "4242",
  "expiry_month": 12,
  "expiry_year": 2025,
  "is_default": false,
  "billing_address": "123 Main St, City, Country"
}
```

**Response (201 Created):**
```json
{
  "message": "Payment method added successfully",
  "payment_method": { ... }
}
```

---

### Wallets

#### GET /api/wallets/
Get all user wallets.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "wallets": [
    {
      "id": "wallet-id",
      "currency": "USD",
      "balance": 1000.00,
      "available_balance": 950.00,
      "pending_balance": 50.00
    }
  ]
}
```

#### GET /api/wallets/:currency
Get wallet for specific currency.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "wallet-id",
  "currency": "USD",
  "balance": 1000.00,
  "available_balance": 950.00,
  "pending_balance": 50.00
}
```

#### POST /api/wallets/transfer
Transfer funds to another user.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "recipient_email": "recipient@example.com",
  "amount": 50.00,
  "currency": "USD"
}
```

**Response (200 OK):**
```json
{
  "message": "Transfer completed successfully",
  "transaction": { ... },
  "new_balance": 950.00
}
```

#### POST /api/wallets/withdraw
Withdraw funds from wallet.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "amount": 100.00,
  "currency": "USD",
  "description": "Bank withdrawal"
}
```

**Response (200 OK):**
```json
{
  "message": "Withdrawal processed successfully",
  "transaction": { ... },
  "new_balance": 850.00
}
```

---

### Users

#### GET /api/users/profile
Get user profile.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Response (200 OK):**
```json
{
  "id": "user-id",
  "email": "user@example.com",
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

#### PUT /api/users/profile
Update user profile.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1234567890"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "user": { ... }
}
```

#### POST /api/users/change-password
Change user password.

**Headers:**
```
Authorization: Bearer <access-token>
```

**Request Body:**
```json
{
  "current_password": "OldPass123",
  "new_password": "NewPass456"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid or missing token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

## Rate Limiting

API requests are limited to 100 requests per hour per user. Exceeding this limit will result in a 429 Too Many Requests response.

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (e.g., httpOnly cookies, secure storage)
3. **Refresh tokens before they expire**
4. **Validate input on client side** before sending requests
5. **Handle errors gracefully** with user-friendly messages
6. **Log out users** when tokens expire
7. **Use pagination** for large datasets
8. **Implement retry logic** for failed requests
