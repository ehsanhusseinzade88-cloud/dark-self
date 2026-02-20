"""
MongoDB Models using MongoEngine
Dark Self Bot Database Schema
"""

from mongoengine import (
    Document, StringField, IntField, BooleanField, DateTimeField,
    ListField, DictField, ReferenceField, EmbeddedDocument, EmbeddedDocumentField,
    EmailField, URLField
)
from datetime import datetime
import json


# ============= EMBEDDED DOCUMENTS =============

class AdminSettings(EmbeddedDocument):
    """Admin settings embedded in Admin document"""
    gem_price_toman = IntField(default=40)
    minimum_gems_activate = IntField(default=80)
    gems_per_hour = IntField(default=2)
    bank_card_number = StringField()
    bank_account_name = StringField()
    require_subscription = BooleanField(default=True)
    subscription_channel = StringField()
    max_users = IntField(default=0)
    self_timeout = IntField(default=3600)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

# ============= MAIN DOCUMENTS =============

class Admin(Document):
    """Admin User"""
    meta = {
        'collection': 'admins',
        'indexes': ['username', 'telegram_id']
    }
    
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    telegram_id = IntField(unique=True, sparse=True)
    is_active = BooleanField(default=True)
    settings = EmbeddedDocumentField(AdminSettings, default=AdminSettings)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class User(Document):
    """User Account"""
    meta = {
        'collection': 'users',
        'indexes': ['telegram_id', 'phone_number', 'admin_id']
    }
    
    admin_id = IntField(required=True)
    telegram_id = IntField(unique=True, required=True)
    phone_number = StringField(required=True)
    username = StringField()
    first_name = StringField()
    last_name = StringField()
    
    # Account status
    is_authenticated = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    
    # Gems (currency)
    gems = IntField(default=0)
    gems_spent = IntField(default=0)
    
    # Features status
    features_enabled = DictField(default={})
    
    # Subscription
    is_premium = BooleanField(default=False)
    premium_until = DateTimeField()
    
    # Self settings
    self_settings = DictField(default={})
    
    # Time settings
    time_enabled = BooleanField(default=False)
    time_font = IntField(default=0)
    bio_time_enabled = BooleanField(default=False)
    bio_date_enabled = BooleanField(default=False)
    date_type = StringField(default='jalali')
    bio_time_font = IntField(default=0)
    
    # Privacy settings
    pv_lock_enabled = BooleanField(default=False)
    copy_profile_enabled = BooleanField(default=False)
    forward_messages = DictField(default={})
    
    # Tracking
    created_at = DateTimeField(default=datetime.utcnow)
    last_active = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)



class UserSession(Document):
    """User Telegram Session"""
    meta = {
        'collection': 'user_sessions',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    session_string = StringField(required=True)
    api_id = IntField()
    api_hash = StringField()
    phone_code_hash = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()




class UserFeature(Document):
    """User Feature Settings"""
    meta = {
        'collection': 'user_features',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    feature_name = StringField(required=True)
    is_enabled = BooleanField(default=False)
    settings = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)


class EnemyList(Document):
    """Enemy List"""
    meta = {
        'collection': 'enemy_lists',
        'indexes': ['user_id', 'target_id']
    }
    
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    responses = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)


class FriendList(Document):
    """Friend List"""
    meta = {
        'collection': 'friend_lists',
        'indexes': ['user_id', 'target_id']
    }
    
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    responses = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)


class CrushList(Document):
    """Crush List"""
    meta = {
        'collection': 'crush_lists',
        'indexes': ['user_id', 'target_id']
    }
    
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    messages = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)


class Payment(Document):
    """Payment Record"""
    meta = {
        'collection': 'payments',
        'indexes': ['user_id', 'status', 'created_at']
    }
    
    user_id = IntField(required=True)
    gems = IntField(required=True)
    amount_toman = IntField(required=True)
    receipt_image = StringField()  # Base64 encoded image
    
    # Status
    status = StringField(default='pending')  # pending, approved, rejected
    approved_by_admin = IntField()
    approval_note = StringField()
    
    created_at = DateTimeField(default=datetime.utcnow)
    approved_at = DateTimeField()


class TextFormat(Document):
    """Text Format Options"""
    meta = {
        'collection': 'text_formats'
    }
    
    format_name = StringField(unique=True, required=True)
    enabled = BooleanField(default=True)
    description = StringField()


class Font(Document):
    """Font Styles"""
    meta = {
        'collection': 'fonts'
    }
    
    name = StringField(required=True)
    emoji = StringField()
    sample_text = StringField()
    alphabet = StringField()


class UserTextFormat(Document):
    """User Text Formatting Settings"""
    meta = {
        'collection': 'user_text_formats',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    format_type = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


class UserMediaLock(Document):
    """User Media Locks in Private Messages"""
    meta = {
        'collection': 'user_media_locks',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    media_type = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


class UserStatusAction(Document):
    """User Status and Action Settings"""
    meta = {
        'collection': 'user_status_actions',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    action_type = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


class UserTranslation(Document):
    """User Auto-Translation Settings"""
    meta = {
        'collection': 'user_translations',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    target_language = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


class UserComment(Document):
    """User Comment/Reply Settings"""
    meta = {
        'collection': 'user_comments',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    is_enabled = BooleanField(default=False)
    comment_text = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class UserSecretary(Document):
    """User Secretary/Auto-Reply Settings"""
    meta = {
        'collection': 'user_secretaries',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    is_enabled = BooleanField(default=False)
    auto_reply_text = StringField()
    use_ai = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class UserAntiLogin(Document):
    """User Anti-Login Protection"""
    meta = {
        'collection': 'user_anti_logins',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    is_enabled = BooleanField(default=False)
    alert_on_login = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)


class UserAutoReaction(Document):
    """User Auto-Reaction Settings"""
    meta = {
        'collection': 'user_auto_reactions',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    emoji = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


class UserLearning(Document):
    """User AI Learning Data"""
    meta = {
        'collection': 'user_learning',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    input_text = StringField(required=True)
    output_text = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)


class UserBlock(Document):
    """User Block List"""
    meta = {
        'collection': 'user_blocks',
        'indexes': ['user_id', 'target_id']
    }
    
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)


class UserMute(Document):
    """User Mute List"""
    meta = {
        'collection': 'user_mutes',
        'indexes': ['user_id', 'target_id']
    }
    
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)


class UserAnimationPreset(Document):
    """User Animation Presets"""
    meta = {
        'collection': 'user_animation_presets',
        'indexes': ['user_id']
    }
    
    user_id = IntField(required=True)
    preset_name = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)


class SubscriptionChannel(Document):
    """Mandatory Subscription Channels"""
    meta = {
        'collection': 'subscription_channels',
        'indexes': ['admin_id', 'channel_id']
    }
    
    admin_id = IntField(required=True)
    channel_id = IntField(required=True)
    channel_username = StringField()
    channel_title = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


class Report(Document):
    """Report Management (Spam, Scam, etc)"""
    meta = {
        'collection': 'reports',
        'indexes': ['admin_id', 'target_id', 'status']
    }
    
    admin_id = IntField(required=True)
    target_id = IntField(required=True)  # Channel/Group/User ID
    target_type = StringField(choices=['channel', 'group', 'user'], required=True)
    target_username = StringField()
    target_title = StringField()
    reason = StringField(choices=['spam', 'scam', 'abuse', 'other'], default='spam')
    status = StringField(choices=['pending', 'deleted', 'skipped', 'reported'], default='pending')
    notes = StringField()
    delete_request_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)