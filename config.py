import os
from datetime import timedelta

class Config:
    """Base configuration"""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb+srv://ehsanpoint_db_user:nz7eUwWT8chu5Wpb@cluster0test.bmg2cu2.mongodb.net/?appName=Cluster0Test'
    )
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'dark_self_bot')
    
    # Telegram API
    API_ID = int(os.getenv('API_ID', '0'))
    API_HASH = os.getenv('API_HASH', '')
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # Admin credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    # Payment settings
    GEM_PRICE_TOMAN = int(os.getenv('GEM_PRICE_TOMAN', '40'))
    MINIMUM_GEMS = int(os.getenv('MINIMUM_GEMS', '80'))
    GEMS_PER_HOUR = int(os.getenv('GEMS_PER_HOUR', '2'))
    
    # Bank settings
    BANK_CARD_NUMBER = os.getenv('BANK_CARD_NUMBER', '')
    BANK_ACCOUNT_NAME = os.getenv('BANK_ACCOUNT_NAME', '')
    
    # Subscription
    REQUIRE_CHANNEL_SUBSCRIBE = os.getenv('REQUIRE_CHANNEL_SUBSCRIBE', 'true').lower() == 'true'
    SUBSCRIPTION_CHANNEL = os.getenv('SUBSCRIPTION_CHANNEL', '@your_channel')
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'false').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Features
    MAX_AUTO_ACTIONS = int(os.getenv('MAX_AUTO_ACTIONS', '10'))
    AUTO_REACTION_LIMIT = int(os.getenv('AUTO_REACTION_LIMIT', '3'))
    
    # UI
    BOT_NAME = 'DARK SELF BOT'
    BOT_VERSION = '1.0.0'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
