#!/usr/bin/env python
"""
DARK SELF BOT - Quick Start Script
Run this for the first time setup
"""

import os
import sys
from pathlib import Path

def main():
    print("""
    ╔══════════════════════════════════════════════════╗
    ║         🌟 DARK SELF BOT - Setup Guide 🌟       ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    # Check if .env exists
    if not Path('.env').exists():
        print("\n⚠️  .env file not found!")
        print("📋 Creating .env from .env.example...\n")
        
        if Path('.env.example').exists():
            with open('.env.example', 'r') as f:
                content = f.read()
            with open('.env', 'w') as f:
                f.write(content)
            print("✅ .env file created!")
            print("📝 Please edit .env with your credentials:\n")
            print("   1. Open .env in text editor")
            print("   2. Add your Telegram API_ID and API_HASH")
            print("   3. Add your BOT_TOKEN")
            print("   4. Configure admin username/password")
            print("   5. Add bank details")
        else:
            print("❌ .env.example not found")
            sys.exit(1)
    else:
        print("✅ .env file found")
    
    # Check requirements
    print("\n📦 Checking dependencies...\n")
    
    try:
        import flask
        print("✅ Flask installed")
    except ImportError:
        print("❌ Flask not installed. Run: pip install -r requirements.txt")
        sys.exit(1)
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy installed")
    except ImportError:
        print("❌ Flask-SQLAlchemy not installed")
        sys.exit(1)
    
    try:
        import telethon
        print("✅ Telethon installed")
    except ImportError:
        print("❌ Telethon not installed")
        sys.exit(1)
    
    # Initialize database
    print("\n🔧 Initializing database...\n")
    
    try:
        from app import create_app, db
        app = create_app()
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created")
            
            # Create default admin
            from models import Admin
            from werkzeug.security import generate_password_hash
            
            if not Admin.query.first():
                admin = Admin(
                    username='admin',
                    password_hash=generate_password_hash('admin123')
                )
                db.session.add(admin)
                db.session.commit()
                print("✅ Default admin user created")
                print("   Username: admin")
                print("   Password: admin123")
                print("\n⚠️  CHANGE THIS PASSWORD IN .env FILE!\n")
            else:
                print("✅ Admin user already exists")
    
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)
    
    # Final instructions
    print("""
    ╔════════════════════════════════════════════════════╗
    ║          ✅ Setup Complete! Ready to Run          ║
    ╚════════════════════════════════════════════════════╝
    
    🚀 To start the bot, run:
    
       python app.py
    
    🌐 Access the admin panel at:
    
       http://localhost:5000/auth/admin/login
    
    📱 Default Credentials:
    
       Username: admin
       Password: admin123
    
    ⚠️  IMPORTANT:
    
       1. Edit .env with your Telegram API credentials
       2. Change admin password immediately
       3. Add bank details for payment system
       4. Configure subscription channel if needed
    
    📖 For more info, see README.md
    
    ╚════════════════════════════════════════════════════╝
    """)

if __name__ == '__main__':
    main()
