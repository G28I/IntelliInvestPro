"""Main Flask application factory"""
import sys
import os
# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config.config import config
from backend.models import db

migrate = Migrate()
jwt = JWTManager()

def create_app(config_name='development'):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from backend.routes import auth, payments, users, wallets
    app.register_blueprint(auth.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(wallets.bp)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.route('/')
    def index():
        """API health check endpoint"""
        return jsonify({
            'status': 'online',
            'service': 'IntelliPay - World-Class Payments API',
            'version': '1.0.0'
        })
    
    @app.route('/health')
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy'}), 200
    
    return app

if __name__ == '__main__':
    import os
    app = create_app()
    # Only enable debug in development, never in production
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
