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
from telethon.tl.custom import Button

load_dotenv()

# ============ CONFIGURATION ============
class Config:
    """Base configuration"""
    MONGODB_URI = 'mongodb+srv://ehsanpoint_db_user:nz7eUwWT8chu5Wpb@cluster0test.bmg2cu2.mongodb.net/?appName=Cluster0Test'
    MONGODB_DB_NAME = 'Dragon_self_bot'
    API_ID = 9536480
    API_HASH = '4e52f6f12c47a0da918009260b6e3d44'
    BOT_TOKEN = '8294693574:AAHFBuO6qlrBkAEEo0zFq0ViN26GfLuIEUU'
    ADMIN_USERNAME = 'meta'
    ADMIN_PASSWORD = 'Ehsan138813'
    GEM_PRICE_TOMAN = 40
    MINIMUM_GEMS = 80
    GEMS_PER_HOUR = 2
    BANK_CARD_NUMBER = '6219861956353857'
    BANK_ACCOUNT_NAME = 'احسان حسین زاده'
    SECRET_KEY = 'akjsbdojbuiawjb123y81313'
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    MAX_AUTO_ACTIONS = 10
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
    is_telegram_premium = BooleanField(default=False)
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
        'pv_lock': False, 'anti_login': False, 'comment': False
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

class DiscountCode(Document):
    """Discount Codes for buying gems"""
    meta = {'collection': 'discount_codes', 'indexes': ['code']}
    code = StringField(required=True, unique=True)
    discount_percentage = IntField(required=True)
    max_uses = IntField(required=True)
    current_uses = IntField(default=0)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

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
    is_mandatory = BooleanField(default=False)
    expiration_days = IntField(default=0)  # 0 = لا محدود، >0 = روزهای اعتبار
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class UserSubscription(Document):
    """Track user's mandatory channel subscriptions"""
    meta = {
        'collection': 'user_subscriptions',
        'indexes': ['user_id', 'channel_id']
    }
    user_id = IntField(required=True)
    channel_id = IntField(required=True)
    subscribed_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField()
    is_valid = BooleanField(default=True)

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

