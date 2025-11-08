#!/bin/bash

# IntelliPay Startup Script

echo "🚀 Starting IntelliPay - World-Class Payments Application"
echo "=========================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Initialize database
echo "💾 Initializing database..."
cd backend
python -c "from app import create_app; from models import db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized successfully')"

# Start the application
echo ""
echo "🎉 Starting IntelliPay server..."
echo "📍 API will be available at: http://localhost:5000"
echo "📍 Frontend: Open frontend/index.html in your browser"
echo ""
python app.py
