"""
🌟 DRAGON SELF BOT - All-in-One Application v2.0 🌟
یک ربات خودکار تلگرام با قابلیت‌های پیشرفته
✨ All Features + Website + Payment System + Telethon Handlers ✨
"""

# ============ IMPORTS ============
from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from mongoengine import (
    connect, disconnect, Document, StringField, IntField, BooleanField, 
    DateTimeField, ListField, DictField, EmbeddedDocument, EmbeddedDocumentField,
    EmailField, URLField, FloatField
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime, timedelta
from bson import ObjectId
import os
import base64
import jdatetime
import pytz
import json
import re
import asyncio
import threading
import requests
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

# Telethon Imports
from telethon import TelegramClient, events, functions, types
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession

load_dotenv()

# ============ CONFIGURATION ============
class Config:
    """Base configuration"""
    MONGODB_URI = os.getenv(
        'MONGODB_URI',
        'mongodb+srv://ehsanpoint_db_user:nz7eUwWT8chu5Wpb@cluster0test.bmg2cu2.mongodb.net/?appName=Cluster0Test'
    )
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'Dragon_self_bot')
    API_ID = int(os.getenv('API_ID', '9536480'))
    API_HASH = os.getenv('API_HASH', '4e52f6f12c47a0da918009260b6e3d44')
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8294693574:AAHFBuO6qlrBkAEEo0zFq0ViN26GfLuIEUU')
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'meta')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Ehsan138813')
    GEM_PRICE_TOMAN = int(os.getenv('GEM_PRICE_TOMAN', '40'))
    MINIMUM_GEMS = int(os.getenv('MINIMUM_GEMS', '80'))
    GEMS_PER_HOUR = int(os.getenv('GEMS_PER_HOUR', '2'))
    BANK_CARD_NUMBER = os.getenv('BANK_CARD_NUMBER', '6219861956353857')
    BANK_ACCOUNT_NAME = os.getenv('BANK_ACCOUNT_NAME', 'احسان حسین زاده')
    SECRET_KEY = os.getenv('SECRET_KEY', 'akjsbdojbuiawjb123y81313')
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAX_AUTO_ACTIONS = int(os.getenv('MAX_AUTO_ACTIONS', '10'))
    BOT_NAME = 'Dragon SELF BOT'
    BOT_VERSION = '2.0.0'

# ============ UTILITIES ============
IRAN_TZ = pytz.timezone('Asia/Tehran')

FONTS = {
    0: {'name': 'Normal', 'example': '12:34:56'},
    1: {'name': 'Subscript', 'example': '₁₂:₃₄:₅₆'},
    2: {'name': 'Superscript', 'example': '¹²:³⁴:⁵⁶'},
    3: {'name': 'Fullwidth', 'example': '１２:３４:５６'},
    4: {'name': 'Mathematical Bold', 'example': '𝟏𝟐:𝟑𝟒:𝟓𝟔'},
    5: {'name': 'Mathematical Double-struck', 'example': '𝟙𝟚:𝟛𝟜:𝟝𝟞'},
}