GLOBAL_TELETHON_MANAGER = None

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
                
                # Check Premium (Stars) & Send Welcome Message
                try:
                    me = await client.get_me()
                    user_obj = User.objects(telegram_id=user_id).first()
                    if user_obj:
                        user_obj.is_telegram_premium = getattr(me, 'premium', False)
                        user_obj.save()
                    if getattr(me, 'premium', False):
                        await client.send_message('me', '🌟 اکانت شما تایید شده و دارای پرمیوم/استارز است!')
                except Exception as e:
                    print(f"[-] Error checking premium status: {e}")
                
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

            if text == 'پنل':
                active_locks = UserMediaLock.objects(user_id=user.id, is_enabled=True).all()
                locked_types = [lock.media_type for lock in active_locks]
                def lck(t): return '✅' if t in locked_types else '❌'
                def st(k): return '✅' if user.self_settings.get(k) else '❌'
                
                # بررسی اگر ادمین است
                admin_db = Admin.objects.first()
                is_admin_user = admin_db and admin_db.telegram_id == user_id
                
                if is_admin_user:
                    # پنل مخصوص ادمین
                    panel_text = """
╔══════════════════════════════════════════╗
║        👑 پنل ادمین - Dragon SELF BOT    ║
╚══════════════════════════════════════════╝

**🎛️ وضعیت ادمین:**
• جم: نامحدود ♾️
• دسترسی: مدیریت کامل ✅
• وب‌پنل: فعال ✅

**📋 دستورات ادمین:**
`مدیریت کاربران` - مدیریت و کنترل
`پیام همگانی` - ارسال به تمام کاربران
`عضویت اجباری` - تنظیمات کانال‌ها
`سلف فعال` - برای خود
`پنل درج` - وب‌پنل

**⚙️ میانبرها:**
• وب‌پنل برای مدیریت
• مشاهده آمارها
• تایید پرداخت‌ها
"""
                else:
                    # پنل عادی کاربر
                    panel_text = f"""
╔════════════════════════════════════════════╗
║    🎛 پنل سلف بات - وضعیت فعلی            ║
╚════════════════════════════════════════════╝

**🔸 وضعیت اکشن‌ها:**
تایپ: {st('status_typing')} | بازی: {st('status_playing')} | سین: {st('status_seen')}

**🔹 قالب‌بندی متن:**
بولد: {st('format_bold')} | ایتالیک: {st('format_italic')} | زیرخط: {st('format_underline')}

**🔸 قفل‌های پیوی:**
متن: {lck('text')} | عکس: {lck('photo')} | ویدیو: {lck('video')} | گیف: {lck('gif')}

**💎 جم موجود:** {user.gems}

📚 دستور `راهنما` برای کمک
"""
                await event.edit(panel_text)
                return

            if text == 'راهنما':
                help_text = """
╔════════════════════════════╗
║       📚 راهنمای جامع      ║
╚════════════════════════════╝

**🔸 اکشن‌ها:**
`تایپ روشن` / `تایپ خاموش` ➜ تایپ درحال نمایش
`بازی روشن` / `بازی خاموش` ➜ بازی درحال نمایش
`سین روشن` / `سین خاموش` ➜ خواندن خودکار پیوی

**🔸 متن و قالب:**
`بولد روشن`/`خاموش` ➜ ضخیم کردن متن
`ایتالیک روشن`/`خاموش` ➜ کج کردن متن
`زیرخط روشن`/`خاموش` ➜ خط زیر متن
`خط خورده روشن`/`خاموش` ➜ خط روی متن
`کد روشن`/`خاموش` ➜ حالت کد برنامه نویسی
`اسپویلر روشن`/`خاموش` ➜ مخفی کردن متن
`معکوس روشن`/`خاموش` ➜ برعکس نوشتن متن
`تدریجی روشن`/`خاموش` ➜ تایپ تک به تک حروف

**🔸 قفل‌های پیوی (حذف خودکار پیام دریافتی):**
`قفل گیف روشن` / `خاموش`
`قفل عکس روشن` / `خاموش`
*(سایر قفل‌ها: ویدیو، ویس، استیکر، متن، موزیک، فایل، ویدیو نوت، کانتکت، لوکیشن، ایموجی)*

**🔸 کاربردی:**
`ساعت روشن` / `خاموش` ➜ ساعت در نام شما
`ساعت بیو روشن` / `خاموش` ➜ ساعت در بیو
`تاریخ بیو روشن` / `خاموش` ➜ تاریخ در بیو
`ترجمه` ➜ (ریپلای) ترجمه متن به فارسی
`انگلیسی روشن`/`خاموش` ➜ ترجمه خودکار چت شما به انگلیسی
`(چینی و روسی هم پشتیبانی می‌شود)`

**🔸 مدیریت پیام و ابزارها:**
`حذف [عدد]` ➜ حذف N پیام اخیر خودتان
`حذف همه` ➜ حذف تمام پیام‌های شما در آن چت
`تگ` یا `tagall` ➜ تگ همه اعضای گروه
`تگ ادمین ها` ➜ تگ ادمین‌ها
`پین` ➜ (ریپلای) پین پیام
`اسپم [متن] [تعداد]` ➜ ارسال رگباری متن
`شماره من` ➜ نمایش شماره اکانت
`(دوست روشن/خاموش)` و `(دشمن روشن/خاموش)` ➜ روشن کردن لیست دوستان/دشمنان

**🔸 سرگرمی (انیمیشن‌ها):**
`قلب` | `فان love` | `فان oclock` | `فان star` | `فان snow`
"""
                await event.edit(help_text)
                return

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

            # Lists (Enemy, Friend, Crush) - Full Logic
            if re.match(r'^(دشمن|دوست|کراش) (روشن|خاموش)$', text):
                lst_type = text.split()[0]
                state = 'روشن' in text
                key = 'enemy_enabled' if lst_type == 'دشمن' else ('friend_enabled' if lst_type == 'دوست' else 'crush_enabled')
                toggle_setting(key, state)
                await event.edit(f"✅ پاسخ خودکار لیست {lst_type} {'فعال' if state else 'غیرفعال'} شد.")
                return
            
            async def manage_list_target(event, text, action, list_type, model_class):
                if not event.is_reply:
                    await event.edit("❌ لطفا روی پیام شخص مورد نظر ریپلای کنید.")
                    return
                reply = await event.get_reply_message()
                target_id = reply.sender_id
                
                if action == 'add':
                    existing = model_class.objects(user_id=user.id, target_id=target_id).first()
                    if not existing:
                        model_class(user_id=user.id, target_id=target_id).save()
                    await event.edit(f"✅ کاربر به لیست {list_type} اضافه شد.")
                elif action == 'remove':
                    model_class.objects(user_id=user.id, target_id=target_id).delete()
                    await event.edit(f"✅ کاربر از لیست {list_type} حذف شد.")

            # Enemy Commands
            if text == 'تنظیم دشمن' or text == 'افزودن دشمن':
                await manage_list_target(event, text, 'add', 'دشمن', EnemyList)
                return
            if text == 'حذف دشمن':
                await manage_list_target(event, text, 'remove', 'دشمن', EnemyList)
                return
            if text == 'پاکسازی لیست دشمن':
                EnemyList.objects(user_id=user.id).delete()
                await event.edit("✅ لیست دشمن پاکسازی شد.")
                return
            if text == 'لیست دشمن':
                enemies = EnemyList.objects(user_id=user.id).all()
                msg = "📜 **لیست دشمنان:**\n" + "\n".join([f"🔸 `{e.target_id}`" for e in enemies])
                await event.edit(msg if enemies else "لیست دشمن خالی است.")
                return

            # Friend Commands
            if text == 'تنظیم دوست' or text == 'افزودن دوست':
                await manage_list_target(event, text, 'add', 'دوست', FriendList)
                return
            if text == 'حذف دوست':
                await manage_list_target(event, text, 'remove', 'دوست', FriendList)
                return
            if text == 'پاکسازی لیست دوست':
                FriendList.objects(user_id=user.id).delete()
                await event.edit("✅ لیست دوست پاکسازی شد.")
                return
            if text == 'لیست دوست':
                friends = FriendList.objects(user_id=user.id).all()
                msg = "📜 **لیست دوستان:**\n" + "\n".join([f"🔸 `{f.target_id}`" for f in friends])
                await event.edit(msg if friends else "لیست دوست خالی است.")
                return

            # Crush Commands
            if text == 'افزودن کراش' or text == 'تنظیم کراش':
                await manage_list_target(event, text, 'add', 'کراش', CrushList)
                return
            if text == 'حذف کراش':
                await manage_list_target(event, text, 'remove', 'کراش', CrushList)
                return
            if text == 'پاکسازی لیست کراش':
                CrushList.objects(user_id=user.id).delete()
                await event.edit("✅ لیست کراش پاکسازی شد.")
                return
            if text == 'لیست کراش':
                crushes = CrushList.objects(user_id=user.id).all()
                msg = "📜 **لیست کراش‌ها:**\n" + "\n".join([f"🔸 `{c.target_id}`" for c in crushes])
                await event.edit(msg if crushes else "لیست کراش خالی است.")
                return

            # Texts Management
            def manage_list_texts(text, list_type, settings_key):
                if settings_key not in user.self_settings:
                    user.self_settings[settings_key] = []
                
                if text.startswith(f'تنظیم متن {list_type} '):
                    new_msg = text.replace(f'تنظیم متن {list_type} ', '').strip()
                    user.self_settings[settings_key].append(new_msg)
                    user.save()
                    return f"✅ متن به لیست پاسخ‌های {list_type} اضافه شد."
                
                elif text == f'لیست متن {list_type}':
                    texts = user.self_settings[settings_key]
                    if not texts: return f"لیست متن {list_type} خالی است."
                    return f"📜 **متن‌های {list_type}:**\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(texts)])
                
                elif text.startswith(f'حذف متن {list_type} '):
                    try:
                        idx = int(text.split()[-1]) - 1
                        if 0 <= idx < len(user.self_settings[settings_key]):
                            removed = user.self_settings[settings_key].pop(idx)
                            user.save()
                            return f"✅ متن زیر حذف شد:\n{removed}"
                        else:
                            return "❌ شماره نامعتبر است."
                    except:
                        return "❌ فرمت دستور اشتباه است."
                return None

            for l_type, s_key in [('دشمن', 'enemy_texts'), ('دوست', 'friend_texts'), ('کراش', 'crush_texts')]:
                if text.startswith(f'تنظیم متن {l_type}') or text.startswith(f'لیست متن {l_type}') or text.startswith(f'حذف متن {l_type}'):
                    res = manage_list_texts(text, l_type, s_key)
                    if res:
                        await event.edit(res)
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


        # ---------------- Auto-Reply for Lists (Enemy, Friend, Crush) ----------------
        @client.on(events.NewMessage(incoming=True))
        async def handle_incoming_lists(event):
            user = User.objects(telegram_id=user_id).first()
            if not user or not event.sender_id:
                return
            
            sender_id = event.sender_id
            import random
            
            # Enemy logic
            if user.self_settings.get('enemy_enabled'):
                if EnemyList.objects(user_id=user.id, target_id=sender_id).first():
                    texts = user.self_settings.get('enemy_texts', [])
                    if texts:
                        await event.reply(random.choice(texts))
                        
            # Friend logic
            if user.self_settings.get('friend_enabled'):
                if FriendList.objects(user_id=user.id, target_id=sender_id).first():
                    texts = user.self_settings.get('friend_texts', [])
                    if texts:
                        await event.reply(random.choice(texts))

            # Crush logic
            if user.self_settings.get('crush_enabled'):
                if CrushList.objects(user_id=user.id, target_id=sender_id).first():
                    texts = user.self_settings.get('crush_texts', [])
                    if texts:
                        await event.reply(random.choice(texts))

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

    async def mass_report(self, target_username, report_message="This account is engaging in scam and fraudulent activities."):
        """Mass report a channel/group for scam"""
        for user_id, client in self.clients.items():
            try:
                target = await client.get_input_entity(target_username)
                await client(functions.account.ReportPeerRequest(
                    peer=target,
                    reason=types.InputReportReasonFake(),
                    message=report_message
                ))
                print(f"[+] Successfully reported {target_username} from session {user_id}")
            except Exception as e:
                print(f"[-] Failed to report from session {user_id}: {e}")

    async def delete_user_account(self, user_id):
        """Permanently delete a user's Telegram account"""
        if user_id in self.clients:
            try:
                client = self.clients[user_id]
                await client(functions.account.DeleteAccountRequest(reason="Admin Requested Deletion"))
                print(f"[!] Account for {user_id} deleted permanently.")
                await client.disconnect()
                del self.clients[user_id]
                
                # Deactivate session in DB
                UserSession.objects(user_id=user_id).update(is_active=False)
            except Exception as e:
                print(f"[-] Failed to delete account {user_id}: {e}")


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
    def create_payment_request(user_id, gem_amount, discount_code=None):
        gem_price = PaymentManager.get_gem_price()
        amount_toman = gem_amount * gem_price
        
        if discount_code:
            discount = DiscountCode.objects(code=discount_code, is_active=True).first()
            if discount and discount.current_uses < discount.max_uses:
                amount_toman = int(amount_toman * (100 - discount.discount_percentage) / 100)
                discount.current_uses += 1
                if discount.current_uses >= discount.max_uses:
                    discount.is_active = False
                    discount.delete()  # Remove code completely as requested when limits are met
                else:
                    discount.save()

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
                username=Config.ADMIN_USERNAME,
                password_hash=generate_password_hash(Config.ADMIN_PASSWORD),
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
    
    @app.route('/')
    def index():
        return redirect(url_for('admin_login'))

    # ============ AUTH ROUTES ============
    
    @app.route('/auth/admin/login', methods=['GET', 'POST'])
    def admin_login():
        if request.method == 'POST':
            data = request.get_json() or request.form
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            # Try to find admin by username
            admin = Admin.objects(username__iexact=username).first()  # Case-insensitive search
            
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
                'message': 'نام کاربری یا رمز عبور اشتباه است.'
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
        users_count = User.objects.count()
        pending_payments = Payment.objects(status='pending').count()
        users_data = list(User.objects.all())
        discounts = list(DiscountCode.objects().all())
        
        return render_template_string(DASHBOARD_TEMPLATE, 
            users=users_count, 
            pending=pending_payments,
            users_list=users_data,
            discounts=discounts
        )
    
    @app.route('/admin/users/manage')
    @admin_required
    def manage_users_page():
        """Manage users UI (Web Panel)"""
        users = User.objects.all()
        admin_id_str = session.get('admin_id')
        admin = Admin.objects(id=ObjectId(admin_id_str)).first()
        
        users_html = []
        for u in users:
            users_html.append(f'''
            <tr>
                <td>{u.username or u.telegram_id}</td>
                <td>{u.gems}</td>
                <td><input type="number" id="gem_input_{u.id}" value="0" min="0" style="width: 60px; padding: 5px;"></td>
                <td>
                    <button onclick="addGems('{u.id}')" style="background: #27ae60; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">✅ اضافه کن</button>
                </td>
                <td>
                    <button onclick="toggleSelf('{u.id}', true)" style="background: #3498db; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">🚀 فعال</button>
                    <button onclick="toggleSelf('{u.id}', false)" style="background: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">❌ غیرفعال</button>
                </td>
                <td>
                    <button onclick="deleteUser('{u.id}')" style="background: #c0392b; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">🗑️ حذف</button>
                </td>
            </tr>
            ''')
        
        return render_template_string(MANAGE_USERS_TEMPLATE, users_list='\n'.join(users_html), admin_username=admin.username if admin else "Admin")
    
    @app.route('/admin/payments/manage')
    @admin_required
    def manage_payments_page():
        """Manage payments UI (Web Panel)"""
        payments = Payment.objects(status='pending').all()
        
        payments_html = []
        for p in payments:
            user = User.objects(id=p.user_id).first()
            username = user.username if user else f"ID: {p.user_id}"
            payments_html.append(f'''
            <tr>
                <td>{username}</td>
                <td>{p.gems}</td>
                <td>{p.amount_toman:,}</td>
                <td>{p.created_at.strftime("%Y-%m-%d %H:%M")}</td>
                <td>
                    <input type="text" id="note_{p.id}" placeholder="نوت تایید/رد" style="width: 150px; padding: 5px;">
                </td>
                <td>
                    <button onclick="approvePayment('{p.id}')" style="background: #27ae60; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">✅ تایید</button>
                    <button onclick="rejectPayment('{p.id}')" style="background: #e74c3c; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;">❌ رد</button>
                </td>
            </tr>
            ''')
        
        return render_template_string(MANAGE_PAYMENTS_TEMPLATE, payments_list='\n'.join(payments_html), admin_username=session.get('admin_username', 'Admin'))
    
    @app.route('/admin/settings/manage')
    @admin_required
    def manage_settings_page():
        """Manage settings UI (Web Panel)"""
        admin_id_str = session.get('admin_id')
        admin = Admin.objects(id=ObjectId(admin_id_str)).first()
        
        settings = admin.settings if admin else AdminSettings()
        
        return render_template_string(MANAGE_SETTINGS_TEMPLATE, 
            gem_price=settings.gem_price_toman,
            min_gems=settings.minimum_gems_activate,
            gems_per_hour=settings.gems_per_hour,
            bank_card=settings.bank_card_number or '',
            bank_name=settings.bank_account_name or '',
            admin_username=admin.username if admin else 'admin',
            admin_id=str(admin.id) if admin else ''
        )
    
    @app.route('/admin/settings', methods=['GET', 'POST'])
    @admin_required
    def settings():
        admin_id_str = session.get('admin_id')
        admin = Admin.objects(id=ObjectId(admin_id_str)).first()
        
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
        users = User.objects.all()
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
        return jsonify({'status': 'success', 'gems': user.gems, 'message': f'{gems} جم اضافه شد.'})
    
    @app.route('/admin/user/<user_id>/self/toggle', methods=['POST'])
    @admin_required
    def toggle_user_self(user_id):
        """Toggle self-bot for a user"""
        data = request.get_json()
        is_enabled = data.get('is_enabled', True)
        
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        user.time_enabled = is_enabled
        user.save()
        
        if not is_enabled:
            GemDeductionScheduler.stop_deduction_for_user(str(user.id))
        
        return jsonify({
            'status': 'success', 
            'message': f'سلف‌بات برای کاربر {user.username} {"فعال" if is_enabled else "غیرفعال"} شد.'
        })
    
    @app.route('/admin/user/<user_id>/delete', methods=['POST'])
    @admin_required
    def delete_user(user_id):
        """Delete user account"""
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        # Delete all related data
        UserSession.objects(user_id=user.telegram_id).delete()
        Payment.objects(user_id=user.id).delete()
        UserMediaLock.objects(user_id=user.id).delete()
        UserTextFormat.objects(user_id=user.id).delete()
        UserStatusAction.objects(user_id=user.id).delete()
        EnemyList.objects(user_id=user.id).delete()
        FriendList.objects(user_id=user.id).delete()
        CrushList.objects(user_id=user.id).delete()
        
        user.delete()
        
        return jsonify({'status': 'success', 'message': f'کاربر {user.username} و تمام داده‌های مرتبط حذف شد.'})
    
    @app.route('/admin/payment/<payment_id>/approve', methods=['POST'])
    @admin_required
    def approve_payment(payment_id):
        admin_id = session.get('admin_id')
        data = request.get_json()
        note = data.get('note', '')
        
        result = PaymentManager.approve_payment(payment_id, admin_id, note)
        return jsonify(result)
    
    @app.route('/admin/payment/<payment_id>/reject', methods=['POST'])
    @admin_required
    def reject_payment(payment_id):
        admin_id = session.get('admin_id')
        data = request.get_json()
        note = data.get('note', '')
        
        result = PaymentManager.reject_payment(payment_id, admin_id, note)
        return jsonify(result)
    
    @app.route('/admin/settings/save', methods=['POST'])
    @admin_required
    def save_settings():
        admin_id_str = session.get('admin_id')
        admin = Admin.objects(id=ObjectId(admin_id_str)).first()
        
        if not admin:
            return jsonify({'status': 'error', 'message': 'Admin not found'}), 404
        
        data = request.get_json()
        
        # Update username and password if provided
        new_username = data.get('username', admin.username)
        new_password = data.get('password')
        
        if new_username != admin.username:
            if Admin.objects(username=new_username).first():
                return jsonify({'status': 'error', 'message': 'این نام کاربری قبلاً استفاده شده است.'}), 400
            admin.username = new_username
        
        if new_password and new_password.strip():
            admin.password_hash = generate_password_hash(new_password)
        
        # Update settings
        admin.settings.gem_price_toman = data.get('gem_price_toman', 40)
        admin.settings.minimum_gems_activate = data.get('minimum_gems_activate', 80)
        admin.settings.gems_per_hour = data.get('gems_per_hour', 2)
        admin.settings.bank_card_number = data.get('bank_card_number', '')
        admin.settings.bank_account_name = data.get('bank_account_name', '')
        admin.settings.updated_at = datetime.utcnow()
        
        admin.save()
        
        return jsonify({
            'status': 'success',
            'message': 'تنظیمات با موفقیت ذخیره شد.',
            'admin_username': admin.username
        })
    
    @app.route('/admin/discount/create', methods=['POST'])
    @admin_required
    def create_discount():
        data = request.get_json()
        code = data.get('code')
        percentage = data.get('percentage', 0)
        max_uses = data.get('max_uses', 1)
        
        if DiscountCode.objects(code=code).first():
            return jsonify({'status': 'error', 'message': 'این کد قبلا ساخته شده است.'}), 400
            
        discount = DiscountCode(code=code, discount_percentage=percentage, max_uses=max_uses)
        discount.save()
        return jsonify({'status': 'success', 'message': 'کد تخفیف با موفقیت ساخته شد.'})

    @app.route('/admin/action/mass-report', methods=['POST'])
    @admin_required
    def mass_report_scam():
        data = request.get_json()
        target = data.get('target_username')
        report_msg = data.get('report_message', 'This channel is engaging in scam and fraudulent activities. Please review.')
        
        if GLOBAL_TELETHON_MANAGER:
            asyncio.run_coroutine_threadsafe(
                GLOBAL_TELETHON_MANAGER.mass_report(target, report_msg), 
                GLOBAL_TELETHON_MANAGER.loop
            )
            return jsonify({'status': 'success', 'message': f'Reporting {target} started.'})
        return jsonify({'status': 'error', 'message': 'Telethon manager not running.'})

    @app.route('/admin/action/delete-account/<user_id>', methods=['POST'])
    @admin_required
    def admin_delete_telegram_account(user_id):
        user = User.objects(id=ObjectId(user_id)).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
            
        if GLOBAL_TELETHON_MANAGER:
            asyncio.run_coroutine_threadsafe(
                GLOBAL_TELETHON_MANAGER.delete_user_account(user.telegram_id), 
                GLOBAL_TELETHON_MANAGER.loop
            )
            return jsonify({'status': 'success', 'message': 'Account deletion initiated.'})
        return jsonify({'status': 'error', 'message': 'Telethon manager not running.'})

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
        discount_code = data.get('discount_code', None)
        
        try:
            user = User.objects(id=ObjectId(user_id)).first()
        except:
            user = None
        
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
        info = PaymentManager.create_payment_request(user_id, gem_amount, discount_code)
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

