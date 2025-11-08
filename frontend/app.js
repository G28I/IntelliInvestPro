// API Configuration
const API_BASE_URL = 'http://localhost:5000/api';
let authToken = localStorage.getItem('authToken');
let currentUser = null;

// Utility Functions
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.textContent = message;
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

async function apiRequest(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (authToken) {
        headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        throw error;
    }
}

function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showDashboard() {
    document.getElementById('authSection').style.display = 'none';
    document.getElementById('dashboardSection').classList.add('active');
}

function showAuth() {
    document.getElementById('authSection').style.display = 'flex';
    document.getElementById('dashboardSection').classList.remove('active');
}

function logout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    showAuth();
    showAlert('Logged out successfully', 'success');
}

// Authentication
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
        
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        currentUser = data.user;
        
        showAlert('Login successful!', 'success');
        loadDashboard();
        showDashboard();
    } catch (error) {
        showAlert(error.message, 'error');
    }
});

document.getElementById('registerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('regEmail').value;
    const username = document.getElementById('regUsername').value;
    const password = document.getElementById('regPassword').value;
    const first_name = document.getElementById('regFirstName').value;
    const last_name = document.getElementById('regLastName').value;
    
    try {
        const data = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify({ 
                email, 
                username, 
                password, 
                first_name, 
                last_name 
            })
        });
        
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        currentUser = data.user;
        
        showAlert('Registration successful!', 'success');
        loadDashboard();
        showDashboard();
    } catch (error) {
        showAlert(error.message, 'error');
    }
});

// Dashboard Functions
async function loadDashboard() {
    try {
        // Load user info
        const user = await apiRequest('/auth/me');
        document.getElementById('userName').textContent = user.username;
        document.getElementById('userEmail').textContent = user.email;
        
        // Load wallet
        await loadWallet();
        
        // Load transactions
        await loadTransactions();
    } catch (error) {
        showAlert('Failed to load dashboard: ' + error.message, 'error');
    }
}

async function loadWallet() {
    try {
        const data = await apiRequest('/wallets/USD');
        document.getElementById('walletBalance').textContent = data.balance.toFixed(2);
    } catch (error) {
        console.error('Failed to load wallet:', error);
    }
}

async function loadTransactions() {
    try {
        const data = await apiRequest('/payments/transactions?per_page=10');
        const transactionsList = document.getElementById('transactionsList');
        
        if (data.transactions.length === 0) {
            transactionsList.innerHTML = '<p>No transactions yet. Start by making a payment!</p>';
            return;
        }
        
        transactionsList.innerHTML = data.transactions.map(txn => `
            <div class="transaction-item">
                <div>
                    <div><strong>${txn.description || txn.type}</strong></div>
                    <div style="font-size: 0.9em; color: #666;">
                        ${new Date(txn.created_at).toLocaleString()}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="amount ${txn.amount > 0 ? 'positive' : 'negative'}">
                        ${txn.amount > 0 ? '+' : ''}$${Math.abs(txn.amount).toFixed(2)}
                    </div>
                    <div class="status ${txn.status}">${txn.status}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load transactions:', error);
    }
}

// Payment Modal
function showPaymentModal() {
    showModal('paymentModal');
}

document.getElementById('paymentForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = document.getElementById('paymentAmount').value;
    const description = document.getElementById('paymentDescription').value;
    
    try {
        const data = await apiRequest('/payments/process', {
            method: 'POST',
            body: JSON.stringify({ amount, description })
        });
        
        showAlert('Payment processed successfully!', 'success');
        closeModal('paymentModal');
        document.getElementById('paymentForm').reset();
        
        // Reload dashboard
        await loadWallet();
        await loadTransactions();
    } catch (error) {
        showAlert('Payment failed: ' + error.message, 'error');
    }
});

// Transfer Modal
function showTransferModal() {
    showModal('transferModal');
}

document.getElementById('transferForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const recipient_email = document.getElementById('transferEmail').value;
    const amount = document.getElementById('transferAmount').value;
    
    try {
        const data = await apiRequest('/wallets/transfer', {
            method: 'POST',
            body: JSON.stringify({ recipient_email, amount })
        });
        
        showAlert('Transfer completed successfully!', 'success');
        closeModal('transferModal');
        document.getElementById('transferForm').reset();
        
        // Reload dashboard
        await loadWallet();
        await loadTransactions();
    } catch (error) {
        showAlert('Transfer failed: ' + error.message, 'error');
    }
});

// Withdraw Modal
function showWithdrawModal() {
    showModal('withdrawModal');
}

document.getElementById('withdrawForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const amount = document.getElementById('withdrawAmount').value;
    const description = document.getElementById('withdrawDescription').value;
    
    try {
        const data = await apiRequest('/wallets/withdraw', {
            method: 'POST',
            body: JSON.stringify({ amount, description })
        });
        
        showAlert('Withdrawal processed successfully!', 'success');
        closeModal('withdrawModal');
        document.getElementById('withdrawForm').reset();
        
        // Reload dashboard
        await loadWallet();
        await loadTransactions();
    } catch (error) {
        showAlert('Withdrawal failed: ' + error.message, 'error');
    }
});

// Initialize
if (authToken) {
    loadDashboard();
    showDashboard();
} else {
    showAuth();
}