CHAR_MAP = {
    0: {'0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', ':': ':'},
    1: {'0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄', '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉', ':': ':'},
    2: {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', ':': ':'},
    3: {'0': '０', '1': '１', '2': '２', '3': '３', '4': '４', '5': '５', '6': '６', '7': '７', '8': '８', '9': '９', ':': '：'},
    4: {'0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗', ':': ':'},
    5: {'0': '𝟘', '1': '𝟙', '2': '𝟚', '3': '𝟛', '4': '𝟜', '5': '𝟝', '6': '𝟞', '7': '𝟟', '8': '𝟠', '9': '𝟡', ':': ':'},
}

TEXT_FORMATS = {
    'bold': {'name': '🔹 بولد', 'emoji': '🔹'},
    'italic': {'name': '🔸 ایتالیک', 'emoji': '🔸'},
    'underline': {'name': '🔹 زیرخط', 'emoji': '🔹'},
    'strikethrough': {'name': '🔸 خط خورده', 'emoji': '🔸'},
    'monospace': {'name': '🔹 کد', 'emoji': '🔹'},
    'spoiler': {'name': '🔸 اسپویلر', 'emoji': '🔸'},
}

MEDIA_LOCKS = {
    'gif': '🔒 قفل گیف',
    'photo': '🔒 قفل عکس',
    'video': '🔒 قفل ویدیو',
    'voice': '🔒 قفل ویس',
    'sticker': '🔒 قفل استیکر',
    'file': '🔒 قفل فایل',
    'music': '🔒 قفل موزیک',
    'video_note': '🔒 قفل ویدیو نوت',
    'contact': '🔒 قفل کانتکت',
    'location': '🔒 قفل لوکیشن',
    'emoji': '🔒 قفل ایموجی',
    'text': '🔒 قفل متن'
}

STATUS_ACTIONS = {
    'typing': '🎮 تایپ',
    'playing': '🎯 بازی',
    'recording_voice': '🎙 ضبط ویس',
    'uploading_photo': '📸 عکس',
    'uploading_video': '🎬 گیف',
}

def get_iran_now():
    return datetime.now(IRAN_TZ)

def format_iran_time(dt=None, font_id=0):
    if dt is None:
        dt = get_iran_now()
    time_str = dt.strftime('%H:%M')
    if font_id in CHAR_MAP:
        return ''.join(CHAR_MAP[font_id].get(c, c) for c in time_str)
    return time_str

def get_jalali_date(dt=None):
    if dt is None:
        dt = get_iran_now()
    j_date = jdatetime.datetime.fromgregorian(datetime=dt)
    return j_date.strftime('%Y/%m/%d')

def get_gregorian_date(dt=None):
    if dt is None:
        dt = get_iran_now()
    return dt.strftime('%Y/%m/%d')

def format_date(date_type='jalali', dt=None, font_id=0):
    if date_type == 'jalali':
        date_str = get_jalali_date(dt)
    else:
        date_str = get_gregorian_date(dt)
    if font_id in CHAR_MAP:
        return ''.join(CHAR_MAP[font_id].get(c, c) for c in date_str)
    return date_str

def apply_text_format(text, formats_dict):
    if formats_dict.get('reverse'):
        text = text[::-1]
    if formats_dict.get('bold'):
        text = f'**{text}**'
    if formats_dict.get('italic'):
        text = f'__{text}__'
    if formats_dict.get('underline'):
        text = f'__<u>{text}</u>__'
    if formats_dict.get('strikethrough'):
        text = f'~~{text}~~'
    if formats_dict.get('monospace'):
        text = f'`{text}`'
    if formats_dict.get('spoiler'):
        text = f'||{text}||'
    if formats_dict.get('quote'):
        text = f'❝ {text} ❞'
    return text

def translate_text(text, target_lang='fa'):
    # A simple fallback using free translation API format or Google Translate API
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={text}"
        response = requests.get(url)
        if response.status_code == 200:
            return ''.join([sentence[0] for sentence in response.json()[0]])
    except Exception as e:
        print(f"Translation error: {e}")
    return text

def get_all_features_menu():
    return """🌟 DRAGON SELF BOT - All Features Available 🌟"""

# ============ DATABASE MODELS ============

class AdminSettings(EmbeddedDocument):
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

class Admin(Document):
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
    is_authenticated = BooleanField(default=False)
    is_verified = BooleanField(default=False)
    gems = IntField(default=0)
    gems_spent = IntField(default=0)
    features_enabled = DictField(default={})
    is_premium = BooleanField(default=False)
    premium_until = DateTimeField()
    self_settings = DictField(default={
        # Additional state tracking to avoid external DB hits for fast toggles
        'format_bold': False, 'format_italic': False, 'format_underline': False,
        'format_strike': False, 'format_mono': False, 'format_spoiler': False,
        'format_mention': False, 'format_quote': False, 'format_hashtag': False,
        'format_reverse': False, 'format_gradual': False,
        'status_typing': False, 'status_playing': False, 'status_voice': False, 
        'status_photo': False, 'status_gif': False, 'status_seen': False,
        'trans_english': False, 'trans_chinese': False, 'trans_russian': False,
        'pv_lock': False, 'anti_login': False, 'secretary': False, 'comment': False
    })
    time_enabled = BooleanField(default=False)
    time_font = IntField(default=0)
    bio_time_enabled = BooleanField(default=False)
    bio_date_enabled = BooleanField(default=False)
    date_type = StringField(default='jalali')
    bio_time_font = IntField(default=0)
    pv_lock_enabled = BooleanField(default=False)
    copy_profile_enabled = BooleanField(default=False)
    forward_messages = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)
    last_active = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class UserSession(Document):
    meta = {'collection': 'user_sessions', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    session_string = StringField(required=True)
    api_id = IntField()
    api_hash = StringField()
    phone_code_hash = StringField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()

class Payment(Document):
    meta = {
        'collection': 'payments',
        'indexes': ['user_id', 'status', 'created_at']
    }
    user_id = IntField(required=True)
    gems = IntField(required=True)
    amount_toman = IntField(required=True)
    receipt_image = StringField()
    status = StringField(default='pending')
    approved_by_admin = IntField()
    approval_note = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    approved_at = DateTimeField()

class UserTextFormat(Document):
    meta = {'collection': 'user_text_formats', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    format_type = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

class UserMediaLock(Document):
    meta = {'collection': 'user_media_locks', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    media_type = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

class UserStatusAction(Document):
    meta = {'collection': 'user_status_actions', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    action_type = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

class UserTranslation(Document):
    meta = {'collection': 'user_translations', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    target_language = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

class UserComment(Document):
    meta = {'collection': 'user_comments', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    is_enabled = BooleanField(default=False)
    comment_text = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class UserSecretary(Document):
    meta = {'collection': 'user_secretaries', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    is_enabled = BooleanField(default=False)
    auto_reply_text = StringField()
    use_ai = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class UserAntiLogin(Document):
    meta = {'collection': 'user_anti_logins', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    is_enabled = BooleanField(default=False)
    alert_on_login = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

class UserAutoReaction(Document):
    meta = {'collection': 'user_auto_reactions', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    emoji = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

class UserLearning(Document):
    meta = {'collection': 'user_learning', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    input_text = StringField(required=True)
    output_text = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

class UserBlock(Document):
    meta = {'collection': 'user_blocks', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

class UserMute(Document):
    meta = {'collection': 'user_mutes', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

class UserAnimationPreset(Document):
    meta = {'collection': 'user_animation_presets', 'indexes': ['user_id']}
    user_id = IntField(required=True)
    preset_name = StringField(required=True)
    is_enabled = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)

class EnemyList(Document):
    meta = {'collection': 'enemy_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    responses = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)

class FriendList(Document):
    meta = {'collection': 'friend_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    responses = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)

class CrushList(Document):
    meta = {'collection': 'crush_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    messages = DictField(default={})
    created_at = DateTimeField(default=datetime.utcnow)

class SubscriptionChannel(Document):
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
    meta = {
        'collection': 'reports',
        'indexes': ['admin_id', 'target_id', 'status']
    }
    admin_id = IntField(required=True)
    target_id = IntField(required=True)
    target_type = StringField(choices=['channel', 'group', 'user'], required=True)
    target_username = StringField()
    target_title = StringField()
    reason = StringField(choices=['spam', 'scam', 'abuse', 'other'], default='spam')
    status = StringField(choices=['pending', 'deleted', 'skipped', 'reported'], default='pending')
    notes = StringField()
    delete_request_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)


# ============ TELETHON CLIENT MANAGER ============

class TelethonManager:
    """Manager to handle Telethon clients based on UserSessions"""
    def __init__(self):
        self.clients = {}
        self.loop = asyncio.get_event_loop()
        
    async def start_client(self, user_id, session_string):
        if user_id in self.clients:
            return
            
        try:
            client = TelegramClient(StringSession(session_string), Config.API_ID, Config.API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                self.clients[user_id] = client
                self.register_handlers(client, user_id)
                print(f"[+] Client initialized for User ID: {user_id}")
                
                # Start background tasks (Clock/Bio updater)
                self.loop.create_task(self.background_updater(client, user_id))
            else:
                print(f"[-] Client not authorized for User ID: {user_id}")
        except Exception as e:
            print(f"[-] Error starting client for {user_id}: {e}")

    async def background_updater(self, client, user_id):
        """Task to update Bio and Name with time if enabled"""
        while True:
            try:
                user = User.objects(telegram_id=user_id).first()
                if user and user.time_enabled:
                    time_str = format_iran_time(font_id=user.time_font)
                    if user.bio_time_enabled or user.bio_date_enabled:
                        bio_text = ""
                        if user.bio_time_enabled:
                            bio_text += f"🕒 {time_str} "
                        if user.bio_date_enabled:
                            date_str = format_date(user.date_type, font_id=user.bio_time_font)
                            bio_text += f"📅 {date_str}"
                        await client(functions.account.UpdateProfileRequest(about=bio_text))
                    
                    # Update Name with time if requested
                    # await client(functions.account.UpdateProfileRequest(first_name=f"{user.first_name} {time_str}"))
            except Exception as e:
                pass
            await asyncio.sleep(60)

    def register_handlers(self, client: TelegramClient, user_id):
        
        # ---------------- 1. Command Toggle Interceptor ----------------
        @client.on(events.NewMessage(outgoing=True))
        async def handle_commands(event):
            text = event.raw_text.strip()
            if not text:
                return

            user = User.objects(telegram_id=user_id).first()
            if not user:
                return

            # Helper to update settings
            def toggle_setting(key, state):
                user.self_settings[key] = state
                user.save()

            # Status and Action Toggle
            if re.match(r'^تایپ (روشن|خاموش)$', text):
                state = 'روشن' in text
                toggle_setting('status_typing', state)
                await event.edit(f"✅ حالت تایپ خودکار {'فعال' if state else 'غیرفعال'} شد.")
                return

            if re.match(r'^بازی (روشن|خاموش)$', text):
                state = 'روشن' in text
                toggle_setting('status_playing', state)
                await event.edit(f"✅ حالت بازی {'فعال' if state else 'غیرفعال'} شد.")
                return

            if re.match(r'^سین (روشن|خاموش)$', text):
                state = 'روشن' in text
                toggle_setting('status_seen', state)
                await event.edit(f"✅ سین خودکار پیام‌ها {'فعال' if state else 'غیرفعال'} شد.")
                return

            # Text Formatting Toggle
            formatting_commands = {
                'بولد': 'format_bold', 'ایتالیک': 'format_italic', 'زیرخط': 'format_underline',
                'خط خورده': 'format_strike', 'کد': 'format_mono', 'اسپویلر': 'format_spoiler',
                'منشن': 'format_mention', 'نقل و قول': 'format_quote', 'هشتگ': 'format_hashtag',
                'معکوس': 'format_reverse', 'تدریجی': 'format_gradual'
            }
            for cmd, key in formatting_commands.items():
                if re.match(f'^{cmd} (روشن|خاموش)$', text):
                    state = 'روشن' in text
                    toggle_setting(key, state)
                    await event.edit(f"✅ قالب‌بندی {cmd} {'فعال' if state else 'غیرفعال'} شد.")
                    return

            # Auto Translation
            if re.match(r'^ترجمه$', text) and event.is_reply:
                reply = await event.get_reply_message()
                translated = translate_text(reply.text, 'fa')
                await event.edit(f"**ترجمه:**\n{translated}")
                return

            trans_commands = {'انگلیسی': 'trans_english', 'چینی': 'trans_chinese', 'روسی': 'trans_russian'}
            for cmd, key in trans_commands.items():
                if re.match(f'^{cmd} (روشن|خاموش)$', text):
                    state = 'روشن' in text
                    toggle_setting(key, state)
                    await event.edit(f"✅ ترجمه خودکار به {cmd} {'فعال' if state else 'غیرفعال'} شد.")
                    return

            # Media Lock in PV Toggle
            if re.match(r'^قفل (گیف|عکس|ویدیو|ویس|استیکر|فایل|موزیک|ویدیو نوت|کانتکت|لوکیشن|ایموجی|متن) (روشن|خاموش)$', text):
                match = re.match(r'^قفل (.+) (روشن|خاموش)$', text)
                media_type = match.group(1)
                state = match.group(2) == 'روشن'
                
                # Update UserMediaLock DB directly for persistence
                lock_map = {'گیف': 'gif', 'عکس': 'photo', 'ویدیو': 'video', 'ویس': 'voice', 'استیکر': 'sticker',
                            'فایل': 'file', 'موزیک': 'music', 'ویدیو نوت': 'video_note', 'کانتکت': 'contact',
                            'لوکیشن': 'location', 'ایموجی': 'emoji', 'متن': 'text'}
                
                if media_type in lock_map:
                    db_type = lock_map[media_type]
                    lock = UserMediaLock.objects(user_id=user.id, media_type=db_type).first()
                    if not lock:
                        lock = UserMediaLock(user_id=user.id, media_type=db_type)
                    lock.is_enabled = state
                    lock.save()
                    await event.edit(f"✅ قفل {media_type} در پیوی {'فعال' if state else 'غیرفعال'} شد.")
                return

            # Time and Font
            if re.match(r'^ساعت (روشن|خاموش)$', text):
                user.time_enabled = 'روشن' in text
                user.save()
                await event.edit(f"✅ ساعت در نام {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                return
            
            if re.match(r'^ساعت بیو (روشن|خاموش)$', text):
                user.bio_time_enabled = 'روشن' in text
                user.save()
                await event.edit(f"✅ ساعت در بیو {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                return

            if re.match(r'^تاریخ بیو (روشن|خاموش)$', text):
                user.bio_date_enabled = 'روشن' in text
                user.save()
                await event.edit(f"✅ تاریخ در بیو {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                return

            # Message Management
            if text.startswith('حذف ') and text.split()[1].isdigit():
                count = int(text.split()[1])
                await event.delete()
                msgs = await client.get_messages(event.chat_id, limit=count)
                await client.delete_messages(event.chat_id, msgs)
                return

            if text == 'حذف همه':
                await event.delete()
                async for msg in client.iter_messages(event.chat_id, from_user='me'):
                    await msg.delete()
                return

            # Lists (Enemy, Friend, Crush) -> simplified toggles
            if re.match(r'^(دشمن|دوست) (روشن|خاموش)$', text):
                state = 'روشن' in text
                lst_type = "دشمن" if "دشمن" in text else "دوست"
                await event.edit(f"✅ لیست {lst_type} {'فعال' if state else 'غیرفعال'} شد.")
                return

            # Fun Animations
            fun_commands = ['قلب', 'heart', 'فان love', 'fun love', 'فان oclock', 'fun oclock', 'فان star', 'فان snow']
            if text in fun_commands:
                if 'قلب' in text or 'heart' in text:
                    hearts = ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "❤️"]
                    for h in hearts:
                        await event.edit(h)
                        await asyncio.sleep(0.3)
                elif 'oclock' in text:
                    clocks = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
                    for c in clocks:
                        await event.edit(c)
                        await asyncio.sleep(0.2)
                elif 'star' in text:
                    stars = ["⭐", "🌟", "✨", "💫", "🌟", "⭐"]
                    for s in stars:
                        await event.edit(s)
                        await asyncio.sleep(0.3)
                elif 'snow' in text:
                    snows = ["❄️", "🌨", "❄️", "⛄", "❄️"]
                    for s in snows:
                        await event.edit(s)
                        await asyncio.sleep(0.4)
                return

            # Tools
            if text in ['تگ', 'tagall']:
                await event.delete()
                async for user_obj in client.iter_participants(event.chat_id):
                    if not user_obj.bot:
                        await client.send_message(event.chat_id, f"[{user_obj.first_name}](tg://user?id={user_obj.id})")
                return

            if text in ['تگ ادمین ها', 'tagadmins']:
                await event.delete()
                async for admin_obj in client.iter_participants(event.chat_id, filter=types.ChannelParticipantsAdmins):
                    await client.send_message(event.chat_id, f"[{admin_obj.first_name}](tg://user?id={admin_obj.id})")
                return
            
            if text == 'شماره من':
                me = await client.get_me()
                await event.edit(f"شماره حساب شما: +{me.phone}")
                return

            if text == 'پین' and event.is_reply:
                reply = await event.get_reply_message()
                await client.pin_message(event.chat_id, reply.id)
                await event.delete()
                return

            if text.startswith('اسپم '):
                parts = text.split()
                if len(parts) >= 3 and parts[-1].isdigit():
                    count = int(parts[-1])
                    msg_text = " ".join(parts[1:-1])
                    await event.delete()
                    for _ in range(count):
                        await client.send_message(event.chat_id, msg_text)
                        await asyncio.sleep(0.1)
                return

            # ========================================================
            # If it's NOT a command, apply formatting or status to normal text
            # ========================================================
            
            # 1. Apply formatting
            new_text = event.raw_text
            should_edit = False

            if user.self_settings.get('format_reverse'):
                new_text = new_text[::-1]
                should_edit = True
            
            if user.self_settings.get('format_bold'):
                new_text = f"**{new_text}**"
                should_edit = True
                
            if user.self_settings.get('format_italic'):
                new_text = f"__{new_text}__"
                should_edit = True

            if user.self_settings.get('format_gradual'):
                # Typewriter effect
                temp_text = ""
                for char in event.raw_text:
                    temp_text += char
                    await event.edit(temp_text)
                    await asyncio.sleep(0.1)
                return # Already edited, exit

            # 2. Translate if translation is on
            if user.self_settings.get('trans_english'):
                new_text = translate_text(new_text, 'en')
                should_edit = True
            elif user.self_settings.get('trans_chinese'):
                new_text = translate_text(new_text, 'zh-CN')
                should_edit = True
            elif user.self_settings.get('trans_russian'):
                new_text = translate_text(new_text, 'ru')
                should_edit = True

            if should_edit and new_text != event.raw_text:
                await event.edit(new_text)


        # ---------------- 2. Incoming PV Interceptor (Locks & Auto-Seen) ----------------
        @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
        async def handle_incoming_pv(event):
            user = User.objects(telegram_id=user_id).first()
            if not user:
                return

            # Auto-Seen
            if user.self_settings.get('status_seen'):
                await client.send_read_acknowledge(event.chat_id)

            # Check PV Locks
            active_locks = UserMediaLock.objects(user_id=user.id, is_enabled=True).all()
            locked_types = [lock.media_type for lock in active_locks]

            should_delete = False
            if 'text' in locked_types and event.text and not event.media:
                should_delete = True
            if 'photo' in locked_types and event.photo:
                should_delete = True
            if 'video' in locked_types and event.video and not event.gif:
                should_delete = True
            if 'gif' in locked_types and event.gif:
                should_delete = True
            if 'voice' in locked_types and event.voice:
                should_delete = True
            if 'sticker' in locked_types and event.sticker:
                should_delete = True
            if 'music' in locked_types and event.audio and not event.voice:
                should_delete = True
            if 'file' in locked_types and event.document and not (event.audio or event.video or event.gif or event.sticker):
                should_delete = True

            if should_delete:
                await event.delete()
                return

            # Secretary / Auto Reply
            if user.self_settings.get('secretary'):
                sec = UserSecretary.objects(user_id=user.id).first()
                if sec and sec.is_enabled and sec.auto_reply_text:
                    await event.reply(sec.auto_reply_text)

        # ---------------- 3. Status Action Maintainer ----------------
        @client.on(events.NewMessage(outgoing=True))
        async def handle_status_actions(event):
            user = User.objects(telegram_id=user_id).first()
            if not user:
                return
            
            if user.self_settings.get('status_typing'):
                async with client.action(event.chat_id, 'typing'):
                    await asyncio.sleep(2)
            if user.self_settings.get('status_playing'):
                async with client.action(event.chat_id, 'game'):
                    await asyncio.sleep(2)


# ============ PAYMENT MANAGER ============

class PaymentManager:
    """Manage user payments and gems"""
    
    @staticmethod
    def get_gem_price():
        try:
            settings = Admin.objects.first()
            if settings and settings.settings:
                return settings.settings.gem_price_toman
        except:
            pass
        return 40
    
    @staticmethod
    def create_payment_request(user_id, gem_amount):
        gem_price = PaymentManager.get_gem_price()
        amount_toman = gem_amount * gem_price
        payment = Payment(
            user_id=user_id,
            gems=gem_amount,
            amount_toman=amount_toman,
            status='pending'
        )
        payment.save()
        return {
            'payment_id': str(payment.id),
            'gems': gem_amount,
            'amount_toman': amount_toman,
            'price_per_gem': gem_price,
            'status': 'pending'
        }
    
    @staticmethod
    def upload_receipt(payment_id, image_data):
        try:
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except:
            payment = None
        if not payment:
            return {'status': 'error', 'message': 'Payment not found'}
        payment.receipt_image = image_data
        payment.status = 'pending'
        payment.save()
        return {'status': 'success', 'message': 'Receipt uploaded'}
    
    @staticmethod
    def approve_payment(payment_id, admin_id, note=''):
        try:
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except:
            payment = None
        if not payment:
            return {'status': 'error', 'message': 'Payment not found'}
        user = User.objects(id=payment.user_id).first()
        if not user:
            return {'status': 'error', 'message': 'User not found'}
        user.gems += payment.gems
        payment.status = 'approved'
        payment.approved_by_admin = admin_id
        payment.approval_note = note
        payment.approved_at = datetime.utcnow()
        user.save()
        payment.save()
        return {
            'status': 'success',
            'message': f'Payment approved. {payment.gems} gems added',
            'total_gems': user.gems
        }
    
    @staticmethod
    def reject_payment(payment_id, admin_id, note=''):
        try:
            payment = Payment.objects(id=ObjectId(payment_id)).first()
        except:
            payment = None
        if not payment:
            return {'status': 'error', 'message': 'Payment not found'}
        payment.status = 'rejected'
        payment.approval_note = note
        payment.save()
        return {'status': 'success', 'message': 'Payment rejected'}
    
    @staticmethod
    def get_pending_payments():
        payments = Payment.objects(status='pending').all()
        return [{
            'id': str(p.id),
            'user_id': p.user_id,
            'gems': p.gems,
            'amount_toman': p.amount_toman,
            'status': p.status,
            'created_at': p.created_at.isoformat()
        } for p in payments]
    
    @staticmethod
    def get_user_gems(user_id):
        user = User.objects(id=ObjectId(user_id)).first()
        return user.gems if user else 0

class GemDeductionScheduler:
    """Handle automatic gem deduction"""
    scheduler = BackgroundScheduler()
    active_jobs = {}
    
    @staticmethod
    def start_deduction_for_user(user_id, interval_seconds=3600):
        try:
            if not GemDeductionScheduler.scheduler.running:
                GemDeductionScheduler.scheduler.start()
            
            job_id = f"deduction_{user_id}"
            if job_id not in GemDeductionScheduler.active_jobs:
                GemDeductionScheduler.scheduler.add_job(
                    GemDeductionScheduler.deduct_gems,
                    'interval',
                    seconds=interval_seconds,
                    args=[user_id],
                    id=job_id
                )
                GemDeductionScheduler.active_jobs[job_id] = True
        except:
            pass
    
    @staticmethod
    def stop_deduction_for_user(user_id):
        try:
            job_id = f"deduction_{user_id}"
            if job_id in GemDeductionScheduler.active_jobs:
                GemDeductionScheduler.scheduler.remove_job(job_id)
                del GemDeductionScheduler.active_jobs[job_id]
        except:
            pass
    
    @staticmethod
    def deduct_gems(user_id, gems_count=2):
        try:
            user = User.objects(id=ObjectId(user_id)).first()
            if user and user.gems >= gems_count:
                user.gems -= gems_count
                user.gems_spent += gems_count
                user.save()
        except:
            pass
    
    @staticmethod
    def check_minimum_gems(user_id):
        try:
            user = User.objects(id=ObjectId(user_id)).first()
            admin = Admin.objects(id=user.admin_id).first() if user else None
            minimum = admin.settings.minimum_gems_activate if admin and admin.settings else 80
            
            if not user:
                return {'has_minimum': False, 'gems': 0, 'required': minimum, 'remaining': minimum}
            
            if user.gems >= minimum:
                return {'has_minimum': True, 'gems': user.gems, 'required': minimum, 'remaining': 0}
            else:
                return {
                    'has_minimum': False,
                    'gems': user.gems,
                    'required': minimum,
                    'remaining': minimum - user.gems
                }
        except:
            return {'has_minimum': False, 'gems': 0, 'required': 80, 'remaining': 80}

# ============ AUTHENTICATION DECORATORS ============

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ============ FLASK ROUTES ============

def create_app():
    """Create and configure Flask app"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize MongoDB
    try:
        disconnect()
    except:
        pass
    
    connect(
        db=app.config.get('MONGODB_DB_NAME', 'Dragon_self_bot'),
        host=app.config.get('MONGODB_URI'),
        retryWrites=True,
        w='majority'
    )
    
    CORS(app)
    
    # Initialize default settings
    try:
        if Admin.objects.count() == 0:
            admin = Admin(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_active=True
            )
            admin.save()
        
        admin = Admin.objects.first()
        if admin and not admin.settings:
            admin.settings = AdminSettings()
            admin.save()
    except Exception as e:
        print(f"Error initializing: {e}")
    
    # Start scheduler
    try:
        if not GemDeductionScheduler.scheduler.running:
            GemDeductionScheduler.scheduler.start()
    except:
        pass
    
    @app.before_request
    def before_request():
        if request.path.startswith('/admin') and request.path != '/auth/admin/login':
            if 'admin_id' not in session:
                return redirect(url_for('admin_login'))
    
    # ============ AUTH ROUTES ============
    
    @app.route('/auth/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            data = request.get_json() or request.form
            username = data.get('username')
            password = data.get('password')
            
            admin = Admin.objects(username=username).first()
            
            if admin and check_password_hash(admin.password_hash, password):
                session['admin_id'] = str(admin.id)
                session['admin_username'] = admin.username
                session.permanent = True
                return jsonify({
                    'status': 'success',
                    'message': 'Login successful',
                    'redirect': '/admin/dashboard'
                })
            
            return jsonify({
                'status': 'error',
                'message': 'Invalid credentials'
            }), 401
        
        return render_template_string(LOGIN_TEMPLATE)
    
    @app.route('/auth/admin/logout', methods=['POST'])
    def admin_logout():
        session.clear()
        return jsonify({'status': 'success', 'message': 'Logged out'})
    
    # ============ ADMIN ROUTES ============
    
    @app.route('/admin/dashboard')
    @admin_required
    def dashboard():
        admin_id = ObjectId(session.get('admin_id'))
        users_count = User.objects(admin_id=admin_id).count()
        pending_payments = Payment.objects(status='pending').count()
        return render_template_string(DASHBOARD_TEMPLATE, 
            users=users_count, 
            pending=pending_payments
        )
    
    @app.route('/admin/settings', methods=['GET', 'POST'])
    @admin_required
    def settings():
        admin_id = ObjectId(session.get('admin_id'))
        admin = Admin.objects(id=admin_id).first()
        
        if request.method == 'POST':
            data = request.get_json()
            if admin:
                admin.settings.gem_price_toman = data.get('gem_price_toman', 40)
                admin.settings.minimum_gems_activate = data.get('minimum_gems_activate', 80)
                admin.settings.gems_per_hour = data.get('gems_per_hour', 2)
                admin.settings.bank_card_number = data.get('bank_card_number', '')
                admin.settings.bank_account_name = data.get('bank_account_name', '')
                admin.settings.updated_at = datetime.utcnow()
                admin.save()
            return jsonify({'status': 'success', 'message': 'Settings updated'})
        
        settings_data = admin.settings if admin else AdminSettings()
        return jsonify({
            'gem_price_toman': settings_data.gem_price_toman,
            'minimum_gems_activate': settings_data.minimum_gems_activate,
            'gems_per_hour': settings_data.gems_per_hour,
            'bank_card_number': settings_data.bank_card_number or '',
            'bank_account_name': settings_data.bank_account_name or ''
        })
    
    @app.route('/admin/users', methods=['GET'])
    @admin_required
    def users_list():
        admin_id = ObjectId(session.get('admin_id'))
        users = User.objects(admin_id=admin_id).all()
        return jsonify({
            'users': [{
                'id': str(u.id),
                'telegram_id': u.telegram_id,
                'username': u.username,
                'gems': u.gems,
                'created_at': u.created_at.isoformat()
            } for u in users]
        })
    
    @app.route('/admin/user/<user_id>/gems', methods=['POST'])
    @admin_required
    def add_gems(user_id):
        data = request.get_json()
        gems = data.get('gems', 0)
        
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        user.gems += gems
        user.save()
        return jsonify({'status': 'success', 'gems': user.gems})
    
    @app.route('/admin/payments', methods=['GET'])
    @admin_required
    def payments():
        payments = PaymentManager.get_pending_payments()
        return jsonify({'payments': payments})
    
    @app.route('/admin/payment/<payment_id>/approve', methods=['POST'])
    @admin_required
    def approve_payment(payment_id):
        admin_id = session.get('admin_id')
        result = PaymentManager.approve_payment(payment_id, admin_id)
        return jsonify(result)
    
    # ============ USER ROUTES ============
    
    @app.route('/user/<user_id>/profile', methods=['GET'])
    def user_profile(user_id):
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        return jsonify({
            'id': str(user.id),
            'gems': user.gems,
            'username': user.username
        })
    
    @app.route('/user/<user_id>/self/activate', methods=['POST'])
    def activate_self(user_id):
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        admin = Admin.objects(id=user.admin_id).first()
        is_admin = admin is not None
        
        if not is_admin:
            check = GemDeductionScheduler.check_minimum_gems(str(user.id))
            if not check['has_minimum']:
                return jsonify({
                    'status': 'error',
                    'message': f'Need {check["remaining"]} more gems'
                }), 400
        
        user.time_enabled = True
        if not is_admin:
            GemDeductionScheduler.start_deduction_for_user(str(user.id))
        
        user.save()
        return jsonify({
            'status': 'success',
            'message': 'Self-bot activated',
            'is_free': is_admin
        })
    
    # ============ PAYMENT ROUTES ============
    
    @app.route('/payment/buy-gems', methods=['POST'])
    def buy_gems():
        data = request.get_json()
        user_id = data.get('user_id')
        gem_amount = data.get('gem_amount')
        
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        info = PaymentManager.create_payment_request(user_id, gem_amount)
        admin = Admin.objects(id=user.admin_id).first()
        
        return jsonify({
            'status': 'success',
            'payment_id': info['payment_id'],
            'amount_toman': info['amount_toman'],
            'bank_card': admin.settings.bank_card_number if admin else '',
        })
    
    # ============ SELF-BOT FEATURES ROUTES ============
    
    @app.route('/user/<user_id>/features', methods=['GET'])
    def get_features(user_id):
        """Get all available features for user"""
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        features = {
            'text_formatting': ['bold', 'italic', 'underline', 'strikethrough', 'monospace', 'spoiler'],
            'media_locks': ['gif', 'photo', 'video', 'voice', 'sticker'],
            'status_actions': ['typing', 'playing', 'recording_voice', 'uploading_photo', 'uploading_video'],
            'auto_translation': ['english', 'chinese', 'arabic', 'spanish'],
            'auto_reactions': ['emoji_support', 'custom_reactions'],
            'protection': ['anti_login', 'anti_forward', 'anti_copy'],
            'secretary': ['auto_reply', 'ai_powered'],
            'lists': ['enemy_list', 'friend_list', 'crush_list', 'block_list', 'mute_list'],
            'animations': ['preset_support', 'custom_timings'],
        }
        
        return jsonify({
            'status': 'success',
            'features': features,
            'gems_available': user.gems
        })
    
    @app.route('/user/<user_id>/text-format/toggle', methods=['POST'])
    def toggle_text_format(user_id):
        """Toggle text formatting for user"""
        data = request.get_json()
        format_type = data.get('format_type')
        is_enabled = data.get('is_enabled', True)
        
        try:
            user_format = UserTextFormat.objects(user_id=user_id, format_type=format_type).first()
            if not user_format:
                user_format = UserTextFormat(user_id=user_id, format_type=format_type)
            
            user_format.is_enabled = is_enabled
            user_format.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Text format {format_type} {"enabled" if is_enabled else "disabled"}',
                'format_type': format_type
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/media-lock/toggle', methods=['POST'])
    def toggle_media_lock(user_id):
        """Toggle media lock for user"""
        data = request.get_json()
        media_type = data.get('media_type')
        is_enabled = data.get('is_enabled', True)
        
        try:
            media_lock = UserMediaLock.objects(user_id=user_id, media_type=media_type).first()
            if not media_lock:
                media_lock = UserMediaLock(user_id=user_id, media_type=media_type)
            
            media_lock.is_enabled = is_enabled
            media_lock.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Media lock {media_type} {"enabled" if is_enabled else "disabled"}',
                'media_type': media_type
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/status-action/toggle', methods=['POST'])
    def toggle_status_action(user_id):
        """Toggle status action for user"""
        data = request.get_json()
        action_type = data.get('action_type')
        is_enabled = data.get('is_enabled', True)
        
        try:
            action = UserStatusAction.objects(user_id=user_id, action_type=action_type).first()
            if not action:
                action = UserStatusAction(user_id=user_id, action_type=action_type)
            
            action.is_enabled = is_enabled
            action.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Status action {action_type} {"enabled" if is_enabled else "disabled"}',
                'action_type': action_type
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/translation/toggle', methods=['POST'])
    def toggle_translation(user_id):
        """Toggle auto-translation for user"""
        data = request.get_json()
        target_language = data.get('target_language')
        is_enabled = data.get('is_enabled', True)
        
        try:
            translation = UserTranslation.objects(user_id=user_id, target_language=target_language).first()
            if not translation:
                translation = UserTranslation(user_id=user_id, target_language=target_language)
            
            translation.is_enabled = is_enabled
            translation.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Translation to {target_language} {"enabled" if is_enabled else "disabled"}',
                'language': target_language
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/auto-reaction/toggle', methods=['POST'])
    def toggle_auto_reaction(user_id):
        """Toggle auto-reaction for user"""
        data = request.get_json()
        emoji = data.get('emoji', '👍')
        is_enabled = data.get('is_enabled', True)
        
        try:
            reaction = UserAutoReaction.objects(user_id=user_id, emoji=emoji).first()
            if not reaction:
                reaction = UserAutoReaction(user_id=user_id, emoji=emoji)
            
            reaction.is_enabled = is_enabled
            reaction.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Auto-reaction {emoji} {"enabled" if is_enabled else "disabled"}',
                'emoji': emoji
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/secretary/set', methods=['POST'])
    def set_secretary(user_id):
        """Set secretary/auto-reply message"""
        data = request.get_json()
        auto_reply_text = data.get('auto_reply_text', '')
        use_ai = data.get('use_ai', False)
        is_enabled = data.get('is_enabled', True)
        
        try:
            user = User.objects(id=ObjectId(user_id)).first()
            if not user:
                return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
            secretary = UserSecretary.objects(user_id=user_id).first()
            if not secretary:
                secretary = UserSecretary(user_id=user_id)
            
            secretary.auto_reply_text = auto_reply_text
            secretary.use_ai = use_ai
            secretary.is_enabled = is_enabled
            secretary.save()
            
            return jsonify({
                'status': 'success',
                'message': 'Secretary settings updated',
                'use_ai': use_ai
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/anti-login/toggle', methods=['POST'])
    def toggle_anti_login(user_id):
        """Toggle anti-login protection"""
        data = request.get_json()
        is_enabled = data.get('is_enabled', True)
        
        try:
            anti_login = UserAntiLogin.objects(user_id=user_id).first()
            if not anti_login:
                anti_login = UserAntiLogin(user_id=user_id)
            
            anti_login.is_enabled = is_enabled
            anti_login.save()
            
            return jsonify({
                'status': 'success',
                'message': f'Anti-login protection {"enabled" if is_enabled else "disabled"}'
            })
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/block/<int:target_id>', methods=['POST'])
    def add_block(user_id, target_id):
        """Add user to block list"""
        data = request.get_json()
        target_username = data.get('target_username', '')
        
        try:
            block = UserBlock.objects(user_id=user_id, target_id=target_id).first()
            if not block:
                block = UserBlock(
                    user_id=user_id,
                    target_id=target_id,
                    target_username=target_username
                )
                block.save()
                return jsonify({'status': 'success', 'message': 'User blocked'})
            else:
                return jsonify({'status': 'error', 'message': 'User already blocked'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    @app.route('/user/<user_id>/mute/<int:target_id>', methods=['POST'])
    def add_mute(user_id, target_id):
        """Add user to mute list"""
        data = request.get_json()
        target_username = data.get('target_username', '')
        
        try:
            mute = UserMute.objects(user_id=user_id, target_id=target_id).first()
            if not mute:
                mute = UserMute(
                    user_id=user_id,
                    target_id=target_id,
                    target_username=target_username
                )
                mute.save()
                return jsonify({'status': 'success', 'message': 'User muted'})
            else:
                return jsonify({'status': 'error', 'message': 'User already muted'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
    
    # ============ ADMIN ROUTES FOR USERS ============
    
    @app.route('/admin/user/<user_id>/features', methods=['GET'])
    @admin_required
    def admin_user_features(user_id):
        """Admin view user features"""
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        formats = UserTextFormat.objects(user_id=user_id).all()
        locks = UserMediaLock.objects(user_id=user_id).all()
        actions = UserStatusAction.objects(user_id=user_id).all()
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'gems': user.gems,
            'text_formats': [{
                'type': f.format_type,
                'enabled': f.is_enabled
            } for f in formats],
            'media_locks': [{
                'type': l.media_type,
                'enabled': l.is_enabled
            } for l in locks],
            'status_actions': [{
                'type': a.action_type,
                'enabled': a.is_enabled
            } for a in actions]
        })
    
    @app.route('/admin/user/<user_id>/self/activate-free', methods=['POST'])
    @admin_required
    def activate_self_free(user_id):
        """Admin activates self-bot for free"""
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        user.time_enabled = True
        user.save()
        
        return jsonify({
            'status': 'success',
            'message': f'Self-bot activated for {user.username} (FREE - Admin override)',
            'user_id': user_id,
            'is_free': True
        })
    
    return app

# ============ HTML TEMPLATES ============

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌟 Dragon SELF BOT - ورود ادمین</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', 'Vazir', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            align-items: center;
            max-width: 1000px;
            width: 100%;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: slideIn 0.5s ease;
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            text-align: center;
            color: #999;
            margin-bottom: 30px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #eee;
            border-radius: 8px;
            font-size: 14px;
            transition: all 0.3s;
            font-family: 'Segoe UI', sans-serif;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }
        button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
        }
        .message {
            margin-top: 20px;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            display: none;
            animation: slideIn 0.3s ease;
        }
        .success { 
            background: #d4edda; 
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .error { 
            background: #f8d7da; 
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .features {
            color: white;
            display: none;
        }
        .features h2 {
            margin-bottom: 20px;
            font-size: 22px;
        }
        .features-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        .feature-item {
            background: rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 8px;
            font-size: 13px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            .features {
                display: block;
            }
            .login-box {
                max-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div style="color: white; display: none;" class="features">
            <h2>✨ Dragon SELF BOT v2.0</h2>
            <div class="features-list">
                <div class="feature-item">📝 Text Formatting</div>
                <div class="feature-item">🔒 Media Locks</div>
                <div class="feature-item">⏰ Status Actions</div>
                <div class="feature-item">🌍 Auto Translation</div>
                <div class="feature-item">😊 Auto Reactions</div>
                <div class="feature-item">🛡️ Anti-Login Protection</div>
                <div class="feature-item">🤖 AI Secretary</div>
                <div class="feature-item">💎 Gem Payment System</div>
                <div class="feature-item">📋 User Management</div>
                <div class="feature-item">💳 Payment Processing</div>
                <div class="feature-item">⚙️ Full Admin Panel</div>
                <div class="feature-item">🚀 Free Admin Activation</div>
            </div>
        </div>

        <div class="login-box">
            <h1>🌟 Dragon SELF BOT</h1>
            <p class="subtitle">ربات خودکار تلگرام | Admin Login</p>
            
            <form id="loginForm">
                <div class="form-group">
                    <label for="username">👤 Username</label>
                    <input type="text" id="username" name="username" placeholder="admin" required>
                </div>
                <div class="form-group">
                    <label for="password">🔐 Password</label>
                    <input type="password" id="password" name="password" placeholder="••••••••" required>
                </div>
                <button type="submit">🚀 ورود به پنل ادمین</button>
            </form>
            
            <div id="message" class="message"></div>
            
            <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #999; font-size: 12px;">
                <p>🔒 Secure Admin Panel</p>
                <p>Version 2.0.0 - All-in-One System</p>
            </div>
        </div>
    </div>

    <script>
        // Show features on desktop
        if (window.innerWidth > 768) {
            document.querySelector('.features').style.display = 'block';
        }

        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const msg = document.getElementById('message');
            
            // Show loading state
            msg.textContent = '⏳ درحال بررسی...';
            msg.className = 'message success';
            msg.style.display = 'block';
            
            try {
                const response = await fetch('/auth/admin/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    msg.textContent = '✅ ' + data.message;
                    msg.className = 'message success';
                    msg.style.display = 'block';
                    setTimeout(() => window.location.href = data.redirect, 1500);
                } else {
                    msg.textContent = '❌ ' + data.message;
                    msg.className = 'message error';
                    msg.style.display = 'block';
                }
            } catch (error) {
                msg.textContent = '❌ خطا: ' + error;
                msg.className = 'message error';
                msg.style.display = 'block';
            }
        });
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dragon SELF BOT - Admin Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px 0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
        }
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        }
        h1 { margin: 0; font-size: 28px; }
        .header-buttons {
            display: flex;
            gap: 10px;
        }
        .btn-logout, .btn-refresh {
            background: rgba(255,255,255,0.2);
            border: 1px solid rgba(255,255,255,0.3);
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .btn-logout:hover, .btn-refresh:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            border-left: 5px solid #667eea;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.15);
        }
        .stat-label { color: #999; font-size: 13px; margin-bottom: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
        .stat-value { font-size: 36px; font-weight: bold; color: #667eea; }
        .stat-card:nth-child(2) { border-left-color: #f093fb; }
        .stat-card:nth-child(2) .stat-value { color: #f093fb; }
        .stat-card:nth-child(3) { border-left-color: #4facfe; }
        .stat-card:nth-child(3) .stat-value { color: #4facfe; }
        .section {
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        }
        h2 { color: #333; margin-bottom: 20px; font-size: 22px; border-bottom: 2px solid #667eea; padding-bottom: 15px; }
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        .btn-tertiary {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background: #f5f5f5;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .feature-box {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid #eee;
        }
        .feature-box:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        .feature-box.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>🌟 Dragon SELF BOT - Admin Panel v2.0</h1>
                <p style="margin-top: 5px; opacity: 0.9;">All Features Management System</p>
            </div>
            <div class="header-buttons">
                <button class="btn-refresh" onclick="location.reload()">🔄 Refresh</button>
                <button class="btn-logout" onclick="logout()">🚪 Logout</button>
            </div>
        </header>
        
        <div class="stats" id="statsContainer">
            <div class="stat-card">
                <div class="stat-label">Total Users</div>
                <div class="stat-value">{{ users }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Pending Payments</div>
                <div class="stat-value">{{ pending }}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Status</div>
                <div class="stat-value" style="color: #27ae60;">Active ✓</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Quick Actions</h2>
            <div class="action-buttons">
                <button class="btn" onclick="location.href='/admin/users'">👥 Manage Users</button>
                <button class="btn btn-secondary" onclick="location.href='/admin/payments'">💳 View Payments</button>
                <button class="btn btn-tertiary" onclick="location.href='/admin/settings'">⚙️ Settings</button>
            </div>
        </div>
        
        <div class="section">
            <h2>✨ Available Features</h2>
            <div class="features-grid">
                <div class="feature-box">📝 Text Formatting</div>
                <div class="feature-box">🔒 Media Locks</div>
                <div class="feature-box">⏰ Status Actions</div>
                <div class="feature-box">🌍 Auto Translation</div>
                <div class="feature-box">😊 Auto Reactions</div>
                <div class="feature-box">🛡️ Anti-Login</div>
                <div class="feature-box">🤖 Secretary AI</div>
                <div class="feature-box">📝 Block/Mute</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 System Information</h2>
            <table>
                <tr>
                    <td><strong>Bot Name:</strong></td>
                    <td>Dragon SELF BOT</td>
                </tr>
                <tr>
                    <td><strong>Version:</strong></td>
                    <td>2.0.0 - All-in-One</td>
                </tr>
                <tr>
                    <td><strong>Database:</strong></td>
                    <td>MongoDB Connected ✓</td>
                </tr>
                <tr>
                    <td><strong>Payment System:</strong></td>
                    <td>Active (Gems System)</td>
                </tr>
                <tr>
                    <td><strong>Admin Features:</strong></td>
                    <td>Free Self-Bot Activation Enabled</td>
                </tr>
            </table>
        </div>
    </div>

    <script>
        function logout() {
            if (confirm('Are you sure you want to logout?')) {
                fetch('/auth/admin/logout', {method: 'POST'})
                    .then(() => window.location.href = '/auth/admin/login');
            }
        }
    </script>
</body>
</html>
'''


# ============ ASYNC RUNNER FOR TELETHON ============
def run_telethon_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    manager = TelethonManager()
    
    async def check_users_periodically():
        while True:
            try:
                # Load all active user sessions from DB to run them
                sessions = UserSession.objects(is_active=True).all()
                for sess in sessions:
                    user = User.objects(telegram_id=sess.user_id).first()
                    # Start client only if self bot features are activated (gems checked etc.)
                    if user and user.time_enabled and sess.user_id not in manager.clients:
                        await manager.start_client(sess.user_id, sess.session_string)
            except Exception as e:
                print(f"Error checking DB for users: {e}")
            await asyncio.sleep(10)
            
    loop.create_task(check_users_periodically())
    print("[+] Telethon loop started.")
    loop.run_forever()


# ============ RUN APP ============

if __name__ == '__main__':
    app = create_app()
    print("""
╔════════════════════════════════════════════════════════════════╗
║     🌟 Dragon SELF BOT v2.0.0 - All-in-One System 🌟          ║
║                                                                ║
║  ✨ Features:                                                  ║
║    ✓ Text Formatting (Bold, Italic, Underline, etc)          ║
║    ✓ Media Locks (Photo, Video, Voice, Sticker, GIF, etc)    ║
║    ✓ Status Actions (Typing, Playing, Recording, etc)        ║
║    ✓ Auto Translation (Multi-language support)               ║
║    ✓ Auto Reactions (Custom emoji reactions)                 ║
║    ✓ Anti-Login Protection (Security feature)                ║
║    ✓ AI Secretary (Auto-reply with AI)                       ║
║    ✓ Block/Mute Lists (User management)                      ║
║    ✓ Payment System (Gems-based)                             ║
║    ✓ Admin Panel (Complete control)                          ║
║    ✓ Free Self-Bot for Admins                                ║
║                                                                ║
║  📍 Server: http://localhost:5000                            ║
║  🚪 Login: http://localhost:5000/auth/admin/login            ║
║  👤 Default: admin / admin123                                ║
║                                                                ║
║  🗄️ Database: MongoDB Connected                              ║
║  🔄 Scheduler: APScheduler Active                            ║
║  💎 Payment: Toman-based Gem System                          ║
║  🌐 Telethon: Running Async Background Event Loop            ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Run Telethon event loop in a background thread so it doesn't block Flask
    telethon_thread = threading.Thread(target=run_telethon_loop)
    telethon_thread.daemon = True
    telethon_thread.start()
    
    # Run Flask Application
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
