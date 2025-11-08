"""Initialize the database"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.models import db

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
        print('✅ Database tables created successfully')
        print(f'📍 Database location: {app.config["SQLALCHEMY_DATABASE_URI"]}')
