from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from mongoengine import connect, disconnect
from models import Admin, User, AdminSettings, Payment
from config import config
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from payment_handler import PaymentManager, GemDeductionScheduler
import os
import certifi
from dotenv import load_dotenv

load_dotenv()

def create_app(config_name=None):
    """Application factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize MongoDB
    try:
        disconnect()  # Disconnect any existing connections
    except:
        pass
    
    connect(
        db=app.config.get('MONGODB_DB_NAME', 'dark_self_bot'),
        host=app.config.get('MONGODB_URI'),
        tlsCAFile=certifi.where(),
        retryWrites=True,
        w='majority'
    )
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    from routes import auth_bp, admin_bp, user_bp, payment_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    
    # Initialize default settings
    init_default_settings()
    
    # Start gem deduction scheduler
    GemDeductionScheduler.scheduler.start()
    
    @app.before_request
    def before_request():
        """Check admin authentication"""
        if request.path.startswith('/admin') and request.path != '/admin/login':
            if 'admin_id' not in session:
                return redirect(url_for('auth.admin_login'))
    
    return app


def init_default_settings():
    """Initialize default admin settings"""
    try:
        if Admin.objects.count() == 0:
            # Create default admin
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_active=True
            )
            admin.save()
        
        # Ensure admin has settings
        admin = Admin.objects.first()
        if admin and not admin.settings:
            admin.settings = AdminSettings()
            admin.save()
    except Exception as e:
        print(f"Error initializing default settings: {e}")


if __name__ == '__main__':
    app = create_app()
    # Get port dynamically for cloud environments like Render
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