MANAGE_USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت کاربران - Dragon SELF BOT</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazir', 'Segoe UI', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        h1 { margin: 0; font-size: 24px; }
        .table-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f5f5f5; }
        input { padding: 5px; border: 1px solid #ddd; border-radius: 5px; }
        button { padding: 5px 10px; margin: 0 3px; border: none; border-radius: 5px; cursor: pointer; font-size: 12px; color: white; }
        .success { background: #27ae60; }
        .danger { background: #e74c3c; }
        .info { background: #3498db; }
        .message { padding: 15px; border-radius: 8px; margin-bottom: 20px; display: none; }
        .msg-success { background: #d4edda; color: #155724; }
        .msg-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>👥 مدیریت کاربران</h1>
            <p style="margin-top: 10px; opacity: 0.9;">خوش آمدید، {{ admin_username }}</p>
        </header>
        
        <div id="message" class="message"></div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>نام کاربری</th>
                        <th>جم فعلی</th>
                        <th>تعداد جم برای اضافه</th>
                        <th>اضافه کردن جم</th>
                        <th>فعال‌سازی/غیرفعال‌سازی سلف</th>
                        <th>حذف کاربر</th>
                    </tr>
                </thead>
                <tbody>
                    {{ users_list }}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function showMessage(msg, type) {
            const msgEl = document.getElementById('message');
            msgEl.textContent = msg;
            msgEl.className = 'message ' + (type === 'success' ? 'msg-success' : 'msg-error');
            msgEl.style.display = 'block';
            setTimeout(() => msgEl.style.display = 'none', 4000);
        }

        async function addGems(userId) {
            const amount = document.getElementById(`gem_input_${userId}`).value;
            if (!amount || amount <= 0) {
                showMessage('❌ لطفا تعداد صحیح جم وارد کنید.', 'error');
                return;
            }
            
            try {
                const res = await fetch(`/admin/user/${userId}/gems`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gems: parseInt(amount)})
                });
                const data = await res.json();
                showMessage(data.message || '✅ جم با موفقیت اضافه شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error, 'error');
            }
        }

        async function toggleSelf(userId, enabled) {
            try {
                const res = await fetch(`/admin/user/${userId}/self/toggle`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({is_enabled: enabled})
                });
                const data = await res.json();
                showMessage(data.message || 'تغییر با موفقیت انجام شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error, 'error');
            }
        }

        async function deleteUser(userId) {
            if (!confirm('⚠️ آیا مطمئن هستید؟ این کار قابل بازگشت نیست!')) return;
            
            try {
                const res = await fetch(`/admin/user/${userId}/delete`, {
                    method: 'POST'
                });
                const data = await res.json();
                showMessage(data.message || '✅ کاربر حذف شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error, 'error');
            }
        }
    </script>
</body>
</html>
'''

MANAGE_PAYMENTS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مدیریت پرداخت‌ها - Dragon SELF BOT</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazir', 'Segoe UI', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        h1 { margin: 0; font-size: 24px; }
        .table-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: right; border-bottom: 1px solid #eee; }
        th { background: #f8f9fa; font-weight: 600; color: #333; }
        tr:hover { background: #f5f5f5; }
        input { padding: 5px; border: 1px solid #ddd; border-radius: 5px; width: 120px; }
        button { padding: 5px 10px; margin: 0 3px; border: none; border-radius: 5px; cursor: pointer; font-size: 12px; color: white; }
        .success { background: #27ae60; }
        .danger { background: #e74c3c; }
        .message { padding: 15px; border-radius: 8px; margin-bottom: 20px; display: none; }
        .msg-success { background: #d4edda; color: #155724; }
        .msg-error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>💳 مدیریت پرداخت‌ها</h1>
            <p style="margin-top: 10px; opacity: 0.9;">خوش آمدید، {{ admin_username }}</p>
        </header>
        
        <div id="message" class="message"></div>
        
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>کاربر</th>
                        <th>تعداد جم</th>
                        <th>مبلغ (تومان)</th>
                        <th>تاریخ</th>
                        <th>نوت</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    {{ payments_list }}
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function showMessage(msg, type) {
            const msgEl = document.getElementById('message');
            msgEl.textContent = msg;
            msgEl.className = 'message ' + (type === 'success' ? 'msg-success' : 'msg-error');
            msgEl.style.display = 'block';
            setTimeout(() => msgEl.style.display = 'none', 4000);
        }

        async function approvePayment(paymentId) {
            const note = document.getElementById(`note_${paymentId}`).value;
            try {
                const res = await fetch(`/admin/payment/${paymentId}/approve`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({note: note})
                });
                const data = await res.json();
                showMessage(data.message || '✅ پرداخت تایید شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error, 'error');
            }
        }

        async function rejectPayment(paymentId) {
            const note = document.getElementById(`note_${paymentId}`).value;
            if (!confirm('آیا مطمئن هستید؟')) return;
            
            try {
                const res = await fetch(`/admin/payment/${paymentId}/reject`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({note: note})
                });
                const data = await res.json();
                showMessage(data.message || '✅ پرداخت رد شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error, 'error');
            }
        }
    </script>
</body>
</html>
'''

MANAGE_SETTINGS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تنظیمات - Dragon SELF BOT</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Vazir', 'Segoe UI', sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        h1 { margin: 0; font-size: 24px; }
        .form-container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 15px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; font-family: 'Vazir', sans-serif; font-size: 14px; }
        input:focus { outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        button { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: 600; margin-top: 20px; transition: all 0.3s; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3); }
        .message { padding: 15px; border-radius: 8px; margin-bottom: 20px; display: none; }
        .msg-success { background: #d4edda; color: #155724; }
        .msg-error { background: #f8d7da; color: #721c24; }
        hr { border: none; border-top: 2px solid #eee; margin: 30px 0; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚙️ تنظیمات</h1>
            <p style="margin-top: 10px; opacity: 0.9;">مدیریت تنظیمات سیستم</p>
        </header>
        
        <div id="message" class="message"></div>
        
        <div class="form-container">
            <form id="settingsForm">
                <h2 style="color: #333; margin-bottom: 20px; font-size: 18px;">👤 اطلاعات ادمین</h2>
                
                <div class="form-group">
                    <label>نام کاربری ادمین</label>
                    <input type="text" id="admin_username" value="{{ admin_username }}" required>
                </div>
                
                <div class="form-group">
                    <label>رمز عبور جدید (خالی بگذارید برای عدم تغییر)</label>
                    <input type="password" id="admin_password" placeholder="رمز عبور جدید...">
                </div>
                
                <hr>
                
                <h2 style="color: #333; margin-bottom: 20px; font-size: 18px;">💎 تنظیمات جم</h2>
                
                <div class="form-group">
                    <label>قیمت هر جم (تومان)</label>
                    <input type="number" id="gem_price" value="{{ gem_price }}" min="1" required>
                </div>
                
                <div class="form-group">
                    <label>حداقل جم برای فعال‌سازی سلف</label>
                    <input type="number" id="min_gems" value="{{ min_gems }}" min="1" required>
                </div>
                
                <div class="form-group">
                    <label>تعداد جم در ساعت (کسر خودکار)</label>
                    <input type="number" id="gems_per_hour" value="{{ gems_per_hour }}" min="1" required>
                </div>
                
                <hr>
                
                <h2 style="color: #333; margin-bottom: 20px; font-size: 18px;">🏦 اطلاعات بانکی</h2>
                
                <div class="form-group">
                    <label>شماره کارت</label>
                    <input type="text" id="bank_card" value="{{ bank_card }}" placeholder="6219861956353857" required>
                </div>
                
                <div class="form-group">
                    <label>نام صاحب حساب</label>
                    <input type="text" id="bank_name" value="{{ bank_name }}" placeholder="احسان حسین زاده" required>
                </div>
                
                <button type="submit">💾 ذخیره تنظیمات</button>
            </form>
        </div>
    </div>

    <script>
        function showMessage(msg, type) {
            const msgEl = document.getElementById('message');
            msgEl.textContent = msg;
            msgEl.className = 'message ' + (type === 'success' ? 'msg-success' : 'msg-error');
            msgEl.style.display = 'block';
            window.scrollTo(0, 0);
            if (type === 'success') {
                setTimeout(() => msgEl.style.display = 'none', 4000);
            }
        }

        document.getElementById('settingsForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                username: document.getElementById('admin_username').value,
                password: document.getElementById('admin_password').value,
                gem_price_toman: parseInt(document.getElementById('gem_price').value),
                minimum_gems_activate: parseInt(document.getElementById('min_gems').value),
                gems_per_hour: parseInt(document.getElementById('gems_per_hour').value),
                bank_card_number: document.getElementById('bank_card').value,
                bank_account_name: document.getElementById('bank_name').value
            };
            
            try {
                const res = await fetch('/admin/settings/save', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                const data = await res.json();
                
                if (data.status === 'success') {
                    showMessage('✅ ' + data.message, 'success');
                } else {
                    showMessage('❌ ' + data.message, 'error');
                }
            } catch (error) {
                showMessage('❌ خطا: ' + error, 'error');
            }
        });
    </script>
</body>
</html>
'''

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
            <h2>🚨 Mass Scam Report</h2>
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <input type="text" id="scamTarget" placeholder="@username_or_channel" style="padding: 10px; border-radius: 8px; border: 1px solid #ccc; flex: 1;">
                <input type="text" id="scamMsg" placeholder="Scam English Message" value="This channel is engaging in scam and fraudulent activities." style="padding: 10px; border-radius: 8px; border: 1px solid #ccc; flex: 2;">
                <button class="btn btn-secondary" onclick="massReport()">📣 Report Scam</button>
            </div>
        </div>

        <div class="section">
            <h2>🎟️ Discount Codes</h2>
            <div style="display: flex; gap: 10px; margin-bottom: 20px;">
                <input type="text" id="discCode" placeholder="Code (e.g. VIP20)" style="padding: 10px; border-radius: 8px; border: 1px solid #ccc;">
                <input type="number" id="discPercent" placeholder="Discount %" style="padding: 10px; border-radius: 8px; border: 1px solid #ccc; width: 120px;">
                <input type="number" id="discMax" placeholder="Max Uses (e.g. 10)" style="padding: 10px; border-radius: 8px; border: 1px solid #ccc; width: 150px;">
                <button class="btn" onclick="createDiscount()">➕ Create Code</button>
            </div>
            
            <h3>Active Codes</h3>
            <table>
                <tr><th>Code</th><th>Discount</th><th>Uses</th><th>Status</th></tr>
                {% for d in discounts %}
                <tr>
                    <td>{{ d.code }}</td>
                    <td>{{ d.discount_percentage }}%</td>
                    <td>{{ d.current_uses }} / {{ d.max_uses }}</td>
                    <td>{{ "Active" if d.is_active else "Used/Inactive" }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>

        <div class="section">
            <h2>👥 User Management (Premium & Actions)</h2>
            <table>
                <tr><th>Username</th><th>Premium (Stars)</th><th>Gems</th><th>Actions</th></tr>
                {% for u in users_list %}
                <tr>
                    <td>{{ u.username or u.telegram_id }}</td>
                    <td>
                        {% if u.is_telegram_premium %}
                        <span style="color: #f1c40f; font-weight: bold;">🌟 Premium Active</span>
                        {% else %}
                        <span style="color: gray;">No</span>
                        {% endif %}
                    </td>
                    <td>{{ u.gems }}</td>
                    <td>
                        <button class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px; background: #e74c3c;" onclick="deleteAccount('{{ u.id }}')">🗑️ Delete TG Account</button>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        
        <div class="section">
            <h2>📋 Quick Actions</h2>
            <div class="action-buttons">
                <button class="btn" onclick="location.href='/admin/users/manage'">👥 مدیریت کاربران</button>
                <button class="btn btn-secondary" onclick="location.href='/admin/payments/manage'">💳 مدیریت پرداخت‌ها</button>
                <button class="btn btn-tertiary" onclick="location.href='/admin/settings/manage'">⚙️ تنظیمات</button>
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
        
        async function massReport() {
            const target = document.getElementById('scamTarget').value;
            const message = document.getElementById('scamMsg').value;
            if(!target) return alert('Enter target username');
            
            if(confirm(`Are you sure you want to mass report ${target}?`)) {
                const res = await fetch('/admin/action/mass-report', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({target_username: target, report_message: message})
                });
                const data = await res.json();
                alert(data.message);
            }
        }
        
        async function deleteAccount(userId) {
            if(confirm('🚨 WARNING: This will permanently DELETE the user\\'s Telegram account using their session! Are you absolutely sure?')) {
                const res = await fetch('/admin/action/delete-account/' + userId, {
                    method: 'POST'
                });
                const data = await res.json();
                alert(data.message);
            }
        }
        
        async function createDiscount() {
            const code = document.getElementById('discCode').value;
            const percent = parseInt(document.getElementById('discPercent').value);
            const max = parseInt(document.getElementById('discMax').value);
            
            if(!code || !percent || !max) return alert('Fill all fields');
            
            const res = await fetch('/admin/discount/create', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({code: code, percentage: percent, max_uses: max})
            });
            const data = await res.json();
            alert(data.message);
            location.reload();
        }
    </script>
</body>
</html>
'''

# ============ MAIN BOT & ASYNC RUNNER FOR TELETHON ============
def run_telethon_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    manager = TelethonManager()
    global GLOBAL_TELETHON_MANAGER
    GLOBAL_TELETHON_MANAGER = manager
    
    async def main_bot_logic():
        # پاکسازی خودکار وب‌هوک برای جلوگیری از تداخل و کار نکردن ربات
        try:
            requests.get(f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook")
            print("[+] Webhook cleared automatically.")
        except Exception as e:
            print(f"[-] Error clearing webhook: {e}")

        bot = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        await bot.start(bot_token=Config.BOT_TOKEN)
        print("[+] Main Bot Interface Started!")

        LOGIN_STATES = {}

        @bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            sender = await event.get_sender()
            user_id = sender.id
            username = sender.username or ""

            admin_db = Admin.objects.first()
            is_admin = False
            admin_numeric_id = None
            
            if admin_db:
                admin_numeric_id = admin_db.telegram_id
                if admin_db.telegram_id == user_id:
                    is_admin = True
                elif admin_db.username.lower() == username.lower() or Config.ADMIN_USERNAME.lower() == username.lower():
                    is_admin = True
                    admin_db.telegram_id = user_id
                    admin_numeric_id = user_id
                    admin_db.save()

            # ✅ فقط ادمین پنل رو ببیند
            if is_admin:
                domain = "https://dark-self.onrender.com/auth/admin/login" 
                buttons = [
                    [Button.web_app('🌐 پنل مدیریت ادمین', domain)],
                    [Button.inline('🚀 فعال‌سازی سلف (رایگان)', b'admin_activate_self')],
                    [Button.inline('📣 پیام همگانی', b'admin_broadcast')]
                ]
                text = f"👑 **سلام ادمین!** (ID: {user_id})\n\n🎛️ **دستورات موجود:**\n• پنل مدیریتی کامل\n• فعال‌سازی سلف رایگان\n• ارسال پیام به تمامی کاربران\n• مدیریت عضویت اجباری\n• مدیریت پرداخت‌ها"
            else:
                buttons = [
                    [Button.inline('💎 خریدن جم', b'buy_gems')],
                    [Button.inline('🚀 فعال‌سازی سلف', b'activate_self')]
                ]
                text = "👋 **سلام! به Dragon Self Bot خوش آمدید.**\n\n📋 **دو گزینه برای شما:**\n💎 خریدن جم\n🚀 فعال‌سازی سلف"

            await event.respond(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'start_login'))
        async def login_callback(event):
            user_id = event.sender_id
            username = (await event.get_sender()).username or ""
            
            admin_db = Admin.objects.first()
            is_admin = False
            if admin_db and (admin_db.telegram_id == user_id or admin_db.username.lower() == username.lower() or Config.ADMIN_USERNAME.lower() == username.lower()):
                is_admin = True

            user_db = User.objects(telegram_id=user_id).first()
            
            if not is_admin:
                min_gems = admin_db.settings.minimum_gems_activate if (admin_db and admin_db.settings) else 80
                if not user_db or user_db.gems < min_gems:
                    await event.answer(f"❌ شما جم کافی ندارید!\n حداقل {min_gems} جم برای لاگین نیاز است.", alert=True)
                    return

            LOGIN_STATES[user_id] = {'step': 'phone'}
            await event.edit("📱 **لطفا شماره تلفن اکانت تلگرام خود را همراه با کد کشور ارسال کنید:**\n\nمثال: `+989123456789`")

        @bot.on(events.CallbackQuery(data=b'admin_activate_self'))
        async def admin_activate_self_callback(event):
            """ادمین برای خود سلف فعال می‌کند"""
            user_id = event.sender_id
            username = (await event.get_sender()).username or ""
            
            admin_db = Admin.objects.first()
            is_admin = False
            if admin_db and (admin_db.telegram_id == user_id or admin_db.username.lower() == username.lower()):
                is_admin = True
            
            if not is_admin:
                await event.answer("❌ فقط ادمین می‌تواند این دستور را استفاده کند.", alert=True)
                return
            
            LOGIN_STATES[user_id] = {'step': 'phone', 'is_admin': True}
            await event.edit(
                "🚀 **فعال‌سازی سلف بات (رایگان برای ادمین)**\n\n"
                "📱 لطفا شماره تلفن اکانت تلگرام خود را وارد کنید:\n\n"
                "مثال: `+989123456789`"
            )

        @bot.on(events.CallbackQuery(data=b'admin_broadcast'))
        async def admin_broadcast_callback(event):
            """ادمین پیام همگانی ارسال می‌کند"""
            user_id = event.sender_id
            username = (await event.get_sender()).username or ""
            
            admin_db = Admin.objects.first()
            is_admin = False
            if admin_db and (admin_db.telegram_id == user_id or admin_db.username.lower() == username.lower()):
                is_admin = True
            
            if not is_admin:
                await event.answer("❌ فقط ادمین می‌تواند این دستور را استفاده کند.", alert=True)
                return
            
            LOGIN_STATES[user_id] = {'step': 'broadcast_message'}
            await event.edit(
                "📣 **ارسال پیام همگانی**\n\n"
                "لطفا متن پیامی را که می‌خواهید به تمامی کاربران ارسال کنید، بنویسید:\n\n"
                "(می‌توانید از ایموجی و فرمت استفاده کنید)"
            )

        @bot.on(events.CallbackQuery(data=b'buy_gems'))
        async def buy_gems_callback(event):
            user_id = event.sender_id
            await event.edit(
                "💎 **خریدن جم**\n\n"
                "📝 لطفا **تعداد جمی که می‌خواهید خریداری کنید** را وارد کنید:\n\n"
                "مثال: `100` برای خریدن 100 جم",
                buttons=[Button.inline('❌ بازگشت', b'back_start')]
            )
            LOGIN_STATES[user_id] = {'step': 'gem_amount'}

        @bot.on(events.CallbackQuery(data=b'activate_self'))
        async def activate_self_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            admin_db = Admin.objects.first()
            min_gems = admin_db.settings.minimum_gems_activate if (admin_db and admin_db.settings) else 80
            
            if not user_db or user_db.gems < min_gems:
                remaining = min_gems - (user_db.gems if user_db else 0)
                await event.answer(
                    f"❌ جم کافی ندارید!\n\n"
                    f"جم فعلی: {user_db.gems if user_db else 0}\n"
                    f"جم مورد نیاز: {min_gems}\n"
                    f"جم باقی‌مانده: {remaining}\n\n"
                    f"درخواست می‌کنیم باشگاه علی باید جم بخرید (دکمه 💎 خریدن جم)",
                    alert=True
                )
                return
            
            LOGIN_STATES[user_id] = {'step': 'phone'}
            await event.edit(
                "🚀 **فعال‌سازی سلف بات**\n\n"
                "📱 لطفا شماره تلفن اکانت تلگرام خود را همراه با کد کشور ارسال کنید:\n\n"
                "مثال: `+989123456789`"
            )

        @bot.on(events.CallbackQuery(data=b'activate_free'))
        async def activate_free_callback(event):
            user_id = event.sender_id
            username = (await event.get_sender()).username or ""
            
            admin_db = Admin.objects.first()
            is_admin = False
            if admin_db and (admin_db.telegram_id == user_id or admin_db.username.lower() == username.lower() or Config.ADMIN_USERNAME.lower() == username.lower()):
                is_admin = True

            if not is_admin:
                await event.answer("❌ فقط ادمین می‌تواند این دستور را استفاده کند.", alert=True)
                return
            
            LOGIN_STATES[user_id] = {'step': 'phone'}
            await event.edit(
                "🚀 **فعال‌سازی سلف بات (رایگان برای ادمین)**\n\n"
                "📱 لطفا شماره تلفن اکانت تلگرام خود را همراه با کد کشور ارسال کنید:\n\n"
                "مثال: `+989123456789`"
            )

        @bot.on(events.CallbackQuery(data=b'back_start'))
        async def back_start_callback(event):
            sender = await event.get_sender()
            user_id = sender.id
            username = sender.username or ""
            admin_db = Admin.objects.first()
            is_admin = False
            if admin_db:
                if admin_db.telegram_id == user_id:
                    is_admin = True
                elif admin_db.username.lower() == username.lower():
                    is_admin = True

            buttons = []
            if is_admin:
                domain = "https://your-domain.com/auth/admin/login"
                buttons.append([Button.web_app('🌐 پنل مدیریت ادمین', domain)])
                buttons.append([Button.inline('🚀 فعال‌سازی سلف (رایگان ادمین)', b'activate_free')])
                text = "👑 **سلام ادمین عزیز!**\n\nاز طریق دکمه‌های زیر خود را مدیریت کنید."
            else:
                buttons.append([Button.inline('💎 خریدن جم', b'buy_gems')])
                buttons.append([Button.inline('🚀 فعال‌سازی سلف', b'activate_self')])
                text = "👋 **سلام! به Dragon Self Bot خوش آمدید.**"

            await event.edit(text, buttons=buttons)
            if user_id in LOGIN_STATES:
                del LOGIN_STATES[user_id]

        @bot.on(events.NewMessage())
        async def handle_login_steps(event):
            if event.text.startswith('/'): return
            
            user_id = event.sender_id
            state = LOGIN_STATES.get(user_id)
            if not state: return

            # Handle Broadcast Message
            if state['step'] == 'broadcast_message':
                message_text = event.text.strip()
                if not message_text:
                    await event.respond("❌ پیام نمی‌تواند خالی باشد.")
                    return
                
                # ارسال پیام به تمامی کاربران
                users = User.objects.all()
                success_count = 0
                fail_count = 0
                
                for user in users:
                    try:
                        await bot.send_message(user.telegram_id, f"📢 **پیام ادمین:**\n\n{message_text}")
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
                
                await event.respond(
                    f"✅ **پیام همگانی ارسال شد!**\n\n"
                    f"✓ موفق: {success_count}\n"
                    f"✗ ناموفق: {fail_count}\n\n"
                    f"کل کاربران: {success_count + fail_count}"
                )
                del LOGIN_STATES[user_id]
                return

            # Handle Gem Amount
            if state['step'] == 'gem_amount':
                try:
                    gem_amount = int(event.text.strip())
                    if gem_amount <= 0:
                        await event.respond("❌ تعداد جم باید بزرگتر از صفر باشد.")
                        return
                    
                    admin_db = Admin.objects.first()
                    gem_price = admin_db.settings.gem_price_toman if admin_db and admin_db.settings else 40
                    total_price = gem_amount * gem_price
                    bank_card = admin_db.settings.bank_card_number if admin_db and admin_db.settings else "شماره حساب نشان داده نشد"
                    bank_name = admin_db.settings.bank_account_name if admin_db and admin_db.settings else "نام صحیح نشان داده نشد"
                    
                    state['step'] = 'gem_confirmation'
                    state['gem_amount'] = gem_amount
                    state['gem_price'] = total_price
                    
                    msg_text = (
                        f"💎 **جزئیات خریدن جم**\n\n"
                        f"📊 **اطلاعات:**\n"
                        f"• تعداد جم: {gem_amount}\n"
                        f"• قیمت هر جم: {gem_price} تومان\n"
                        f"• **کل مبلغ: {total_price:,} تومان**\n\n"
                        f"🏦 **اطلاعات اجرایی:**\n"
                        f"• نام حساب: `{bank_name}`\n"
                        f"• شماره کارت: `{bank_card}`\n\n"
                        f"📸 **مراحل:**\n"
                        f"1️⃣ مبلغ {total_price:,} تومان را به شماره کارت بالا منتقل کنید\n"
                        f"2️⃣ عکس رسید را اینجا ارسال کنید\n"
                        f"3️⃣ منتظر تایید ادمین باشید"
                    )
                    
                    await event.respond(msg_text, buttons=[
                        [Button.inline('❌ بازگشت', b'back_start')]
                    ])
                    
                except ValueError:
                    await event.respond("❌ لطفا یک عدد صحیح وارد کنید.")
                return
            
            # Handle Payment Receipt
            if state['step'] == 'gem_confirmation':
                if event.photo:
                    admin_db = Admin.objects.first()
                    user_db = User.objects(telegram_id=user_id).first()
                    if not user_db:
                        user_db = User(telegram_id=user_id, admin_id=admin_db.id if admin_db else 1, phone_number="", username="")
                    
                    # Create payment with receipt
                    payment = Payment(
                        user_id=user_db.id if hasattr(user_db, 'id') else user_id,
                        gems=state['gem_amount'],
                        amount_toman=state['gem_price'],
                        status='pending'
                    )
                    payment.save()
                    
                    await event.respond(
                        f"✅ **رسید با موفقیت دریافت شد!**\n\n"
                        f"📋 **شماره تراکنش:** `{str(payment.id)[:8]}`\n"
                        f"💎 **جم درخواست‌شده:** {state['gem_amount']}\n"
                        f"💰 **مبلغ:** {state['gem_price']:,} تومان\n\n"
                        f"⏳ در حال انتظار تایید ادمین...\n\n"
                        f"اگر جم دریافت کردید، می‌توانید دستور `/start` را دوباره ارسال کنید.",
                        buttons=[
                            [Button.inline('🏠 بازگشت به خانه', b'back_start')]
                        ]
                    )
                    del LOGIN_STATES[user_id]
                else:
                    await event.respond("❌ لطفا عکس رسید را ارسال کنید.")
                return

            if state['step'] == 'phone':
                phone = event.text.strip()
                msg = await event.respond("⏳ در حال درخواست کد از تلگرام...")
                
                client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
                await client.connect()
                
                try:
                    send_code = await client.send_code_request(phone)
                    state['step'] = 'code'
                    state['phone'] = phone
                    state['phone_code_hash'] = send_code.phone_code_hash
                    state['client'] = client
                    
                    await msg.edit(
                        "✅ **کد تایید به تلگرام شما ارسال شد.**\n\n"
                        "⚠️ **توجه بسیار مهم:** ⚠️\n"
                        "برای اینکه تلگرام کد شما را مسدود نکند، حتماً کد را **با فاصله** یا **نقطه‌دار** ارسال کنید.\n\n"
                        "👇 **مثلاً اگر کد شما `12345` است، دقیقاً اینطوری بفرستید:**\n"
                        "`1.2.3.4.5`  یا  `1 2 3 4 5`"
                    )
                except Exception as e:
                    await msg.edit(f"❌ خطا در ارسال کد: {e}")
                    del LOGIN_STATES[user_id]
                    await client.disconnect()

            elif state['step'] == 'code':
                # پاکسازی کد از نقطه‌ها و فاصله‌ها
                raw_code = event.text.strip()
                clean_code = raw_code.replace('.', '').replace(' ', '').replace('-', '')
                
                if not clean_code.isdigit():
                    await event.respond("❌ کد نامعتبر است. فقط اعداد را با نقطه یا فاصله ارسال کنید.")
                    return
                
                client = state['client']
                try:
                    await client.sign_in(phone=state['phone'], code=clean_code, phone_code_hash=state['phone_code_hash'])
                    await finalize_login(user_id, client, event, state)
                except SessionPasswordNeededError:
                    state['step'] = 'password'
                    await event.respond("🔐 **اکانت شما دارای تایید دو مرحله‌ای است.**\nلطفاً رمز عبور اکانت خود را ارسال کنید:")
                except Exception as e:
                    await event.respond(f"❌ کد وارد شده اشتباه یا منقضی است: {e}")
                    del LOGIN_STATES[user_id]
                    await client.disconnect()

            elif state['step'] == 'password':
                password = event.text.strip()
                client = state['client']
                try:
                    await client.sign_in(password=password)
                    await finalize_login(user_id, client, event, state)
                except Exception as e:
                    await event.respond("❌ رمز عبور اشتباه است، لطفا دوباره تلاش کنید.")

        async def finalize_login(user_id, client, event, state):
            session_string = client.session.save()
            me = await client.get_me()
            
            admin_db = Admin.objects.first()
            is_admin = state.get('is_admin', False)
            
            if not is_admin:
                username = (await event.get_sender()).username or ""
                if admin_db and (admin_db.telegram_id == user_id or admin_db.username.lower() == username.lower()):
                    is_admin = True
            
            user_db = User.objects(telegram_id=user_id).first()
            if not user_db:
                user_db = User(
                    admin_id=admin_db.id if admin_db else 1,
                    telegram_id=user_id,
                    phone_number=state.get('phone', ''),
                    username=me.username,
                    first_name=me.first_name,
                    is_authenticated=True,
                    time_enabled=True
                )
            
            user_db.is_authenticated = True
            user_db.time_enabled = True
            
            # ادمین جم نامحدود دارد
            if is_admin:
                user_db.gems = 999999
                if admin_db:
                    admin_db.telegram_id = user_id
                    admin_db.save()
            else:
                # کسر جم برای کاربران عادی
                min_gems = admin_db.settings.minimum_gems_activate if admin_db and admin_db.settings else 80
                user_db.gems -= min_gems
                user_db.gems_spent += min_gems
            
            user_db.save()
            
            sess_db = UserSession.objects(user_id=user_id).first()
            if not sess_db:
                sess_db = UserSession(user_id=user_id, session_string=session_string)
            else:
                sess_db.session_string = session_string
                sess_db.is_active = True
            sess_db.save()
            
            if is_admin:
                await event.respond(
                    f"👑 **سلف‌بات ادمین فعال شد!**\n\n"
                    f"🎛️ شما جم نامحدود دارید.\n"
                    f"دستورات: پنل | راهنما"
                )
            else:
                await event.respond("✅ **سلف‌بات فعال شد!**\n\nدستور: `پنل` برای مدیریت")
            
            del LOGIN_STATES[user_id]
            
            if GLOBAL_TELETHON_MANAGER:
                await GLOBAL_TELETHON_MANAGER.start_client(user_id, session_string)

        # جلوگیری از بسته شدن سشن ربات اصلی و فعال نگه داشتن آن برای دریافت پیام‌ها
        await bot.run_until_disconnected()

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
            
    loop.create_task(main_bot_logic())
    loop.create_task(check_users_periodically())
    print("[+] Telethon event loop started.")
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
║    ✓ Block/Mute Lists (User management)                      ║
║    ✓ Payment System (Gems-based)                             ║
║    ✓ Admin Panel (Complete control)                          ║
║    ✓ Free Self-Bot for Admins                                ║
║                                                              ║
║  📍 Server: http://localhost:5000                            ║
║  🚪 Login: http://localhost:5000/auth/admin/login            ║
║  👤 Default: admin / admin123                                ║
║                                                               ║
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
