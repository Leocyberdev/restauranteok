#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -c "
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
from src.main import app, db
from flask_migrate import upgrade

with app.app_context():
    # Create tables if they don't exist
    db.create_all()
    
    # Try to run migrations if migration folder exists
    try:
        upgrade()
        print('Migrations applied successfully')
    except Exception as e:
        print(f'Migration error (this is normal for first deploy): {e}')
        print('Tables created successfully')
"

