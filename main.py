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
import time
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from PIL import Image  # ✅ Image processing
import io  # ✅ For in-memory operations

# Telethon Imports
from telethon import TelegramClient, events, functions, types
from telethon.errors import SessionPasswordNeededError
from telethon.sessions import StringSession
from telethon.tl.custom import Button
from telethon.tl.types import ChannelParticipantsAdmins

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
    # Currency conversion
    USD_TO_TOMAN = 163000
    # Game settings
    GAME_DEFAULT_BETS = [100, 200, 400, 600]
    GAME_COMMISSION_PERCENT = 2
    # Monthly gems calculation: 2 gems/hour × 24 hours × 30 days = 1440 gems/month
    MONTHLY_GEMS_NEEDED = 24 * 30 * GEMS_PER_HOUR

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

# ============ MULTI-LANGUAGE SYSTEM ============
LANGUAGES = {
    'fa': '🇮🇷 فارسی',
    'en': '🇬🇧 English',
    'ru': '🇷🇺 Русский',
    'ar': '🇸🇦 العربية',
    'de': '🇩🇪 Deutsch'
}

TRANSLATIONS = {
    'fa': {
        'welcome': '👋 سلام {name}! به Dragon Self Bot خوش آمدید.',
        'select_language': '🗣️ لطفاً زبان خود را انتخاب کنید:',
        'enemy_list': '👿 لیست دشمن',
        'add_enemy': '➕ اضافه کردن دشمن',
        'remove_enemy': '➖ حذف دشمن',
        'crush_list': '💕 لیست کراش',
        'add_crush': '➕ اضافه کردن کراش',
        'remove_crush': '➖ حذف کراش',
        'friend_list': '👥 لیست دوستان',
        'add_friend': '➕ اضافه کردن دوست',
        'remove_friend': '➖ حذف دوست',
        'enter_user_id': '🆔 ایدی کاربر را وارد کنید:',
        'enter_message_text': '📝 متن پیام را وارد کنید:',
        'enter_crush_message': '💕 متن کراش را وارد کنید:',
        'added_successfully': '✅ با موفقیت اضافه شد!',
        'removed_successfully': '✅ با موفقیت حذف شد!',
        'enabled': '✅ فعال',
        'disabled': '❌ غیرفعال',
        'settings': '⚙️ تنظیمات',
        'language_settings': '🗣️ تنظیمات زبان',
        'manage_lists': '📋 مدیریت لیست‌ها',
        'translations': '🌐 ترجمه‌ها',
        'home': '🏠 خانه',
        'back': '⬅️ برگشت',
        'gem_shop': '💎 فروشگاه جم',
        'buy_gems': '💳 خرید جم',
        'wallet': '💰 کیف پول',
        'game': '🎮 بازی',
        'play_game': '🎯 شرط بندی',
        'preset_bet_100': '🎲 شرط 100 جم',
        'preset_bet_200': '🎲 شرط 200 جم',
        'preset_bet_400': '🎲 شرط 400 جم',
        'preset_bet_600': '🎲 شرط 600 جم',
        'custom_bet': '🎲 شرط شخصی',
        'winner': '🏆 برنده:',
        'loser': '💔 بازنده:',
        'gems_won': '💎 جم برده شده:',
        'gems_lost': '💎 جم باخته شده:',
        'game_cancelled': '❌ بازی لغو شد',
        'enter_bet_amount': '💎 مقدار شرط را وارد کنید:',
        'time_name': '⏰ ساعت در نام',
        'time_bio': '⏰ ساعت در بیو',
        'date_bio': '📅 تاریخ در بیو',
        'change_font': '🔤 تغییر فونت',
        'enemy_message_text': '📝 متن های دشمن را وارد کنید (با , جدا کنید):',
        'crush_message_text': '💕 متن های کراش را وارد کنید (با , جدا کنید):',
        'usd_to_toman': 'دلار به تومان: 1 USD = 163,000 تومان',
        'monthly_gems_needed': '📊 جمهای مورد نیاز ماهانه (2 جم/ساعت):',
        'gems_per_hour_loss': '⏸️ هر ساعت 2 جم کم می‌شود',
        'total_monthly': '📈 ماهانه: {total} جم',
    },
    'en': {
        'welcome': '👋 Hello {name}! Welcome to Dragon Self Bot.',
        'select_language': '🗣️ Please select your language:',
        'enemy_list': '👿 Enemy List',
        'add_enemy': '➕ Add Enemy',
        'remove_enemy': '➖ Remove Enemy',
        'crush_list': '💕 Crush List',
        'add_crush': '➕ Add Crush',
        'remove_crush': '➖ Remove Crush',
        'friend_list': '👥 Friend List',
        'add_friend': '➕ Add Friend',
        'remove_friend': '➖ Remove Friend',
        'enter_user_id': '🆔 Enter user ID:',
        'enter_message_text': '📝 Enter message text:',
        'enter_crush_message': '💕 Enter crush message:',
        'added_successfully': '✅ Added successfully!',
        'removed_successfully': '✅ Removed successfully!',
        'enabled': '✅ Enabled',
        'disabled': '❌ Disabled',
        'settings': '⚙️ Settings',
        'language_settings': '🗣️ Language Settings',
        'manage_lists': '📋 Manage Lists',
        'translations': '🌐 Translations',
        'home': '🏠 Home',
        'back': '⬅️ Back',
        'gem_shop': '💎 Gem Shop',
        'buy_gems': '💳 Buy Gems',
        'wallet': '💰 Wallet',
        'game': '🎮 Game',
        'play_game': '🎯 Play Game',
        'preset_bet_100': '🎲 Bet 100 Gems',
        'preset_bet_200': '🎲 Bet 200 Gems',
        'preset_bet_400': '🎲 Bet 400 Gems',
        'preset_bet_600': '🎲 Bet 600 Gems',
        'custom_bet': '🎲 Custom Bet',
        'winner': '🏆 Winner:',
        'loser': '💔 Loser:',
        'gems_won': '💎 Gems Won:',
        'gems_lost': '💎 Gems Lost:',
        'game_cancelled': '❌ Game Cancelled',
        'enter_bet_amount': '💎 Enter bet amount:',
        'time_name': '⏰ Show Time in Name',
        'time_bio': '⏰ Show Time in Bio',
        'date_bio': '📅 Show Date in Bio',
        'change_font': '🔤 Change Font',
        'enemy_message_text': '📝 Enter enemy messages (separated by comma):',
        'crush_message_text': '💕 Enter crush messages (separated by comma):',
        'usd_to_toman': 'USD to Toman: 1 USD = 163,000 Toman',
        'monthly_gems_needed': '📊 Monthly gems needed (2 gems/hour):',
        'gems_per_hour_loss': '⏸️ Loses 2 gems per hour',
        'total_monthly': '📈 Monthly: {total} gems',
    },
    'ru': {
        'welcome': '👋 Привет {name}! Добро пожаловать в Dragon Self Bot.',
        'select_language': '🗣️ Пожалуйста, выберите язык:',
        'enemy_list': '👿 Список врагов',
        'add_enemy': '➕ Добавить врага',
        'remove_enemy': '➖ Удалить врага',
        'crush_list': '💕 Список крашей',
        'add_crush': '➕ Добавить краш',
        'remove_crush': '➖ Удалить краш',
        'friend_list': '👥 Список друзей',
        'add_friend': '➕ Добавить друга',
        'remove_friend': '➖ Удалить друга',
        'enter_user_id': '🆔 Введите ID пользователя:',
        'enter_message_text': '📝 Введите текст сообщения:',
        'enter_crush_message': '💕 Введите сообщение краша:',
        'added_successfully': '✅ Успешно добавлено!',
        'removed_successfully': '✅ Успешно удалено!',
        'enabled': '✅ Включено',
        'disabled': '❌ Отключено',
        'settings': '⚙️ Параметры',
        'language_settings': '🗣️ Параметры языка',
        'manage_lists': '📋 Управление списками',
        'translations': '🌐 Переводы',
        'home': '🏠 Главная',
        'back': '⬅️ Назад',
        'gem_shop': '💎 Магазин драгоценностей',
        'buy_gems': '💳 Купить драгоценности',
        'wallet': '💰 Кошелек',
        'game': '🎮 Игра',
        'play_game': '🎯 Играть',
        'preset_bet_100': '🎲 Ставка 100 драгоценностей',
        'preset_bet_200': '🎲 Ставка 200 драгоценностей',
        'preset_bet_400': '🎲 Ставка 400 драгоценностей',
        'preset_bet_600': '🎲 Ставка 600 драгоценностей',
        'custom_bet': '🎲 Пользовательская ставка',
        'winner': '🏆 Победитель:',
        'loser': '💔 Проигравший:',
        'gems_won': '💎 Выигранные драгоценности:',
        'gems_lost': '💎 Потерянные драгоценности:',
        'game_cancelled': '❌ Игра отменена',
        'enter_bet_amount': '💎 Введите размер ставки:',
        'time_name': '⏰ Показывать время в имени',
        'time_bio': '⏰ Показывать время в биографии',
        'date_bio': '📅 Показывать дату в биографии',
        'change_font': '🔤 Изменить шрифт',
        'enemy_message_text': '📝 Введите сообщения врагов (разделены запятой):',
        'crush_message_text': '💕 Введите сообщения крашей (разделены запятой):',
        'usd_to_toman': 'Доллар в иранский риал: 1 USD = 163,000 иранских риалов',
        'monthly_gems_needed': '📊 Ежемесячно необходимо драгоценностей (2 драгоценности/час):',
        'gems_per_hour_loss': '⏸️ Теряет 2 драгоценности в час',
        'total_monthly': '📈 Ежемесячно: {total} драгоценностей',
        'home': '🏠 Главная',
        'back': '⬅️ Назад'
    },
    'ar': {
        'welcome': '👋 مرحباً {name}! أهلاً وسهلاً في Dragon Self Bot.',
        'select_language': '🗣️ يرجى تحديد لغتك:',
        'enemy_list': '👿 قائمة الأعداء',
        'add_enemy': '➕ إضافة عدو',
        'remove_enemy': '➖ إزالة عدو',
        'crush_list': '💕 قائمة الأحلام',
        'add_crush': '➕ إضافة إلى القائمة',
        'remove_crush': '➖ إزالة من القائمة',
        'friend_list': '👥 قائمة الأصدقاء',
        'add_friend': '➕ إضافة صديق',
        'remove_friend': '➖ إزالة صديق',
        'enter_user_id': '🆔 أدخل معرف المستخدم:',
        'enter_message_text': '📝 أدخل نص الرسالة:',
        'enter_crush_message': '💕 أدخل رسالة الحلم:',
        'added_successfully': '✅ تمت الإضافة بنجاح!',
        'removed_successfully': '✅ تم الحذف بنجاح!',
        'enabled': '✅ مفعل',
        'disabled': '❌ معطل',
        'settings': '⚙️ الإعدادات',
        'language_settings': '🗣️ إعدادات اللغة',
        'manage_lists': '📋 إدارة القوائم',
        'translations': '🌐 الترجمات',
        'home': '🏠 الرئيسية',
        'back': '⬅️ رجوع',
        'gem_shop': '💎 متجر الجواهر',
        'buy_gems': '💳 شراء جواهر',
        'wallet': '💰 المحفظة',
        'game': '🎮 لعبة',
        'play_game': '🎯 العب اللعبة',
        'preset_bet_100': '🎲 رهان 100 جوهرة',
        'preset_bet_200': '🎲 رهان 200 جوهرة',
        'preset_bet_400': '🎲 رهان 400 جوهرة',
        'preset_bet_600': '🎲 رهان 600 جوهرة',
        'custom_bet': '🎲 رهان مخصص',
        'winner': '🏆 الفائز:',
        'loser': '💔 الخاسر:',
        'gems_won': '💎 الجواهر الفائزة:',
        'gems_lost': '💎 الجواهر المفقودة:',
        'game_cancelled': '❌ تم إلغاء اللعبة',
        'enter_bet_amount': '💎 أدخل مبلغ الرهان:',
        'time_name': '⏰ عرض الوقت في الاسم',
        'time_bio': '⏰ عرض الوقت في السيرة',
        'date_bio': '📅 عرض التاريخ في السيرة',
        'change_font': '🔤 تغيير الخط',
        'enemy_message_text': '📝 أدخل رسائل الأعداء (مفصولة بفاصلة):',
        'crush_message_text': '💕 أدخل رسائل الأحلام (مفصولة بفاصلة):',
        'usd_to_toman': 'دولار بالريال الإيراني: 1 دولار = 163000 ريال إيراني',
        'monthly_gems_needed': '📊 الجواهر المطلوبة شهرياً (2 جوهرة/ساعة):',
        'gems_per_hour_loss': '⏸️ يفقد 2 جوهرة في الساعة',
        'total_monthly': '📈 شهري: {total} جوهرة',
    },
    'de': {
        'welcome': '👋 Hallo {name}! Willkommen bei Dragon Self Bot.',
        'select_language': '🗣️ Bitte wählen Sie Ihre Sprache:',
        'enemy_list': '👿 Feindeslist',
        'add_enemy': '➕ Feind hinzufügen',
        'remove_enemy': '➖ Feind entfernen',
        'crush_list': '💕 Crush-Liste',
        'add_crush': '➕ Crush hinzufügen',
        'remove_crush': '➖ Crush entfernen',
        'friend_list': '👥 Freundesliste',
        'add_friend': '➕ Freund hinzufügen',
        'remove_friend': '➖ Freund entfernen',
        'enter_user_id': '🆔 Benutzer-ID eingeben:',
        'enter_message_text': '📝 Nachrichtentext eingeben:',
        'enter_crush_message': '💕 Crush-Nachricht eingeben:',
        'added_successfully': '✅ Erfolgreich hinzugefügt!',
        'removed_successfully': '✅ Erfolgreich entfernt!',
        'enabled': '✅ Aktiviert',
        'disabled': '❌ Deaktiviert',
        'settings': '⚙️ Einstellungen',
        'language_settings': '🗣️ Spracheinstellungen',
        'manage_lists': '📋 Listen verwalten',
        'translations': '🌐 Übersetzungen',
        'home': '🏠 Startseite',
        'back': '⬅️ Zurück',
        'gem_shop': '💎 Edelstein-Shop',
        'buy_gems': '💳 Edelsteine kaufen',
        'wallet': '💰 Geldbörse',
        'game': '🎮 Spiel',
        'play_game': '🎯 Spielen',
        'preset_bet_100': '🎲 Einsatz 100 Edelsteine',
        'preset_bet_200': '🎲 Einsatz 200 Edelsteine',
        'preset_bet_400': '🎲 Einsatz 400 Edelsteine',
        'preset_bet_600': '🎲 Einsatz 600 Edelsteine',
        'custom_bet': '🎲 Benutzerdefinierter Einsatz',
        'winner': '🏆 Gewinner:',
        'loser': '💔 Verlierer:',
        'gems_won': '💎 Edelsteine gewonnen:',
        'gems_lost': '💎 Edelsteine verloren:',
        'game_cancelled': '❌ Spiel abgebrochen',
        'enter_bet_amount': '💎 Einsatzbetrag eingeben:',
        'time_name': '⏰ Uhrzeit im Namen anzeigen',
        'time_bio': '⏰ Uhrzeit in Bio anzeigen',
        'date_bio': '📅 Datum in Bio anzeigen',
        'change_font': '🔤 Schriftart ändern',
        'enemy_message_text': '📝 Feinschaftsnachrichten eingeben (durch Komma getrennt):',
        'crush_message_text': '💕 Crush-Nachrichten eingeben (durch Komma getrennt):',
        'usd_to_toman': 'Dollar zu iranischem Rial: 1 USD = 163.000 iranische Rial',
        'monthly_gems_needed': '📊 Monatlich erforderliche Edelsteine (2 Edelsteine/Stunde):',
        'gems_per_hour_loss': '⏸️ Verliert 2 Edelsteine pro Stunde',
        'total_monthly': '📈 Monatlich: {total} Edelsteine',
    }
}

def get_text(user_language, key):
    """سازگار شدن متن‌ها با زبان کاربر"""
    lang = user_language if user_language in TRANSLATIONS else 'fa'
    return TRANSLATIONS[lang].get(key, TRANSLATIONS['fa'].get(key, key))

# ============ PERFORMANCE OPTIMIZATION - USER CACHE ============
# Reduces database queries for frequently accessed user data
_user_cache = {}
_cache_timeout = 300  # 5 minutes

def get_cached_user(user_id):
    """Get user from cache or database with TTL"""
    import time
    if user_id in _user_cache:
        cached_data, timestamp = _user_cache[user_id]
        if time.time() - timestamp < _cache_timeout:
            return cached_data
    # Fetch from DB and cache
    user = User.objects(telegram_id=user_id).first()
    if user:
        _user_cache[user_id] = (user, __import__('time').time())
    return user

def invalidate_user_cache(user_id):
    """Clear user cache when data changes"""
    if user_id in _user_cache:
        del _user_cache[user_id]

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
    admin_id = StringField(default='default')  # ✅ MongoDB ObjectId reference
    telegram_id = IntField(unique=True, required=True)
    phone_number = StringField(default='')  # ✅ Optional - can be empty
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
    language = StringField(default='fa')  # ✅ fa (فارسی) یا en (انگلیسی) - پیش‌فرض فارسی
    language_selected = BooleanField(default=False)  # ✅ Track if user selected language on first run
    enemy_messages = ListField(StringField(), default=[])  # ✅ Customizable enemy messages (comma-separated)
    crush_messages = ListField(StringField(), default=[])  # ✅ Customizable crush messages
    friend_messages = ListField(StringField(), default=[])  # ✅ Customizable friend messages
    # ✅ 🛡 Security & Protection Features
    anti_login_enabled = BooleanField(default=False)  # ✅ محافظت ورود
    copy_profile_enabled = BooleanField(default=False)  # ✅ کپی پروفایل
    profile_backup = DictField(default={})  # Store original profile to restore
    # ✅ Enemy List Settings
    enemy_list_enabled = BooleanField(default=False)
    # ✅ Friend List Settings
    friend_list_enabled = BooleanField(default=False)
    # ✅ Crush List Settings
    crush_list_enabled = BooleanField(default=False)
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
        'indexes': [
            'user_id', 'status', 'created_at',
            # TTL Index: automatically delete after 7 days (604800 seconds)
            {'fields': [('created_at', 1)], 'expireAfterSeconds': 604800}
        ]
    }
    user_id = IntField(required=True)
    gems = IntField(required=True)
    amount_toman = IntField(required=True)
    receipt_image = StringField()  # ✅ Base64 encoded image (temporary)
    receipt_image_url = StringField()  # ✅ Optional: for external URL storage
    approved_image = StringField()  # ✅ Permanent image if approved (base64)
    auto_delete_at = DateTimeField()  # ✅ Auto-delete temp image after 5 days if not approved
    status = StringField(default='pending')  # pending, approved, rejected
    approved_by_admin = IntField()
    approval_note = StringField()
    created_at = DateTimeField(default=datetime.utcnow)  # ✅ TTL will delete based on this
    approved_at = DateTimeField()
    is_permanent = BooleanField(default=False)  # ✅ Image is saved permanently if True

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
    custom_messages = ListField(StringField(), default=[])  # ✅ Custom semicolon-separated messages
    created_at = DateTimeField(default=datetime.utcnow)

class FriendList(Document):
    meta = {'collection': 'friend_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    responses = DictField(default={})
    custom_messages = ListField(StringField(), default=[])  # ✅ Custom messages for friends
    created_at = DateTimeField(default=datetime.utcnow)

class CrushList(Document):
    meta = {'collection': 'crush_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    messages = DictField(default={})
    custom_messages = ListField(StringField(), default=[])  # ✅ Custom crush messages
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

class Bet(Document):
    meta = {
        'collection': 'bets',
        'indexes': ['bet_id', 'creator_id', 'joiner_id', 'status', 'group_id']
    }
    bet_id = StringField(required=True, unique=True)
    group_id = IntField(required=True)
    creator_id = IntField(required=True)
    creator_name = StringField()
    joiner_id = IntField(sparse=True)
    joiner_name = StringField()
    amount = IntField(required=True)
    status = StringField(choices=['waiting', 'active', 'completed'], default='waiting')
    winner_id = IntField(sparse=True)
    loser_id = IntField(sparse=True)
    commission = IntField(default=2)
    winner_gems = IntField(default=0)
    loser_gems_lost = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    completed_at = DateTimeField(sparse=True)
    message_id = IntField(sparse=True)


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
        """Task to update Bio and Name with time if enabled - ✅ Updated every 3 seconds for accuracy"""
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
            await asyncio.sleep(3)  # ✅ بهتر: هر 3 ثانیه چک کن (قبلاً 60 ثانیه بود)

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
                        new_entry = model_class(user_id=user.id, target_id=target_id)
                        new_entry.save()
                    await event.edit(f"✅ کاربر به لیست {list_type} اضافه شد.")
                elif action == 'remove':
                    model_class.objects(user_id=user.id, target_id=target_id).delete()
                    await event.edit(f"✅ کاربر از لیست {list_type} حذف شد.")

            # Enemy Commands with Custom Messages
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
            # Add enemy messages (comma-separated)
            if text.startswith('متن دشمن '):
                msg_text = text.replace('متن دشمن ', '').strip()
                # Split by comma for multiple messages
                messages = [m.strip() for m in msg_text.split(',') if m.strip()]
                user.enemy_messages = messages
                user.save()
                await event.edit(f"✅ {len(messages)} متن دشمن اضافه شد.\n📝 متن‌ها:\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(messages)]))
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
            # Add crush messages (comma-separated)
            if text.startswith('متن کراش '):
                msg_text = text.replace('متن کراش ', '').strip()
                messages = [m.strip() for m in msg_text.split(',') if m.strip()]
                user.crush_messages = messages
                user.save()
                await event.edit(f"✅ {len(messages)} متن کراش اضافه شد.\n💕 متن‌ها:\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(messages)]))
                return

            # ============ FRIEND LIST EXTENDED COMMANDS ============
            # Friend text management
            if text.startswith('تنظیم متن دوست '):
                msg_text = text.replace('تنظیم متن دوست ', '').strip()
                messages = [m.strip() for m in msg_text.split(',') if m.strip()]
                user.friend_messages = messages
                user.save()
                await event.edit(f"✅ {len(messages)} متن دوست اضافه شد.\n📝 متن‌ها:\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(messages)]))
                return
            
            if text == 'لیست متن دوست':
                if user.friend_messages:
                    msg = "📜 **متن‌های دوست:**\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(user.friend_messages)])
                    await event.edit(msg)
                else:
                    await event.edit("❌ متنی برای دوستان تعریف نشده.")
                return
            
            if text.startswith('حذف متن دوست '):
                idx = int(text.replace('حذف متن دوست ', '').strip()) - 1
                if 0 <= idx < len(user.friend_messages):
                    user.friend_messages.pop(idx)
                    user.save()
                    await event.edit(f"✅ متن شماره {idx+1} حذف شد.")
                else:
                    await event.edit("❌ شماره نامعتبر است.")
                return

            # ============ ENEMY LIST EXTENDED COMMANDS ============
            if text == 'دشمن روشن':
                user.enemy_list_enabled = True
                user.save()
                await event.edit("✅ فعالیت خودکار برای لیست دشمن **فعال** شد.")
                return
            
            if text == 'دشمن خاموش':
                user.enemy_list_enabled = False
                user.save()
                await event.edit("❌ فعالیت خودکار برای لیست دشمن **غیرفعال** شد.")
                return
            
            if text.startswith('تنظیم متن دشمن '):
                msg_text = text.replace('تنظیم متن دشمن ', '').strip()
                messages = [m.strip() for m in msg_text.split(',') if m.strip()]
                user.enemy_messages = messages
                user.save()
                await event.edit(f"✅ {len(messages)} متن دشمن اضافه شد.\n📝 متن‌ها:\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(messages)]))
                return
            
            if text == 'لیست متن دشمن':
                if user.enemy_messages:
                    msg = "📜 **متن‌های دشمن:**\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(user.enemy_messages)])
                    await event.edit(msg)
                else:
                    await event.edit("❌ متنی برای دشمنان تعریف نشده.")
                return
            
            if text.startswith('حذف متن دشمن '):
                idx = int(text.replace('حذف متن دشمن ', '').strip()) - 1
                if 0 <= idx < len(user.enemy_messages):
                    user.enemy_messages.pop(idx)
                    user.save()
                    await event.edit(f"✅ متن شماره {idx+1} حذف شد.")
                else:
                    await event.edit("❌ شماره نامعتبر است.")
                return

            # ============ CRUSH LIST EXTENDED COMMANDS ============
            if text == 'لیست متن کراش':
                if user.crush_messages:
                    msg = "📜 **پیام‌های کراش:**\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(user.crush_messages)])
                    await event.edit(msg)
                else:
                    await event.edit("❌ پیامی برای کراش تعریف نشده.")
                return
            
            if text.startswith('حذف متن کراش '):
                idx = int(text.replace('حذف متن کراش ', '').strip()) - 1
                if 0 <= idx < len(user.crush_messages):
                    user.crush_messages.pop(idx)
                    user.save()
                    await event.edit(f"✅ پیام شماره {idx+1} حذف شد.")
                else:
                    await event.edit("❌ شماره نامعتبر است.")
                return

            # ============ SECURITY FEATURES ============
            # Anti-Login Protection (نتی لوگین)
            if text == 'نتی لوگین روشن':
                user.anti_login_enabled = True
                user.save()
                await event.edit("🛡 **محافظت ورود فعال شد!**\n\nتلاش برای ورود محدود می‌شود.")
                return
            
            if text == 'نتی لوگین خاموش':
                user.anti_login_enabled = False
                user.save()
                await event.edit("🔓 محافظت ورود غیرفعال شد.")
                return

            # Copy Profile (کپی پروفایل)
            if text == 'کپی روشن':
                if not event.is_private:
                    if not event.is_reply:
                        await event.edit("❌ غلط! برای کپی پروفایل باید روی تصویر/پروفایل فردی ریپلای کنید.")
                        return
                    reply = await event.get_reply_message()
                    target = await reply.get_sender()
                else:
                    target = await event.get_sender()
                
                try:
                    # Store original profile backup
                    me = await client.get_me()
                    user.profile_backup = {
                        'first_name': me.first_name or '',
                        'last_name': me.last_name or '',
                        'bio': (await client.get_profile(me)).bio
                    }
                    
                    # Copy target profile
                    target_profile = await client.get_profile(target.id)
                    await client(functions.account.UpdateProfileRequest(
                        first_name=target.first_name or '',
                        last_name=target.last_name or ''
                    ))
                    if target_profile.bio:
                        await client(functions.account.UpdateProfileRequest(about=target_profile.bio))
                    
                    user.copy_profile_enabled = True
                    user.save()
                    await event.edit(f"✅ **پروفایل کپی شد!**\n\n👤 نام: {target.first_name} {target.last_name or ''}")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                return
            
            if text == 'کپی خاموش':
                if user.profile_backup:
                    try:
                        await client(functions.account.UpdateProfileRequest(
                            first_name=user.profile_backup.get('first_name', ''),
                            last_name=user.profile_backup.get('last_name', ''),
                            about=user.profile_backup.get('bio', '')
                        ))
                        user.copy_profile_enabled = False
                        user.profile_backup = {}
                        user.save()
                        await event.edit("✅ پروفایل اصلی بازیابی شد.")
                    except Exception as e:
                        await event.edit(f"❌ خطا: {str(e)}")
                else:
                    await event.edit("❌ بکاپی پروفایل اصلی وجود ندارد.")
                return

            # ============ TOOLS & MANAGEMENT ============
            # Tag All (تگ همه)
            if text == 'تگ':
                if event.is_group:
                    try:
                        members = await client.get_participants(event.chat_id)
                        mentions = ' '.join([f'[{m.first_name}](tg://user?id={m.id})' for m in members[:50]])
                        await event.delete()
                        await client.send_message(event.chat_id, mentions, parse_mode='md')
                    except Exception as e:
                        await event.edit(f"❌ خطا: {str(e)}")
                return
            
            # Tag Admins (تگ ادمین ها)
            if text == 'تگ ادمین ها':
                if event.is_group:
                    try:
                        admins = await client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins())
                        mentions = ' '.join([f'[{a.first_name}](tg://user?id={a.id})' for a in admins])
                        await event.delete()
                        await client.send_message(event.chat_id, mentions, parse_mode='md')
                    except Exception as e:
                        await event.edit(f"❌ خطا: {str(e)}")
                return
            
            # Show My Phone Number
            if text == 'شماره من':
                me = await client.get_me()
                phone = me.phone
                await event.edit(f"📱 **شماره من:** `{phone}`")
                return
            
            # Download (ریپلای)
            if text == 'دانلود':
                if event.is_reply:
                    try:
                        reply = await event.get_reply_message()
                        await event.edit("⏳ درحال دانلود...")
                        path = await client.download_media(reply)
                        await event.edit(f"✅ دانلود شد:\n`{path}`")
                    except Exception as e:
                        await event.edit(f"❌ خطا: {str(e)}")
                else:
                    await event.edit("❌ لطفا روی فایل/رسانه ریپلای کنید.")
                return
            
            # Ban (ریپلای)
            if text == 'بن':
                if not event.is_group:
                    await event.edit("❌ فقط در گروه‌ها کار می‌کند.")
                    return
                if not event.is_reply:
                    await event.edit("❌ لطفا روی پیام کاربری ریپلای کنید.")
                    return
                try:
                    reply = await event.get_reply_message()
                    await client.kick_participant(event.chat_id, reply.sender_id)
                    await event.edit("✅ کاربر از گروه حذف شد.")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                return
            
            # Pin Message (ریپلای)
            if text == 'پین':
                if not event.is_group:
                    await event.edit("❌ فقط در گروه‌ها کار می‌کند.")
                    return
                if not event.is_reply:
                    await event.edit("❌ لطفا روی پیام ریپلای کنید.")
                    return
                try:
                    reply = await event.get_reply_message()
                    await client.pin_message(event.chat_id, reply)
                    await event.edit("✅ پیام پین شد.")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                return
            
            # Unpin
            if text == 'آن پین':
                if not event.is_group:
                    await event.edit("❌ فقط در گروه‌ها کار می‌کند.")
                    return
                try:
                    await client.unpin_message(event.chat_id)
                    await event.edit("✅ آخرین پیام آن‌پین شد.")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                return
            
            # Spam - Repeat text X times (اسپم)
            if text.startswith('اسپم '):
                parts = text.replace('اسپم ', '').split(' ')
                if len(parts) >= 2 and parts[-1].isdigit():
                    count = int(parts[-1])
                    msg = ' '.join(parts[:-1])
                    if count > 100:
                        await event.edit("❌ حداکثر 100 بار!")
                        return
                    await event.delete()
                    for i in range(count):
                        await client.send_message(event.chat_id, msg)
                        await asyncio.sleep(0.5)
                else:
                    await event.edit("❌ فرمت: `اسپم [متن] [تعداد]`")
                return
            
            # Flood - Fast spam (فلود)
            if text.startswith('فلود '):
                parts = text.replace('فلود ', '').split(' ')
                if len(parts) >= 2 and parts[-1].isdigit():
                    count = int(parts[-1])
                    msg = ' '.join(parts[:-1])
                    if count > 50:
                        await event.edit("❌ حداکثر 50 بار!")
                        return
                    await event.delete()
                    for i in range(count):
                        await client.send_message(event.chat_id, msg)
                else:
                    await event.edit("❌ فرمت: `فلود [متن] [تعداد]`")
                return
            
            # Ping - Check connection
            if text == 'ping':
                start = time.time()
                msg = await client.send_message(event.chat_id, '⏱')
                end = time.time()
                ping = int((end - start) * 1000)
                await msg.edit(f"🏓 **Ping:** `{ping}ms`")
                return

            # Gem Shop
            if text == 'فروشگاه جم' or text == 'محاسبه جم':
                monthly_need = 24 * 30 * Config.GEMS_PER_HOUR  # 2 gems/hour * 24 * 30 = 1440
                usd_needed = (Config.GEM_PRICE_TOMAN * monthly_need) / Config.USD_TO_TOMAN
                shop_msg = f"""💎 **فروشگاه جم**

📊 اطلاعات موردنیاز:
• هر ساعت: {Config.GEMS_PER_HOUR} جم کم می‌شود
• ماهانه: {monthly_need} جم نیاز است
• هزینه: {monthly_need * Config.GEM_PRICE_TOMAN:,.0f} تومان = {usd_needed:.2f} USD

💳 نرخ تبدیل: 1 USD = {Config.USD_TO_TOMAN:,} تومان
"""
                await event.edit(shop_msg)
                return

            # Game commands
            if text in ['بازی', 'play', 'game']:
                game_msg = """🎮 **بازی شرط بندی**

بازی را با یکی از دستورات زیر شروع کنید:

🎲 شرط‌های تعریف شده:
`شرط 100` - شرط 100 جم
`شرط 200` - شرط 200 جم
`شرط 400` - شرط 400 جم
`شرط 600` - شرط 600 جم

🎯 شرط شخصی:
`شرط [عدد]` - شرط با تعداد دلخواه جم

نتیجه: برنده تصادفی انتخاب می‌شود!
"""
                await event.edit(game_msg)
                return

            # Bet commands for group
            if text.startswith('شرط ') and event.is_group:
                bet_text = text.replace('شرط ', '').strip()
                if bet_text.isdigit():
                    amount = int(bet_text)
                    if amount > 0 and user.gems >= amount:
                        bet_id = f"{event.chat_id}_{datetime.utcnow().timestamp()}"
                        new_bet = Bet(
                            bet_id=bet_id,
                            group_id=event.chat_id,
                            creator_id=user.id,
                            creator_name=user.username or user.first_name,
                            amount=amount,
                            status='waiting'
                        )
                        new_bet.save()
                        
                        # Create game message with buttons
                        game_msg = f"""🎮 **بازی شرط بندی**

💎 شرط: {amount} جم
👤 ایجاد کننده: @{user.username or user.first_name}

برای شرکت در بازی بر روی دکمه زیر کلیک کنید!
"""
                        await event.edit(game_msg)
                    else:
                        await event.edit(f"❌ جم کافی ندارید! شما {user.gems} جم دارید.")
                return
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
            
            # ✅ دشمن - پاسخ خودکار با متن‌های custom
            enemy = EnemyList.objects(user_id=user.id, target_id=sender_id).first()
            if enemy and enemy.is_enabled:
                # اولویت: custom_messages از EnemyList یا enemy_messages از User
                messages = enemy.custom_messages if enemy.custom_messages else user.enemy_messages
                if messages:
                    response_text = random.choice(messages)
                    try:
                        await event.reply(response_text)
                    except:
                        pass
            
            # ✅ کراش - پاسخ خودکار با متن‌های custom          
            crush = CrushList.objects(user_id=user.id, target_id=sender_id).first()
            if crush and crush.is_enabled:
                # اولویت: custom_messages از CrushList یا crush_messages از User
                messages = crush.custom_messages if crush.custom_messages else user.crush_messages
                if messages:
                    response_text = random.choice(messages)
                    try:
                        await event.reply(response_text)
                    except:
                        pass
            
            # ✅ دوست - بدون پاسخ (فقط نشان‌دادن لیست)
            friend = FriendList.objects(user_id=user.id, target_id=sender_id).first()
            # دوستان نیازی به پاسخ خودکار ندارند

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

    async def mass_report_authenticated(self, target_username, report_message, authenticated_users):
        """✅ Mass report using only authenticated users with self-bot activated"""
        reported_count = 0
        for user in authenticated_users:
            user_id = int(user.telegram_id)
            if user_id in self.clients:
                try:
                    client = self.clients[user_id]
                    target = await client.get_input_entity(target_username)
                    await client(functions.account.ReportPeerRequest(
                        peer=target,
                        reason=types.InputReportReasonFake(),
                        message=report_message
                    ))
                    reported_count += 1
                    print(f"[+] Reported {target_username} from authenticated session {user_id}")
                except Exception as e:
                    print(f"[-] Failed to report from authenticated session {user_id}: {e}")
        print(f"✅ Report completed: {reported_count} authenticated accounts used")

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
        # ✅ Move image to approved storage (permanent)
        if payment.receipt_image:
            payment.approved_image = payment.receipt_image
            payment.is_permanent = True
            payment.receipt_image = None  # ✅ Clear temporary image
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
        # ✅ Clear temporary image on rejection
        payment.receipt_image = None
        payment.approved_image = None
        payment.is_permanent = False
        payment.save()
        return {'status': 'success', 'message': 'Payment rejected and image deleted'}
    
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
                # ✅ Start image cleanup job (once per 24 hours)
                GemDeductionScheduler.scheduler.add_job(
                    GemDeductionScheduler.cleanup_expired_images,
                    'interval',
                    hours=24,
                    id='cleanup_images'
                )
            
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
    def cleanup_expired_images():
        """✅ Delete receipt images older than 5 days if still pending"""
        try:
            five_days_ago = datetime.utcnow() - timedelta(days=5)
            # Find pending payments older than 5 days
            expired_payments = Payment.objects(
                status='pending',
                created_at__lt=five_days_ago,
                receipt_image__exists=True
            ).all()
            
            for payment in expired_payments:
                payment.receipt_image = None  # ✅ Delete temporary image
                payment.save()
                print(f"[CLEANUP] Deleted expired receipt image for payment: {payment.id}")
        except Exception as e:
            print(f"[ERROR] Image cleanup failed: {e}")
    
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
    
    # ✅ Setup TTL index for auto-deletion of payment receipts after 7 days
    try:
        from pymongo import ASCENDING
        db = connect(
            db=app.config.get('MONGODB_DB_NAME', 'Dragon_self_bot'),
            host=app.config.get('MONGODB_URI'),
            retryWrites=True,
            w='majority'
        ).get_database()
        
        # Create TTL index: delete documents 7 days (604800 seconds) after created_at
        db.payments.create_index(
            [('created_at', ASCENDING)],
            expireAfterSeconds=604800  # 7 days
        )
        print("✅ TTL index created for payments collection (7 days auto-delete)")
    except Exception as e:
        print(f"⚠️ Warning: Could not create TTL index: {e}")
    
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
        admin_id_str = session.get('admin_id')
        admin = Admin.objects(id=ObjectId(admin_id_str)).first()
        
        # Get ALL users (both pending and authenticated)
        all_users = User.objects.all()
        print(f"📊 Total users in DB: {len(all_users)}")
        
        # Separate pending and authenticated users
        pending_users = [u for u in all_users if not u.is_authenticated]
        authenticated_users = [u for u in all_users if u.is_authenticated]
        
        print(f"⏳ Pending: {len(pending_users)}, ✅ Auth: {len(authenticated_users)}")
        
        # Build pending users list
        pending_html = []
        for u in pending_users:
            user_id_str = str(u.id)  # ✅ Convert ObjectId to string explicitly
            pending_html.append(f'''
            <tr>
                <td>{u.username or u.telegram_id}</td>
                <td>{u.gems}</td>
                <td><input type="number" id="gem_input_{user_id_str}" value="0" min="0"></td>
                <td>
                    <button class="btn-add" onclick="addGems('{user_id_str}')">✅ اضافه کن</button>
                </td>
                <td>
                    <button class="btn-activate" onclick="toggleSelf('{user_id_str}', true)">🚀 فعال کن</button>
                </td>
            </tr>
            ''')
        
        # Build authenticated users list
        auth_html = []
        for u in authenticated_users:
            user_id_str = str(u.id)  # ✅ Convert ObjectId to string explicitly
            auth_html.append(f'''
            <tr>
                <td>{u.username or u.telegram_id}</td>
                <td>{u.gems}</td>
                <td><input type="number" id="gem_input_{user_id_str}" value="0" min="0"></td>
                <td>
                    <button class="btn-add" onclick="addGems('{user_id_str}')">✅ اضافه کن</button>
                    <button class="btn-subtract" onclick="subtractGems('{user_id_str}')">➖ کم کن</button>
                </td>
                <td>
                    <button class="btn-deactivate" onclick="toggleSelf('{user_id_str}', false)">❌ غیرفعال</button>
                </td>
                <td>
                    <button class="btn-delete" onclick="deleteUser('{user_id_str}')">🗑️ حذف</button>
                </td>
            </tr>
            ''')
        
        return render_template_string(MANAGE_USERS_TEMPLATE, 
            pending_users='\n'.join(pending_html) if pending_html else '<tr><td colspan="5" style="text-align: center; color: #999;">هیچ کاربری در انتظار نیست</td></tr>',
            authenticated_users='\n'.join(auth_html) if auth_html else '<tr><td colspan="6" style="text-align: center; color: #999;">هیچ کاربر فعال نیست</td></tr>',
            pending_count=len(pending_users),
            auth_count=len(authenticated_users),
            total_count=len(all_users),
            admin_username=admin.username if admin else "Admin")
    
    @app.route('/admin/payments/manage')
    @admin_required
    def manage_payments_page():
        """Manage payments UI (Web Panel)"""
        payments = Payment.objects(status='pending').all()
        
        payments_html = []
        for p in payments:
            user = User.objects(id=p.user_id).first()
            username = user.username if user else f"ID: {p.user_id}"
            receipt_button = ""
            if p.receipt_image:
                # If receipt_image is base64 encoded
                payment_id = str(p.id)
                receipt_src = f"data:image/png;base64,{p.receipt_image}" if not p.receipt_image.startswith('data:') else p.receipt_image
                receipt_button = f"<button data-image=\"{payment_id}\" class='receipt-btn' style='background: #3498db; color: white; padding: 5px 10px; border: none; border-radius: 5px; cursor: pointer;'>📷 رسید</button>"
            else:
                receipt_button = "<span style='color: #999;'>بدون رسید</span>"
            
            payments_html.append(f'''
            <tr>
                <td>{username}</td>
                <td>{p.gems}</td>
                <td>{p.amount_toman:,}</td>
                <td>{p.created_at.strftime("%Y-%m-%d %H:%M") if p.created_at else "نامشخص"}</td>
                <td>
                    {receipt_button}
                </td>
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
            admin_numeric_id=admin.telegram_id if admin and admin.telegram_id else 'لم تعیین نشده',
            admin_id=str(admin.id) if admin else '',
            require_subscription=settings.require_subscription if settings else False,  # ✅ عضویت اجباری
            subscription_channel=settings.subscription_channel or ''  # ✅ کانال عضویت
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
    
    @app.route('/admin/payment/<payment_id>/image', methods=['GET'])
    @admin_required
    def get_payment_image(payment_id):
        """Get payment receipt image as base64"""
        try:
            payment = Payment.objects(id=ObjectId(payment_id)).first()
            if payment and payment.receipt_image:
                image_data = payment.receipt_image
                if not image_data.startswith('data:'):
                    image_data = f"data:image/png;base64,{image_data}"
                return jsonify({'status': 'success', 'image': image_data})
            else:
                return jsonify({'status': 'error', 'message': 'عکس در دسترس نیست'}), 404
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
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
        numeric_id = data.get('numeric_id')
        
        if new_username != admin.username:
            if Admin.objects(username=new_username).first():
                return jsonify({'status': 'error', 'message': 'این نام کاربری قبلاً استفاده شده است.'}), 400
            admin.username = new_username
        
        if new_password and new_password.strip():
            admin.password_hash = generate_password_hash(new_password)
        
        # Update numeric ID if provided
        if numeric_id and isinstance(numeric_id, int):
            admin.telegram_id = numeric_id
        
        # Update settings
        admin.settings.gem_price_toman = data.get('gem_price_toman', 40)
        admin.settings.minimum_gems_activate = data.get('minimum_gems_activate', 80)
        admin.settings.gems_per_hour = data.get('gems_per_hour', 2)
        admin.settings.bank_card_number = data.get('bank_card_number', '')
        admin.settings.bank_account_name = data.get('bank_account_name', '')
        admin.settings.require_subscription = data.get('require_subscription', False)  # ✅ عضویت اجباری
        admin.settings.subscription_channel = data.get('subscription_channel', '')  # ✅ کانال عضویت
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
        """Mass report - only authenticated users (with self-bot activated)"""
        data = request.get_json()
        target = data.get('target_username')
        report_msg = data.get('report_message', 'This channel is engaging in scam and fraudulent activities. Please review.')
        
        if not target:
            return jsonify({'status': 'error', 'message': 'Target username is required'}), 400
        
        # ✅ Filter only authenticated users with self-bot activated
        authenticated_users = User.objects(is_authenticated=True).all()
        authenticated_count = len(authenticated_users)
        
        if authenticated_count == 0:
            return jsonify({'status': 'error', 'message': 'No authenticated users available for reporting'}), 400
        
        if GLOBAL_TELETHON_MANAGER:
            # Only use sessions from authenticated users
            asyncio.run_coroutine_threadsafe(
                GLOBAL_TELETHON_MANAGER.mass_report_authenticated(target, report_msg, authenticated_users), 
                GLOBAL_TELETHON_MANAGER.loop
            )
            return jsonify({
                'status': 'success', 
                'message': f'Reporting {target} started using {authenticated_count} authenticated accounts.',
                'users_count': authenticated_count
            })
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

    @app.route('/admin/info/payments', methods=['GET'])
    @admin_required
    def payment_info():
        """Get payment database info including auto-deletion status"""
        from datetime import timedelta
        
        pending = len(Payment.objects(status='pending').all())
        approved = len(Payment.objects(status='approved').all())
        rejected = len(Payment.objects(status='rejected').all())
        total = pending + approved + rejected
        
        # Calculate oldest payment
        oldest_payment = None
        oldest_payment_date = None
        for p in Payment.objects.all().order_by('created_at'):
            oldest_payment = p
            oldest_payment_date = p.created_at
            break
        
        # Calculate auto-deletion timeline
        retention_days = 7
        if oldest_payment_date:
            delete_date = oldest_payment_date + timedelta(days=retention_days)
            days_until_delete = (delete_date - datetime.utcnow()).days
        else:
            delete_date = None
            days_until_delete = None
        
        return jsonify({
            'status': 'success',
            'pending': pending,
            'approved': approved,
            'rejected': rejected,
            'total': total,
            'oldest_payment_date': oldest_payment_date.isoformat() if oldest_payment_date else None,
            'retention_days': retention_days,
            'auto_delete_info': f"Payments are automatically deleted after {retention_days} days (TTL Index enabled)",
            'ttl_enabled': True
        })

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
        body { 
            font-family: "Vazir", "Segoe UI", sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; 
            padding: 20px; 
        }
        .container { max-width: 1200px; margin: 0 auto; }
        header { 
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            color: white; 
            padding: 25px; 
            border-radius: 15px; 
            margin-bottom: 30px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }
        h1 { margin: 0; font-size: 28px; }
        h2 { color: white; margin: 30px 0 15px; font-size: 20px; }
        .table-container { 
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 25px; 
            border-radius: 15px; 
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            overflow-x: auto; 
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 30px;
        }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: right; border-bottom: 1px solid #eee; }
        th { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            font-weight: 600; 
            color: white; 
            border-radius: 8px;
        }
        tr:hover { background: #f0f0f0; }
        input { 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 6px;
            width: 70px;
            font-size: 14px;
        }
        button { 
            padding: 8px 12px; 
            margin: 2px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 12px; 
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            display: inline-block;
        }
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        .btn-add { background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); }
        .btn-subtract { background: linear-gradient(135deg, #e67e22 0%, #f39c12 100%); }
        .btn-activate { background: linear-gradient(135deg, #3498db 0%, #2980b9 100%); }
        .btn-deactivate { background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%); }
        .btn-delete { background: linear-gradient(135deg, #c0392b 0%, #a93226 100%); }
        .message { 
            padding: 15px; 
            border-radius: 8px; 
            margin-bottom: 20px; 
            display: none;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        .msg-success { 
            background: rgba(39, 174, 96, 0.2);
            color: #27ae60;
            border-color: #27ae60;
        }
        .msg-error { 
            background: rgba(231, 76, 60, 0.2);
            color: #e74c3c;
            border-color: #e74c3c;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>👥 مدیریت کاربران</h1>
            <p style="margin-top: 10px; opacity: 0.95;">خوش آمدید، {{ admin_username }}</p>
        </header>
        
        <div id="message" class="message"></div>
        
        <h2>⏳ کاربران در انتظار (فقط /start زده اند)</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>نام کاربری</th>
                        <th>جم فعلی</th>
                        <th>تعداد جم برای اضافه</th>
                        <th>اضافه کردن جم</th>
                        <th>فعال‌سازی سلف</th>
                    </tr>
                </thead>
                <tbody>
                    {{ pending_users }}
                </tbody>
            </table>
        </div>
        
        <h2>✅ کاربران فعال (سلف را فعال کردند)</h2>
        <div class="table-container">
            <table>
                <thead>
                    <tr>
                        <th>نام کاربری</th>
                        <th>جم فعلی</th>
                        <th>تغییر تعداد جم</th>
                        <th>عملیات</th>
                        <th>غیرفعال‌سازی</th>
                        <th>حذف</th>
                    </tr>
                </thead>
                <tbody>
                    {{ authenticated_users }}
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
            const inputEl = document.getElementById('gem_input_' + userId);
            if (!inputEl) {
                showMessage('❌ خطا: عنصر ورودی یافت نشد', 'error');
                return;
            }
            
            const amount = parseInt(inputEl.value) || 0;
            if (!amount || amount <= 0) {
                showMessage('❌ لطفا تعداد صحیح جم وارد کنید.', 'error');
                return;
            }
            
            try {
                const res = await fetch('/admin/user/' + userId + '/gems', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gems: amount})
                });
                const data = await res.json();
                showMessage(data.message || '✅ جم با موفقیت اضافه شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error.message, 'error');
            }
        }

        async function subtractGems(userId) {
            const inputEl = document.getElementById('gem_input_' + userId);
            if (!inputEl) {
                showMessage('❌ خطا: عنصر ورودی یافت نشد', 'error');
                return;
            }
            
            const amount = parseInt(inputEl.value) || 0;
            if (!amount || amount <= 0) {
                showMessage('❌ لطفا تعداد صحیح جم وارد کنید.', 'error');
                return;
            }
            
            try {
                const res = await fetch('/admin/user/' + userId + '/gems', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({gems: -amount})
                });
                const data = await res.json();
                showMessage(data.message || '✅ جم با موفقیت کم شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error.message, 'error');
            }
        }

        async function toggleSelf(userId, enabled) {
            try {
                const res = await fetch('/admin/user/' + userId + '/self/toggle', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({is_enabled: enabled})
                });
                const data = await res.json();
                showMessage(data.message || 'تغییر با موفقیت انجام شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error.message, 'error');
            }
        }

        async function deleteUser(userId) {
            if (!confirm('⚠️ آیا مطمئن هستید؟ این کار قابل بازگشت نیست!')) return;
            
            try {
                const res = await fetch('/admin/user/' + userId + '/delete', {
                    method: 'POST'
                });
                const data = await res.json();
                showMessage(data.message || '✅ کاربر حذف شد.', 'success');
                setTimeout(() => location.reload(), 1500);
            } catch (error) {
                showMessage('❌ خطا: ' + error.message, 'error');
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
        .info { background: #3498db; }
        .message { padding: 15px; border-radius: 8px; margin-bottom: 20px; display: none; }
        .msg-success { background: #d4edda; color: #155724; }
        .msg-error { background: #f8d7da; color: #721c24; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
        .modal-content { background-color: white; margin: 5% auto; padding: 20px; border-radius: 10px; width: 90%; max-width: 600px; }
        .modal-image { max-width: 100%; height: auto; border-radius: 10px; margin-bottom: 20px; }
        .close { color: #aaa; float: left; font-size: 28px; font-weight: bold; cursor: pointer; }
        .close:hover { color: black; }
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
                        <th>رسید</th>
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

    <!-- Modal for Receipt Image -->
    <div id="receiptModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeReceiptModal()">&times;</span>
            <h2>📷 رسید پرداخت</h2>
            <img id="receiptImage" class="modal-image" src="" alt="Receipt">
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

        function showReceipt(imageSrc) {
            const modal = document.getElementById('receiptModal');
            const img = document.getElementById('receiptImage');
            img.src = imageSrc;
            modal.style.display = 'block';
        }

        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('receipt-btn')) {
                const paymentId = e.target.getAttribute('data-image');
                fetch(`/admin/payment/${paymentId}/image`)
                    .then(res => res.json())
                    .then(data => {
                        if (data.image) {
                            showReceipt(data.image);
                        } else {
                            alert('❌ عکس در دسترس نیست');
                        }
                    })
                    .catch(err => alert('❌ خطا: ' + err));
            }
        });

        function closeReceiptModal() {
            document.getElementById('receiptModal').style.display = 'none';
        }

        window.onclick = function(event) {
            const modal = document.getElementById('receiptModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
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
                
                <div class="form-group">
                    <label>🔢 ID عددی تلگرام ادمین (برای شناخت خودکار)</label>
                    <input type="number" id="admin_numeric_id" value="{{ admin_numeric_id if admin_numeric_id != 'لم تعیین نشده' else '' }}" placeholder="مثال: 1234567890" inputmode="numeric">
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
                
                <h2 style="color: #333; margin-bottom: 20px; font-size: 18px;">📢 عضویت اجباری (اختیاری)</h2>
                
                <div class="form-group">
                    <label>
                        <input type="checkbox" id="require_subscription" style="width: auto; cursor: pointer; margin-left: 8px;">
                        فعال‌کردن عضویت اجباری در کانال
                    </label>
                </div>
                
                <div class="form-group">
                    <label>نام کانال (برای عضویت اجباری)</label>
                    <input type="text" id="subscription_channel" placeholder="مثال: @dragon_bot یا dragon_bot">
                </div>
                
                <p style="font-size: 12px; color: #666; margin-top: 10px;">
                    💡 اگر عضویت اجباری فعال باشد، کاربران قبل از استفاده باید در این کانال عضو شوند.
                </p>
                
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
        // ✅ مقداردهی اولیه برای عضویت اجباری
        window.onload = function() {
            document.getElementById('require_subscription').checked = {{ require_subscription|lower }};
            document.getElementById('subscription_channel').value = '{{ subscription_channel }}';
        };

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
                numeric_id: parseInt(document.getElementById('admin_numeric_id').value) || null,
                gem_price_toman: parseInt(document.getElementById('gem_price').value),
                minimum_gems_activate: parseInt(document.getElementById('min_gems').value),
                gems_per_hour: parseInt(document.getElementById('gems_per_hour').value),
                bank_card_number: document.getElementById('bank_card').value,
                bank_account_name: document.getElementById('bank_name').value,
                require_subscription: document.getElementById('require_subscription').checked,
                subscription_channel: document.getElementById('subscription_channel').value
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
        LIST_STATES = {}  # ✅ برای ردگیری state اضافه کردن/حذف لیست‌ها
        ACTIVE_BETS = {}  # {group_id: bet_id}

        @bot.on(events.NewMessage(pattern='/adminid'))
        async def set_admin_id_handler(event):
            """Set admin numeric ID"""
            sender = await event.get_sender()
            user_id = sender.id
            
            admin_db = Admin.objects.first()
            
            if not admin_db:
                await event.respond("❌ ادمین یافت نشد. لطفا ابتدا پنل админа را فعال کنید.")
                return
            
            # Check if this person can set admin ID (they must have correct username or be the admin)
            username = sender.username or ""
            if admin_db.username.lower() != username.lower() and Config.ADMIN_USERNAME.lower() != username.lower():
                await event.respond("❌ شما اجازه ندارید ID ادمین را تعیین کنید.")
                return
            
            # Set admin numeric ID
            admin_db.telegram_id = user_id
            admin_db.save()
            
            await event.respond(
                f"✅ **ID ادمین تنظیم شد:**\n\n"
                f"🔐 **ID عددی:** {user_id}\n"
                f"👤 **نام کاربری:** {admin_db.username}\n\n"
                f"حالا ربات شما را می‌شناسد! 🎉"
            )

        @bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            try:
                sender = await event.get_sender()
                user_id = sender.id
                username = sender.username or ""

                admin_db = Admin.objects.first()
                is_admin = False
                admin_numeric_id = None
                
                # بررسی ادمین بودن
                if admin_db:
                    admin_numeric_id = admin_db.telegram_id
                    if admin_db.telegram_id == user_id:
                        is_admin = True
                    elif admin_db.username.lower() == username.lower() or Config.ADMIN_USERNAME.lower() == username.lower():
                        is_admin = True
                        admin_db.telegram_id = user_id
                        admin_numeric_id = user_id
                        admin_db.save()

                # بررسی عضویت اجباری
                if admin_db and admin_db.settings.require_subscription and admin_db.settings.subscription_channel:
                    channel_name = admin_db.settings.subscription_channel
                    try:
                        # چک کردن عضویت در کانال
                        user_in_channel = False
                        try:
                            channel = await bot.get_entity(channel_name)
                            participant = await bot(functions.channels.GetParticipantRequest(channel, user_id))
                            user_in_channel = True
                        except:
                            user_in_channel = False
                        
                        if not user_in_channel:
                            # اگر متعلق نیست، دکمه عضویت نشان بده
                            buttons = [
                                [Button.url('✅ عضویت در کانال', f'https://t.me/{channel_name.lstrip("@")}')],
                                [Button.inline('✔️ تأیید عضویت', b'check_subscription')]
                            ]
                            text = (
                                f"👋 سلام {sender.first_name or 'دوست'}!\n\n"
                                f"برای استفاده از ربات، ابتدا باید در کانال ما عضو شوید.\n\n"
                                f"📢 **کانال:**\n"
                                f"@{channel_name.lstrip('@')}\n\n"
                                f"پس از عضویت، روی دکمه بالا بزنید."
                            )
                            await event.respond(text, buttons=buttons)
                            return
                    except Exception as e:
                        print(f"[!] خطا در بررسی عضویت: {e}")

                # تشخیص وضعیت کاربر
                user_db = User.objects(telegram_id=user_id).first()
                if not user_db:
                    # کاربر جدید - ابتدا باید زبان انتخاب کند
                    buttons = []
                    for lang_code, lang_name in LANGUAGES.items():
                        buttons.append([Button.inline(lang_name, f'lang_{lang_code}')])
                    
                    text = "🗣️ لطفاً زبان خود را انتخاب کنید / Please select your language:"
                    await event.respond(text, buttons=buttons)
                    return
                
                # اگر کاربر قبلاً زبان انتخاب نکرده، درخواست کن
                if not hasattr(user_db, 'language') or not user_db.language:
                    buttons = []
                    for lang_code, lang_name in LANGUAGES.items():
                        buttons.append([Button.inline(lang_name, f'lang_{lang_code}')])
                    
                    text = "🗣️ لطفاً زبان خود را انتخاب کنید / Please select your language:"
                    await event.respond(text, buttons=buttons)
                    return
                
                is_authenticated = user_db and user_db.is_authenticated

                # دکمه‌های ادمین
                if is_admin:
                    domain = "https://dark-self.onrender.com/auth/admin/login" 
                    buttons = [
                        [Button.url('🌐 پنل مدیریت ادمین', domain)],
                        [Button.inline('🚀 فعال‌سازی سلف (رایگان)', b'admin_activate_self')],
                        [Button.inline('📣 پیام همگانی', b'admin_broadcast')],
                        [Button.inline('📊 مشاهده آمار', b'admin_stats')]
                    ]
                    text = (
                        f"👑 **سلام ادمین!** (ID: {user_id})\n\n"
                        f"🎛️ **دستورات موجود:**\n"
                        f"• 🌐 پنل مدیریتی کامل\n"
                        f"• 🚀 فعال‌سازی سلف رایگان\n"
                        f"• 📣 ارسال پیام به تمام کاربران\n"
                        f"• 🎰 سیستم قمار در گروه‌ها\n"
                        f"• 📊 آمار کاربران\n\n"
                        f"**برای تنظیم ID ادمین:**\n`/adminid` را دستور بدهید\n"
                        f"(فقط یک بار برای شناخت خودکار ربات)"
                    )
                # دکمه‌های کاربران احراز شده (سلف فعال)
                elif is_authenticated:
                    buttons = [
                        [Button.inline('🚀 پنل قابلیت‌های سلف', b'self_panel')],
                        [Button.inline('💎 خریدن جم', b'buy_gems')],
                        [Button.inline('🎁 انتقال جم', b'transfer_gems')],
                        [Button.inline('📊 موجودی', b'balance')]
                    ]
                    text = (
                        f"✅ **سلام {sender.first_name or 'دوست'}!** سلف شما فعال است.\n\n"
                        f"💎 **موجودی:** {user_db.gems} جم\n\n"
                        f"📋 **گزینه‌های موجود:**\n"
                        f"🚀 پنل قابلیت‌های سلف\n"
                        f"💎 خریدن جم\n"
                        f"🎁 انتقال جم به دوستان\n\n"
                        f"**نکات:**\n"
                        f"• از دستور `bet X` در گروه‌ها برای قمار استفاده کنید\n"
                        f"• دستور خالی (Enter) مجدد برای دیدن موجودی جم"
                    )
                # دکمه‌های کاربران pending (فقط /start زده اند)
                else:
                    buttons = [
                        [Button.inline('💎 خریدن جم', b'buy_gems')],
                        [Button.inline('🚀 فعال‌سازی سلف', b'activate_self')],
                        [Button.inline('🎁 انتقال جم', b'transfer_gems')],
                        [Button.inline('📊 موجودی', b'balance')]
                    ]
                    text = (
                        f"👋 **سلام {sender.first_name or 'دوست'}!** به Dragon Self Bot خوش آمدید.\n\n"
                        f"💎 **موجودی:** {user_db.gems} جم\n\n"
                        f"📋 **گزینه‌های موجود:**\n"
                        f"💎 خریدن جم\n"
                        f"🚀 فعال‌سازی سلف\n"
                        f"🎁 انتقال جم به دوستان\n\n"
                        f"**نکات:**\n"
                        f"• پس از خریدن جم می‌توانید سلف را فعال کنید\n"
                        f"• دستور خالی (Enter) مجدد برای دیدن موجودی جم"
                    )

                await event.respond(text, buttons=buttons)
                print(f"✅ /start response sent to user {user_id} (Admin: {is_admin})")
            
            except Exception as e:
                print(f"❌ Error in /start handler: {e}")
                try:
                    await event.respond(f"❌ خطا در /start: {e}")
                except:
                    pass

        # ============ CALLBACK HANDLERS ============

        # ============ LANGUAGE SELECTION CALLBACKS ============
        @bot.on(events.CallbackQuery(data=b'lang_fa'))
        async def lang_fa_callback(event):
            """انتخاب فارسی"""
            await set_language(event, 'fa')

        @bot.on(events.CallbackQuery(data=b'lang_en'))
        async def lang_en_callback(event):
            """Select English"""
            await set_language(event, 'en')

        @bot.on(events.CallbackQuery(data=b'lang_ru'))
        async def lang_ru_callback(event):
            """Выберите русский"""
            await set_language(event, 'ru')

        @bot.on(events.CallbackQuery(data=b'lang_ar'))
        async def lang_ar_callback(event):
            """اختر العربية"""
            await set_language(event, 'ar')

        @bot.on(events.CallbackQuery(data=b'lang_de'))
        async def lang_de_callback(event):
            """Wählen Sie Deutsch"""
            await set_language(event, 'de')

        async def set_language(event, lang_code):
            """تعیین زبان و ذخیره‌سازی"""
            user_id = event.sender_id
            sender = await event.get_sender()
            admin_db = Admin.objects.first()
            
            # ایجاد یا بروزرسانی کاربر
            user_db = User.objects(telegram_id=user_id).first()
            if not user_db:
                try:
                    user_db = User(
                        telegram_id=user_id,
                        admin_id=str(admin_db.id) if admin_db else 'default',
                        phone_number=sender.phone or "",
                        username=sender.username or "",
                        first_name=sender.first_name or "",
                        language=lang_code,  # ✅ زبان ذخیره شد
                        is_authenticated=False
                    )
                    user_db.save()
                except Exception as e:
                    await event.answer(f"❌ خطا: {e}")
                    return
            else:
                user_db.language = lang_code
                user_db.save()
            
            await event.delete()
            
            # نمایش منوی اصلی
            lang_display = {
                'fa': '🇮🇷 فارسی',
                'en': '🇬🇧 English',
                'ru': '🇷🇺 Русский',
                'ar': '🇸🇦 العربية',
                'de': '🇩🇪 Deutsch'
            }
            
            text = f"✅ **زبان انتخاب شد:** {lang_display.get(lang_code, lang_code)}\n\n"
            text += get_text(lang_code, 'welcome').format(name=sender.first_name or 'دوست')
            
            buttons = [
                [Button.inline(get_text(lang_code, 'manage_lists'), b'manage_lists')],
                [Button.inline(get_text(lang_code, 'settings'), b'user_settings')],
                [Button.inline('💎 ' + get_text(lang_code, 'settings').replace('⚙️ ', ''), b'buy_gems')],
            ]
            
            await event.respond(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'check_subscription'))
        async def check_subscription_callback(event):
            """✅ بررسی عضویت اجباری و ادامه یا بازگشت"""
            user_id = event.sender_id
            sender = await event.get_sender()
            admin_db = Admin.objects.first()
            
            if not admin_db or not admin_db.settings.require_subscription:
                # عضویت اجباری غیر فعال است
                await event.answer('✅ عضویت اجباری غیرفعال است!')
                return
            
            channel_name = admin_db.settings.subscription_channel
            if not channel_name:
                await event.answer('❌ کانال تعیین نشده است!')
                return
            
            try:
                # بررسی عضویت کاربر در کانال
                user_in_channel = False
                try:
                    channel = await bot.get_entity(channel_name)
                    participant = await bot(functions.channels.GetParticipantRequest(channel, user_id))
                    user_in_channel = True
                except:
                    user_in_channel = False
                
                if user_in_channel:
                    # کاربر عضو است - بازگشت به منوی اصلی
                    await event.delete()
                    
                    # ایجاد کاربر در دیتابیس
                    user_db = User.objects(telegram_id=user_id).first()
                    if not user_db:
                        try:
                            user_db = User(
                                telegram_id=user_id,
                                admin_id=str(admin_db.id) if admin_db else 'default',
                                phone_number=sender.phone or "",
                                username=sender.username or "",
                                first_name=sender.first_name or "",
                                is_authenticated=False
                            )
                            user_db.save()
                        except:
                            pass
                    
                    # ارسال منوی اصلی
                    buttons = [
                        [Button.inline('💎 خریدن جم', b'buy_gems')],
                        [Button.inline('🚀 فعال‌سازی سلف', b'activate_self')],
                        [Button.inline('🎁 انتقال جم', b'transfer_gems')],
                        [Button.inline('📊 موجودی', b'balance')]
                    ]
                    text = (
                        f"✅ **خوش آمدید {sender.first_name or 'دوست'}!**\n\n"
                        f"🎉 عضویت شما تأیید شد.\n\n"
                        f"💎 **موجودی:** {user_db.gems if user_db else 0} جم\n\n"
                        f"📋 **گزینه‌های موجود:**\n"
                        f"💎 خریدن جم\n"
                        f"🚀 فعال‌سازی سلف\n"
                        f"🎁 انتقال جم به دوستان"
                    )
                    await event.respond(text, buttons=buttons)
                else:
                    # هنوز عضو نشده است
                    await event.answer('❌ ابتدا در کانال عضو شوید، سپس دوباره تلاش کنید!', alert=True)
            except Exception as e:
                print(f"[!] خطا در بررسی عضویت: {e}")
                await event.answer(f'❌ خطای سیستم: {str(e)[:50]}', alert=True)

        # ============ LIST MANAGEMENT CALLBACKS ============
        @bot.on(events.CallbackQuery(data=b'manage_lists'))
        async def manage_lists_callback(event):
            """📋 مدیریت لیست‌های دشمن/کراش/دوست"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            
            if not user_db:
                await event.answer('❌ کاربر پیدا نشد!')
                return
            
            lang = user_db.language or 'fa'
            text = f"📋 **{get_text(lang, 'manage_lists')}**\n\n"
            text += get_text(lang, 'welcome').split('!')[0] + "!"
            
            buttons = [
                [Button.inline('👿 ' + get_text(lang, 'enemy_list'), b'enemy_list_menu')],
                [Button.inline('💕 ' + get_text(lang, 'crush_list'), b'crush_list_menu')],
                [Button.inline('👥 ' + get_text(lang, 'friend_list'), b'friend_list_menu')],
                [Button.inline(get_text(lang, 'back'), b'lang_' + lang)]
            ]
            
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'enemy_list_menu'))
        async def enemy_list_menu(event):
            """👿 منوی لیست دشمن"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            lang = user_db.language or 'fa'
            
            enemies = EnemyList.objects(user_id=user_id).all()
            text = f"👿 **{get_text(lang, 'enemy_list')}**\n\n"
            text += f"📊 {len(enemies)} دشمن ثبت‌شده\n\n"
            
            for enemy in enemies:
                status = '✅' if enemy.is_enabled else '❌'
                text += f"{status} @{enemy.target_username} (ID: {enemy.target_id})\n"
            
            buttons = [
                [Button.inline(get_text(lang, 'add_enemy'), b'add_enemy_prompt')],
                [Button.inline(get_text(lang, 'remove_enemy'), b'remove_enemy_prompt')],
                [Button.inline(get_text(lang, 'back'), b'manage_lists')]
            ]
            
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'crush_list_menu'))
        async def crush_list_menu(event):
            """💕 منوی لیست کراش"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            lang = user_db.language or 'fa'
            
            crushes = CrushList.objects(user_id=user_id).all()
            text = f"💕 **{get_text(lang, 'crush_list')}**\n\n"
            text += f"📊 {len(crushes)} کراش ثبت‌شده\n\n"
            
            for crush in crushes:
                status = '✅' if crush.is_enabled else '❌'
                text += f"{status} @{crush.target_username} (ID: {crush.target_id})\n"
            
            buttons = [
                [Button.inline(get_text(lang, 'add_crush'), b'add_crush_prompt')],
                [Button.inline(get_text(lang, 'remove_crush'), b'remove_crush_prompt')],
                [Button.inline(get_text(lang, 'back'), b'manage_lists')]
            ]
            
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'friend_list_menu'))
        async def friend_list_menu(event):
            """👥 منوی لیست دوستان"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            lang = user_db.language or 'fa'
            
            friends = FriendList.objects(user_id=user_id).all()
            text = f"👥 **{get_text(lang, 'friend_list')}**\n\n"
            text += f"📊 {len(friends)} دوست ثبت‌شده\n\n"
            
            for friend in friends:
                status = '✅' if friend.is_enabled else '❌'
                text += f"{status} @{friend.target_username} (ID: {friend.target_id})\n"
            
            buttons = [
                [Button.inline(get_text(lang, 'add_friend'), b'add_friend_prompt')],
                [Button.inline(get_text(lang, 'remove_friend'), b'remove_friend_prompt')],
                [Button.inline(get_text(lang, 'back'), b'manage_lists')]
            ]
            
            await event.edit(text, buttons=buttons)

        # ============ LANGUAGE SETTINGS ============
        @bot.on(events.CallbackQuery(data=b'user_settings'))
        async def user_settings_callback(event):
            """⚙️ تنظیمات کاربر"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            lang = user_db.language or 'fa'
            
            text = f"⚙️ **{get_text(lang, 'settings')}**\n\n"
            text += f"🗣️ {get_text(lang, 'language_settings')}:\n"
            text += f"**{LANGUAGES.get(lang, lang)}**"
            
            buttons = []
            for lang_code, lang_name in LANGUAGES.items():
                buttons.append([Button.inline(lang_name, f'change_lang_{lang_code}')])
            buttons.append([Button.inline(get_text(lang, 'back'), b'manage_lists')])
            
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery())
        async def change_language_handler(event):
            """تغییر زبان"""
            if event.data.startswith(b'change_lang_'):
                lang_code = event.data.decode().split('_')[2]
                user_id = event.sender_id
                user_db = User.objects(telegram_id=user_id).first()
                
                if user_db:
                    user_db.language = lang_code
                    user_db.save()
                    
                    await event.answer(f"✅ {LANGUAGES.get(lang_code, lang_code)}")
                    
                    text = f"⚙️ **{get_text(lang_code, 'settings')}**\n\n"
                    text += f"🗣️ {get_text(lang_code, 'language_settings')}:\n"
                    text += f"**{LANGUAGES.get(lang_code, lang_code)}**"
                    
                    buttons = []
                    for lc, ln in LANGUAGES.items():
                        buttons.append([Button.inline(ln, f'change_lang_{lc}')])
                    buttons.append([Button.inline(get_text(lang_code, 'back'), b'manage_lists')])
                    
                    await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'self_panel'))
        async def self_panel_callback(event):
            """پنل قابلیت‌های سلف"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            
            if not user_db or not user_db.is_authenticated:
                await event.answer('❌ شما ابتدا باید سلف را فعال کنید!', alert=True)
                return
            
            # وضعیت features
            time_status = "✅" if user_db.time_enabled else "❌"
            bio_time_status = "✅" if user_db.bio_time_enabled else "❌"
            bio_date_status = "✅" if user_db.bio_date_enabled else "❌"
            anti_login = "✅" if user_db.anti_login_enabled else "❌"
            copy_profile = "✅" if user_db.copy_profile_enabled else "❌"
            enemy_enabled = "✅" if user_db.enemy_list_enabled else "❌"
            friend_enabled = "✅" if user_db.friend_list_enabled else "❌"
            
            features = (
                "🎛 **پنل قابلیت‌های سلف شامل:**\n\n"
                "⏰ **ساعت و تاریخ:** {}\n"
                "🛡 **محافظت ورود:** {} | 👤 **کپی پروفایل:** {}\n"
                "💀 **لیست دشمن:** {} | 💚 **لیست دوست:** {}\n"
                "💎 **موجودی:** {} جم\n\n"
                "👇 **برای انتخاب یک بخش دکمه را بزنید:**"
            ).format(time_status, anti_login, copy_profile, enemy_enabled, friend_enabled, user_db.gems)
            
            buttons = [
                [Button.inline('⏰ ساعت و تاریخ', b'manage_time'),
                 Button.inline('📝 فرمت و متن', b'manage_text')],
                [Button.inline('🔒 قفل‌های رسانه', b'manage_locks'),
                 Button.inline('⏳ وضعیت خودکار', b'manage_status')],
                [Button.inline('🌍 ترجمه خودکار', b'manage_translation')],
                [Button.inline('🛡 محافظت و امنیت', b'security_panel'),
                 Button.inline('🛠 ابزار و مدیریت', b'tools_panel')],
                [Button.inline('💀 دشمن', b'enemy_panel'),
                 Button.inline('💚 دوست', b'friend_panel'),
                 Button.inline('💕 کراش', b'crush_panel')],
                [Button.inline('📋 مدیریت لیست‌ها', b'manage_lists'),
                 Button.inline('💎 فروشگاه جم', b'gem_shop')],
                [Button.inline('⚙️ تنظیمات', b'user_settings'),
                 Button.inline('🏠 خانه', b'back_start')]
            ]
            
            await event.edit(features, buttons=buttons)

        # ============ SECURITY & PROTECTION PANEL ============
        @bot.on(events.CallbackQuery(data=b'security_panel'))
        async def security_panel_callback(event):
            """🛡 محافظت و امنیت"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            
            anti_login = "✅ فعال" if user_db.anti_login_enabled else "❌ غیرفعال"
            copy_profile = "✅ فعال" if user_db.copy_profile_enabled else "❌ غیرفعال"
            
            text = (
                "🛡 **محافظت و امنیت:**\n\n"
                f"🔐 **محافظت ورود:** {anti_login}\n"
                f"👤 **کپی پروفایل:** {copy_profile}\n\n"
                "**دستورات:**\n"
                "`نتی لوگین روشن` - فعال‌کردن محافظت\n"
                "`نتی لوگین خاموش` - غیرفعال‌کردن محافظت\n\n"
                "`کپی روشن` - شروع کپی پروفایل\n"
                "`کپی خاموش` - بازیابی پروفایل اصلی"
            )
            
            buttons = [
                [Button.inline('🔐 محافظت ورود', b'anti_login_toggle'),
                 Button.inline('👤 کپی پروفایل', b'copy_profile_help')],
                [Button.inline('🏠 بازگشت', b'self_panel')]
            ]
            
            await event.edit(text, buttons=buttons)
        
        @bot.on(events.CallbackQuery(data=b'anti_login_toggle'))
        async def anti_login_toggle_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            user_db.anti_login_enabled = not user_db.anti_login_enabled
            user_db.save()
            status = "✅ فعال" if user_db.anti_login_enabled else "❌ غیرفعال"
            await event.answer(f'محافظت ورود {status}', alert=True)
            await security_panel_callback(event)
        
        @bot.on(events.CallbackQuery(data=b'copy_profile_help'))
        async def copy_profile_help(event):
            text = (
                "👤 **راهنمای کپی پروفایل:**\n\n"
                "1️⃣ روی پروفایل کاربر مورد نظر بروید\n"
                "2️⃣ دستور `کپی روشن` را ارسال کنید\n"
                "3️⃣ انتظر تا پروفایل شما کپی شود\n"
                "4️⃣ برای بازیابی: `کپی خاموش`\n\n"
                "⚠️ **توجه:** نام و تصویر پروفایل کپی می‌شود"
            )
            buttons = [[Button.inline('🏠 بازگشت', b'security_panel')]]
            await event.edit(text, buttons=buttons)

        # ============ TOOLS & MANAGEMENT PANEL ============
        @bot.on(events.CallbackQuery(data=b'tools_panel'))
        async def tools_panel_callback(event):
            """🛠 ابزار و مدیریت"""
            text = (
                "🛠 **ابزار و مدیریت:**\n\n"
                "📋 **دستورات موجود:**\n"
                "`تگ` - تگ تمام اعضای گروه\n"
                "`تگ ادمین ها` - تگ ادمین‌های گروه\n"
                "`شماره من` - نمایش شماره تلفن\n"
                "`دانلود` - دانلود فایل (ریپلای)\n"
                "`بن` - بن کاربر (ریپلای)\n"
                "`پین` - پین پیام (ریپلای)\n"
                "`آن پین` - آن‌پین آخرین پیام\n"
                "`اسپم [متن] [تعداد]` - ارسال تکراری\n"
                "`فلود [متن] [تعداد]` - فلود سریع\n"
                "`ping` - بررسی سرعت اتصال"
            )
            buttons = [[Button.inline('🏠 بازگشت', b'self_panel')]]
            await event.edit(text, buttons=buttons)

        # ============ ENEMY LIST PANEL ============
        @bot.on(events.CallbackQuery(data=b'enemy_panel'))
        async def enemy_panel_callback(event):
            """💀 لیست دشمن"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            enemy_count = EnemyList.objects(user_id=user_id).count()
            enemy_status = "✅ فعال" if user_db.enemy_list_enabled else "❌ غیرفعال"
            
            text = (
                "💀 **لیست دشمن:**\n\n"
                f"📊 **تعداد دشمن:** {enemy_count}\n"
                f"⚔️ **وضعیت:** {enemy_status}\n\n"
                "**دستورات:**\n"
                "`دشمن روشن` / `دشمن خاموش` - فعال/غیرفعال\n"
                "`تنظیم دشمن` - اضافه کردن (ریپلای)\n"
                "`حذف دشمن` - حذف کردن (ریپلای)\n"
                "`پاکسازی لیست دشمن` - پاک کردن همه\n"
                "`لیست دشمن` - نمایش لیست\n"
                "`تنظیم متن دشمن [متن]` - تنظیم پاسخ\n"
                "`لیست متن دشمن` - نمایش پاسخ‌ها\n"
                "`حذف متن دشمن [عدد]` - حذف پاسخ"
            )
            
            buttons = [
                [Button.inline('✅ فعال/غیرفعال', b'enemy_toggle'),
                 Button.inline('📋 نمایش لیست', b'enemy_show_list')],
                [Button.inline('🏠 بازگشت', b'self_panel')]
            ]
            
            await event.edit(text, buttons=buttons)
        
        @bot.on(events.CallbackQuery(data=b'enemy_toggle'))
        async def enemy_toggle_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            user_db.enemy_list_enabled = not user_db.enemy_list_enabled
            user_db.save()
            status = "✅ فعال" if user_db.enemy_list_enabled else "❌ غیرفعال"
            await event.answer(f'وضعیت دشمن: {status}', alert=True)
            await enemy_panel_callback(event)
        
        @bot.on(events.CallbackQuery(data=b'enemy_show_list'))
        async def enemy_show_list_callback(event):
            user_id = event.sender_id
            enemies = EnemyList.objects(user_id=user_id).all()
            if enemies:
                text = "💀 **لیست دشمن‌های شما:**\n\n" + "\n".join([f"🔸 ID: `{e.target_id}`" for e in enemies])
            else:
                text = "❌ هیچ دشمنی در لیست نیست!"
            buttons = [[Button.inline('🏠 بازگشت', b'enemy_panel')]]
            await event.edit(text, buttons=buttons)

        # ============ FRIEND LIST PANEL ============
        @bot.on(events.CallbackQuery(data=b'friend_panel'))
        async def friend_panel_callback(event):
            """💚 لیست دوست"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            friend_count = FriendList.objects(user_id=user_id).count()
            friend_status = "✅ فعال" if user_db.friend_list_enabled else "❌ غیرفعال"
            
            text = (
                "💚 **لیست دوست:**\n\n"
                f"📊 **تعداد دوست:** {friend_count}\n"
                f"🤝 **وضعیت:** {friend_status}\n\n"
                "**دستورات:**\n"
                "`دوست روشن` / `دوست خاموش` - فعال/غیرفعال\n"
                "`تنظیم دوست` - اضافه کردن (ریپلای)\n"
                "`حذف دوست` - حذف کردن (ریپلای)\n"
                "`پاکسازی لیست دوست` - پاک کردن همه\n"
                "`لیست دوست` - نمایش لیست\n"
                "`تنظیم متن دوست [متن]` - تنظیم پاسخ\n"
                "`لیست متن دوست` - نمایش پاسخ‌ها\n"
                "`حذف متن دوست [عدد]` - حذف پاسخ"
            )
            
            buttons = [
                [Button.inline('✅ فعال/غیرفعال', b'friend_toggle'),
                 Button.inline('📋 نمایش لیست', b'friend_show_list')],
                [Button.inline('🏠 بازگشت', b'self_panel')]
            ]
            
            await event.edit(text, buttons=buttons)
        
        @bot.on(events.CallbackQuery(data=b'friend_toggle'))
        async def friend_toggle_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            user_db.friend_list_enabled = not user_db.friend_list_enabled
            user_db.save()
            status = "✅ فعال" if user_db.friend_list_enabled else "❌ غیرفعال"
            await event.answer(f'وضعیت دوست: {status}', alert=True)
            await friend_panel_callback(event)
        
        @bot.on(events.CallbackQuery(data=b'friend_show_list'))
        async def friend_show_list_callback(event):
            user_id = event.sender_id
            friends = FriendList.objects(user_id=user_id).all()
            if friends:
                text = "💚 **لیست دوستان شما:**\n\n" + "\n".join([f"🔸 ID: `{f.target_id}`" for f in friends])
            else:
                text = "❌ هیچ دوستی در لیست نیست!"
            buttons = [[Button.inline('🏠 بازگشت', b'friend_panel')]]
            await event.edit(text, buttons=buttons)

        # ============ CRUSH LIST PANEL ============
        @bot.on(events.CallbackQuery(data=b'crush_panel'))
        async def crush_panel_callback(event):
            """💕 لیست کراش"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            crush_count = CrushList.objects(user_id=user_id).count()
            
            text = (
                "💕 **لیست کراش:**\n\n"
                f"📊 **تعداد کراش:** {crush_count}\n\n"
                "**دستورات:**\n"
                "`افزودن کراش` - اضافه کردن (ریپلای)\n"
                "`حذف کراش` - حذف کردن (ریپلای)\n"
                "`لیست کراش` - نمایش لیست\n"
                "`تنظیم متن کراش [متن]` - تنظیم پیام\n"
                "`لیست متن کراش` - نمایش پیام‌ها\n"
                "`حذف متن کراش [عدد]` - حذف پیام"
            )
            
            buttons = [
                [Button.inline('📋 نمایش لیست', b'crush_show_list')],
                [Button.inline('🏠 بازگشت', b'self_panel')]
            ]
            
            await event.edit(text, buttons=buttons)
        
        @bot.on(events.CallbackQuery(data=b'crush_show_list'))
        async def crush_show_list_callback(event):
            user_id = event.sender_id
            crushes = CrushList.objects(user_id=user_id).all()
            if crushes:
                text = "💕 **لیست کراش‌های شما:**\n\n" + "\n".join([f"🔸 ID: `{c.target_id}`" for c in crushes])
            else:
                text = "❌ هیچ کراشی در لیست نیست!"
            buttons = [[Button.inline('🏠 بازگشت', b'crush_panel')]]
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'manage_time'))
        async def manage_time_callback(event):
            """مدیریت ساعت و بیو"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            
            if not user_db:
                await event.answer('❌ کاربر یافت نشد', alert=True)
                return
            
            time_status = "✅" if user_db.time_enabled else "❌"
            bio_time_status = "✅" if user_db.bio_time_enabled else "❌"
            bio_date_status = "✅" if user_db.bio_date_enabled else "❌"
            
            text = (
                "⏰ **مدیریت ساعت و تاریخ:**\n\n"
                f"• ساعت در نام: {time_status}\n"
                f"• ساعت در بیو: {bio_time_status}\n"
                f"• تاریخ در بیو: {bio_date_status}\n\n"
                "**دستورات:**\n" 
                "`ساعت روشن` / `ساعت خاموش` - ساعت در نام\n"
                "`ساعت بیو روشن` / `ساعت بیو خاموش` - ساعت در بیو\n"
                "`تاریخ بیو روشن` / `تاریخ بیو خاموش` - تاریخ در بیو\n"
                "`فونت ساعت` - تغییر قالب (0-5 انتخاب کنید)\n\n"
                "**فونت‌های موجود:**\n"
                "0️⃣ Normal: 12:34:56\n"
                "1️⃣ Subscript: ₁₂:₃₄:₅₆\n"
                "2️⃣ Superscript: ¹²:³⁴:⁵⁶\n"
                "3️⃣ Fullwidth: １２:３４:５６\n"
                "4️⃣ Bold: 𝟏𝟐:𝟑𝟒:𝟓𝟔\n"
                "5️⃣ Double-struck: 𝟙𝟚:𝟛𝟜:𝟝𝟞"
            )
            
            buttons = [
                [Button.inline('✅ ساعت روشن', b'time_enable'),
                 Button.inline('❌ ساعت خاموش', b'time_disable')],
                [Button.inline('✅ ساعت بیو', b'biotime_enable'),
                 Button.inline('❌ ساعت بیو خاموش', b'biotime_disable')],
                [Button.inline('✅ تاریخ بیو', b'biodate_enable'),
                 Button.inline('❌ تاریخ بیو خاموش', b'biodate_disable')],
                [Button.inline('🎨 تغییر فونت (0-5)', b'font_select')],
                [Button.inline('🏠 بازگشت', b'self_panel')]
            ]
            
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'time_enable'))
        async def time_enable_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_enabled = True
                user_db.save()
                await event.answer('✅ ساعت در نام فعال شد', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'time_disable'))
        async def time_disable_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_enabled = False
                user_db.save()
                await event.answer('❌ ساعت در نام غیرفعال شد', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'biotime_enable'))
        async def biotime_enable_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.bio_time_enabled = True
                user_db.save()
                await event.answer('✅ ساعت در بیو فعال شد', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'biotime_disable'))
        async def biotime_disable_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.bio_time_enabled = False
                user_db.save()
                await event.answer('❌ ساعت در بیو غیرفعال شد', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'biodate_enable'))
        async def biodate_enable_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.bio_date_enabled = True
                user_db.save()
                await event.answer('✅ تاریخ در بیو فعال شد', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'biodate_disable'))
        async def biodate_disable_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.bio_date_enabled = False
                user_db.save()
                await event.answer('❌ تاریخ در بیو غیرفعال شد', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'font_select'))
        async def font_select_callback(event):
            """انتخاب فونت ساعت"""
            font_text = "🎨 **انتخاب فونت ساعت:**\n\n"
            
            font_buttons = []
            for i in range(6):
                font_info = FONTS.get(i, {})
                font_buttons.append([Button.inline(
                    f"{i} - {font_info.get('name', 'Unknown')}: {font_info.get('example', '')}",
                    f'font_{i}'.encode()
                )])
            
            font_buttons.append([Button.inline('🏠 بازگشت', b'manage_time')])
            
            await event.edit(font_text, buttons=font_buttons)

        # Font selection callbacks - Static handlers
        @bot.on(events.CallbackQuery(data=b'font_0'))
        async def font_0_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_font = 0
                user_db.bio_time_font = 0
                user_db.save()
                await event.answer('✅ فونت به Normal تغییر یافت', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'font_1'))
        async def font_1_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_font = 1
                user_db.bio_time_font = 1
                user_db.save()
                await event.answer('✅ فونت به Subscript تغییر یافت', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'font_2'))
        async def font_2_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_font = 2
                user_db.bio_time_font = 2
                user_db.save()
                await event.answer('✅ فونت به Superscript تغییر یافت', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'font_3'))
        async def font_3_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_font = 3
                user_db.bio_time_font = 3
                user_db.save()
                await event.answer('✅ فونت به Fullwidth تغییر یافت', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'font_4'))
        async def font_4_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_font = 4
                user_db.bio_time_font = 4
                user_db.save()
                await event.answer('✅ فونت به Bold تغییر یافت', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'font_5'))
        async def font_5_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            if user_db:
                user_db.time_font = 5
                user_db.bio_time_font = 5
                user_db.save()
                await event.answer('✅ فونت به Double-struck تغییر یافت', alert=True)
            await manage_time_callback(event)

        @bot.on(events.CallbackQuery(data=b'balance'))
        async def balance_callback(event):
            """نمایش موجودی جم"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            sender = await event.get_sender()
            
            if not user_db:
                admin_db = Admin.objects.first()
                user_db = User(
                    telegram_id=user_id,
                    admin_id=str(admin_db.id) if admin_db else 'default',
                    phone_number=sender.phone or "",
                    username=sender.username or "",
                    first_name=sender.first_name or ""
                )
                user_db.save()
            
            status = "✅ سلف فعال" if user_db.is_authenticated else "⏳ منتظر فعال‌سازی"
            text = (
                f"💎 **موجودی جم شما:**\n\n"
                f"👤 **نام:** {sender.first_name}\n"
                f"💎 **جم:** {user_db.gems}\n"
                f"📊 **وضعیت:** {status}\n\n"
                f"دستورات:\n"
                f"• `bet X` - قمار در گروه‌ها"
            )
            
            await event.edit(text, buttons=[[Button.inline('🏠 بازگشت', b'back_start')]])

        @bot.on(events.CallbackQuery(data=b'admin_stats'))
        async def admin_stats_callback(event):
            """نمایش آمار کاربران برای ادمین"""
            total_users = len(User.objects.all())
            pending_users = len(User.objects(is_authenticated=False).all())
            auth_users = len(User.objects(is_authenticated=True).all())
            total_gems = sum([u.gems for u in User.objects.all()])
            pending_payments = len(Payment.objects(status='pending').all())
            
            stats = (
                f"📊 **آمار سیستم:**\n\n"
                f"📈 **کاربران:**\n"
                f"• کل: {total_users}\n"
                f"• در انتظار: {pending_users}\n"
                f"• فعال: {auth_users}\n\n"
                f"💎 **جم‌ها:**\n"
                f"• کل جم‌های سیستم: {total_gems}\n\n"
                f"💳 **پرداخت:**\n"
                f"• درخواست‌های معلق: {pending_payments}"
            )
            
            await event.edit(stats, buttons=[[Button.inline('🏠 بازگشت', b'back_start')]])

        @bot.on(events.CallbackQuery(data=b'gem_shop'))
        async def gem_shop_callback(event):
            """💎 فروشگاه جم - اطلاعات قیمت و محاسبات"""
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            
            if not user_db:
                await event.answer('❌ کاربر یافت نشد', alert=True)
                return
            
            lang = user_db.language or 'fa'
            
            # محاسبات جم
            monthly_gems = 24 * 30 * Config.GEMS_PER_HOUR  # 1440 gems
            cost_toman = monthly_gems * Config.GEM_PRICE_TOMAN
            cost_usd = cost_toman / Config.USD_TO_TOMAN
            
            if lang == 'fa':
                shop_text = f"""💎 **فروشگاه جم**

📊 **اطلاعات موردنیاز:**
• هر ساعت: {Config.GEMS_PER_HOUR} جم کم می‌شود
• ماهانه: {monthly_gems} جم نیاز است
• 📈 هزینه ماهانه: {cost_toman:,.0f} تومان

💵 **نرخ تبدیل ارز:**
1 USD = {Config.USD_TO_TOMAN:,} تومان
1 تومان = {1/Config.USD_TO_TOMAN:.0e} USD

🎯 **محاسبه ماهانه:**
برای ادامه سلف:
• {monthly_gems} جم موردنیاز
• {cost_usd:.2f} USD
• {cost_toman:,.0f} تومان

💳 **روش پرداخت:**
تماس با ادمین برای خریدن جم
"""
            else:
                shop_text = f"""💎 **Gem Shop**

📊 **Required Information:**
• Per hour: {Config.GEMS_PER_HOUR} gems decrease
• Monthly: {monthly_gems} gems needed
• 📈 Monthly cost: {cost_usd:.2f} USD

💵 **Currency Conversion:**
1 USD = {Config.USD_TO_TOMAN:,} Toman
1 Toman = {1/Config.USD_TO_TOMAN:.0e} USD

🎯 **Monthly Calculation:**
To continue self-bot:
• {monthly_gems} gems needed
• {cost_usd:.2f} USD
• {cost_toman:,.0f} Toman

💳 **Payment Method:**
Contact admin to buy gems
"""
            
            buttons = [
                [Button.inline(get_text(lang, 'back'), b'self_panel')]
            ]
            
            await event.edit(shop_text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'back_start'))
        async def back_start_callback(event):
            """بازگشت به /start"""
            await event.delete()
            sender = await event.get_sender()
            user_id = sender.id
            
            # اجرای مجدد start_handler
            class FakeEvent:
                async def get_sender(self):
                    return sender
                async def respond(self, text, buttons):
                    await event.client.send_message(user_id, text, buttons=buttons)
                    
            fake_event = FakeEvent()
            # فراخوان مجدد دستور /start
            await event.client.send_message(user_id, "🏠 بازگشت به منوی اصلی", buttons=[])
            # ارسال منوی اصلی
            admin_db = Admin.objects.first()
            is_admin = admin_db and admin_db.telegram_id == user_id
            user_db = User.objects(telegram_id=user_id).first()
            is_authenticated = user_db and user_db.is_authenticated
            
            if is_admin:
                domain = "https://dark-self.onrender.com/auth/admin/login"
                buttons = [
                    [Button.url('🌐 پنل مدیریت ادمین', domain)],
                    [Button.inline('🚀 فعال‌سازی سلف (رایگان)', b'admin_activate_self')],
                    [Button.inline('📣 پیام همگانی', b'admin_broadcast')],
                    [Button.inline('📊 مشاهده آمار', b'admin_stats')]
                ]
                text = f"👑 **سلام ادمین!**\n\n🎛️ **دستورات موجود** در بالا"
            elif is_authenticated:
                buttons = [
                    [Button.inline('🚀 پنل قابلیت‌های سلف', b'self_panel')],
                    [Button.inline('💎 خریدن جم', b'buy_gems')],
                    [Button.inline('📊 موجودی', b'balance')]
                ]
                text = f"✅ **سلام!** سلف شما فعال است"
            else:
                buttons = [
                    [Button.inline('💎 خریدن جم', b'buy_gems')],
                    [Button.inline('🚀 فعال‌سازی سلف', b'activate_self')],
                    [Button.inline('📊 موجودی', b'balance')]
                ]
                text = f"👋 **سلام!** خوش آمدید"
            
            await event.client.send_message(user_id, text, buttons=buttons)

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

        @bot.on(events.CallbackQuery(data=b'manage_text'))
        async def manage_text_callback(event):
            """مدیریت فرمت‌بندی متن"""
            text = (
                "📝 **فرمت‌بندی و ترجمه متن:**\n\n"
                "**دستورات:**\n"
                "`بولد روشن` / `بولد خاموش`\n"
                "`ایتالیک روشن` / `ایتالیک خاموش`\n"
                "`زیرخط روشن` / `زیرخط خاموش`\n"
                "`خط خورده روشن` / `خط خورده خاموش`\n"
                "`کد روشن` / `کد خاموش`\n"
                "`اسپویلر روشن` / `اسپویلر خاموش`\n\n"
                "** برای ترجمه:**\n"
                "`ترجمه` (ریپلای روی پیام)\n"
                "`انگلیسی روشن` / `انگلیسی خاموش`\n"
                "`چینی روشن` / `چینی خاموش`\n"
                "`روسی روشن` / `روسی خاموش`"
            )
            buttons = [[Button.inline('🏠 بازگشت', b'self_panel')]]
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'manage_locks'))
        async def manage_locks_callback(event):
            """مدیریت قفل‌های رسانه"""
            text = (
                "🔒 **قفل‌های رسانه (حذف خودکار):**\n\n"
                "**دستورات:**\n"
                "`قفل عکس روشن` / `قفل عکس خاموش`\n"
                "`قفل ویدیو روشن` / `قفل ویدیو خاموش`\n"
                "`قفل ویس روشن` / `قفل ویس خاموش`\n"
                "`قفل فایل روشن` / `قفل فایل خاموش`\n"
                "`قفل استیکر روشن` / `قفل استیکر خاموش`\n"
                "`قفل گیف روشن` / `قفل گیف خاموش`\n"
                "`قفل موزیک روشن` / `قفل موزیک خاموش`\n"
                "`قفل متن روشن` / `قفل متن خاموش`\n\n"
                "📌 این پیام‌ها خود کار حذف می‌شوند!"
            )
            buttons = [[Button.inline('🏠 بازگشت', b'self_panel')]]
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'manage_status'))
        async def manage_status_callback(event):
            """مدیریت وضعیت‌های خودکار"""
            text = (
                "⏳ **وضعیت‌های خودکار:**\n\n"
                "**دستورات:**\n"
                "`تایپ روشن` / `تایپ خاموش`\n"
                "`بازی روشن` / `بازی خاموش`\n"
                "`ویس روشن` / `ویس خاموش`\n"
                "`عکس روشن` / `عکس خاموش`\n"
                "`گیف روشن` / `گیف خاموش`\n"
                "`سین روشن` / `سین خاموش`\n\n"
                "این وضعیت‌ها در پس‌زمینه نمایش داده می‌شوند!"
            )
            buttons = [[Button.inline('🏠 بازگشت', b'self_panel')]]
            await event.edit(text, buttons=buttons)

        @bot.on(events.CallbackQuery(data=b'manage_translation'))
        async def manage_translation_callback(event):
            """مدیریت ترجمه خودکار"""
            text = (
                "🌍 **ترجمه خودکار:**\n\n"
                "**دستورات:**\n"
                "`انگلیسی روشن` / `انگلیسی خاموش` - ترجمه به انگلیسی\n"
                "`چینی روشن` / `چینی خاموش` - ترجمه به چینی\n"
                "`روسی روشن` / `روسی خاموش` - ترجمه به روسی\n\n"
                "**ترجمه دستی:**\n"
                "برای ترجمه پیام‌های شخص دیگر:\n"
                "`ترجمه` (ریپلای روی پیام)"
            )
            buttons = [[Button.inline('🏠 بازگشت', b'self_panel')]]
            await event.edit(text, buttons=buttons)

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
            
            # بررسی عضویت اجباری در کانال‌ها
            mandatory_channels = SubscriptionChannel.objects(is_mandatory=True).all()
            if mandatory_channels:
                not_subscribed = []
                for channel in mandatory_channels:
                    try:
                        # بررسی عضویت کاربر در کانال
                        user_entity = await bot.get_entity(channel.channel_id)
                        # اگر بتوانیم اطلاعات اعضا را بگیریم، کاربر عضو است
                        participants = await bot(functions.channels.GetParticipantRequest(user_entity, user_id))
                    except:
                        not_subscribed.append(f"@{getattr(user_entity, 'username', str(channel.channel_id))}")
                
                if not_subscribed:
                    channels_text = "\n".join([f"• {ch}" for ch in not_subscribed])
                    await event.answer(
                        f"❌ شما باید عضو کانال‌های زیر باشید:\n\n{channels_text}\n\nپس از عضویت دوباره تلاش کنید.",
                        alert=True
                    )
                    return
            
            if not user_db or user_db.gems < min_gems:
                remaining = min_gems - (user_db.gems if user_db else 0)
                await event.answer(
                    f"❌ جم کافی ندارید!\n\n"
                    f"جم فعلی: {user_db.gems if user_db else 0}\n"
                    f"جم مورد نیاز: {min_gems}\n"
                    f"جم باقی‌مانده: {remaining}\n\n"
                    f"درخواست می‌کنیم فروشگاه باید جم بخرید (دکمه 💎 خریدن جم)",
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

        @bot.on(events.CallbackQuery(data=b'transfer_gems'))
        async def transfer_gems_callback(event):
            user_id = event.sender_id
            user_db = User.objects(telegram_id=user_id).first()
            
            if not user_db or user_db.gems <= 0:
                await event.answer(
                    "❌ شما جم ندارید برای انتقال!",
                    alert=True
                )
                return
            
            await event.edit(
                "💎 **انتقال جم به دیگری**\n\n"
                f"جم فعلی شما: {user_db.gems}\n\n"
                "📝 لطفا **تعداد جem برای انتقال** را وارد کنید:\n\n"
                "⚠️ سپس پیام کاربری که می‌خواهید جم به او دهید را **ریپلای** کنید.",
                buttons=[Button.inline('❌ بازگشت', b'back_start')]
            )
            LOGIN_STATES[user_id] = {'step': 'transfer_gems_amount'}

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
                buttons.append([Button.inline('🎁 انتقال جم', b'transfer_gems')])
                text = "👋 **سلام! به Dragon Self Bot خوش آمدید.**"

            await event.edit(text, buttons=buttons)
            if user_id in LOGIN_STATES:
                del LOGIN_STATES[user_id]

        # ============ BETTING SYSTEM HANDLERS ============
        
        @bot.on(events.NewMessage(pattern=r'^bet\s+(\d+)$'))
        async def betting_handler(event):
            """Handle 'bet X' command in groups"""
            if event.is_private:
                await event.respond("❌ دستور قمار فقط در گروه‌ها کار می‌کند.")
                return
            
            sender = await event.get_sender()
            user_id = sender.id
            group_id = event.chat_id
            username = sender.first_name or "کاربر"
            
            # Parse bet amount
            import re
            match = re.match(r'^bet\s+(\d+)$', event.text.strip())
            if not match:
                return
            
            amount = int(match.group(1))
            
            # Check if user has enough gems
            user_db = User.objects(telegram_id=user_id).first()
            if not user_db or user_db.gems < amount:
                await event.respond(f"❌ {username}، شما جم کافی ندارید! جم دارید: {user_db.gems if user_db else 0}")
                return
            
            # Check if there's already an active bet in this group
            if group_id in ACTIVE_BETS:
                await event.respond("🔄 یک قمار فعال در حال حاضر در این گروه وجود دارد. صبر کنید تا تمام شود.")
                return
            
            # Create new bet
            import uuid
            bet_id = str(uuid.uuid4())[:8]
            
            bet = Bet(
                bet_id=bet_id,
                group_id=group_id,
                creator_id=user_id,
                creator_name=username,
                amount=amount,
                status='waiting'
            )
            bet.save()
            
            ACTIVE_BETS[group_id] = bet_id
            
            msg = await event.respond(
                f"🎰 **قمار شروع شد!**\n\n"
                f"👤 **سازنده:** {username}\n"
                f"💎 **مبلغ:** {amount} جم\n\n"
                f"⏳ **در انتظار شرکت‌کننده...**\n"
                f"برای پیوستن به قمار دکمه پایین را بزنید!",
                buttons=[[Button.inline('🎲 پیوستن به قمار', b'join_bet')]]
            )
            
            bet.message_id = msg.id
            bet.save()
            
            # Auto-delete bet after 60 seconds if no one joins
            await asyncio.sleep(60)
            bet_check = Bet.objects(bet_id=bet_id).first()
            if bet_check and bet_check.status == 'waiting':
                await event.respond(f"❌ قمار منقضی شد! بدون شرکت‌کننده.")
                Bet.objects(bet_id=bet_id).delete()
                if group_id in ACTIVE_BETS:
                    del ACTIVE_BETS[group_id]

        @bot.on(events.CallbackQuery(data=b'join_bet'))
        async def join_bet_callback(event):
            """Handle joining a bet"""
            joiner_id = event.sender_id
            joiner_name = (await event.get_sender()).first_name or "کاربر"
            group_id = event.chat_id
            
            # Find active bet in this group
            if group_id not in ACTIVE_BETS:
                await event.answer("❌ قمار فعالی وجود ندارد.", alert=True)
                return
            
            bet_id = ACTIVE_BETS[group_id]
            bet = Bet.objects(bet_id=bet_id).first()
            
            if not bet:
                await event.answer("❌ قمار پیدا نشد.", alert=True)
                if group_id in ACTIVE_BETS:
                    del ACTIVE_BETS[group_id]
                return
            
            # Check if joiner already created this bet
            if bet.creator_id == joiner_id:
                await event.answer("❌ نمی‌توانید به قمار خودتان بپیوندید!", alert=True)
                return
            
            # Check if joiner has enough gems
            joiner_db = User.objects(telegram_id=joiner_id).first()
            if not joiner_db or joiner_db.gems < bet.amount:
                await event.answer(f"❌ شما جم کافی ندارید! جم دارید: {joiner_db.gems if joiner_db else 0}", alert=True)
                return
            
            # Check if someone already joined
            if bet.joiner_id:
                await event.answer("❌ یک شخص دیگر قبلاً به این قمار پیوسته است!", alert=True)
                return
            
            # Add joiner to bet
            bet.joiner_id = joiner_id
            bet.joiner_name = joiner_name
            bet.status = 'active'
            bet.save()
            
            # Update message
            await event.edit(
                f"🎰 **قمار شروع شد!**\n\n"
                f"👤 **سازنده:** {bet.creator_name}\n"
                f"👤 **شرکت‌کننده:** {joiner_name}\n"
                f"💎 **مبلغ:** {bet.amount} جم\n\n"
                f"⏳ **درحال شمارش معکوس برای انتخاب برنده...**"
            )
            
            # Wait 5 seconds then randomly select winner
            await asyncio.sleep(5)
            
            import random
            winner_id = bet.creator_id if random.choice([True, False]) else bet.joiner_id
            loser_id = bet.joiner_id if winner_id == bet.creator_id else bet.creator_id
            
            winner_name = bet.creator_name if winner_id == bet.creator_id else bet.joiner_name
            loser_name = bet.joiner_name if winner_id == bet.creator_id else bet.creator_name
            
            # Calculate gems
            total_pool = bet.amount * 2
            commission = bet.commission
            winner_gems_earned = total_pool - commission
            
            # Update users
            creator_db = User.objects(telegram_id=bet.creator_id).first()
            joiner_db = User.objects(telegram_id=bet.joiner_id).first()
            
            if winner_id == bet.creator_id:
                creator_db.gems += winner_gems_earned
                joiner_db.gems -= bet.amount
            else:
                joiner_db.gems += winner_gems_earned
                creator_db.gems -= bet.amount
            
            creator_db.save()
            joiner_db.save()
            
            # Update bet record
            bet.winner_id = winner_id
            bet.loser_id = loser_id
            bet.status = 'completed'
            bet.winner_gems = winner_gems_earned
            bet.loser_gems_lost = bet.amount
            bet.completed_at = datetime.utcnow()
            bet.save()
            
            # Send result
            result_msg = (
                f"🎰 **نتیجه قمار:**\n\n"
                f"🏆 **برنده:** {winner_name}\n"
                f"💎 **جم دریافت‌شده:** {winner_gems_earned} (بعد از کارمزد {commission} جم)\n\n"
                f"😔 **بازنده:** {loser_name}\n"
                f"💔 **جم از دست‌رفته:** {bet.amount}\n\n"
                f"📊 **آمار:**\n• جم سازنده: {creator_db.gems}\n• جم شرکت‌کننده: {joiner_db.gems}"
            )
            
            await event.edit(result_msg)
            
            # Remove from active bets
            if group_id in ACTIVE_BETS:
                del ACTIVE_BETS[group_id]

        @bot.on(events.NewMessage())
        async def handle_empty_or_betting_message(event):
            """Handle empty messages to show gem balance"""
            if event.text and event.text.startswith('/'):
                return
            
            # If message is empty or just whitespace
            if not event.text or event.text.strip() == '':
                user_id = event.sender_id
                user_db = User.objects(telegram_id=user_id).first()
                
                if not user_db:
                    admin_db = Admin.objects.first()
                    user_db = User(
                        telegram_id=user_id,
                        admin_id=str(admin_db.id) if admin_db else 'default',
                        phone_number="",
                        username=""
                    )
                    user_db.save()
                
                sender = await event.get_sender()
                name = sender.first_name or "کاربر"
                
                await event.respond(
                    f"💎 **موجودی جم شما:**\n\n"
                    f"👤 **نام:** {name}\n"
                    f"💎 **جم:** {user_db.gems}\n\n"
                    f"دستورات:\n"
                    f"• `bet X` - شروع قمار (در گروه)\n"
                    f"• `/start` - بازگشت به منو اصلی"
                )
                return

        @bot.on(events.NewMessage())
        async def handle_login_steps(event):
            # ✅ چک کن که text موجود است
            if not event.text or event.text.startswith('/'): 
                return
            
            user_id = event.sender_id
            state = LOGIN_STATES.get(user_id)
            if not state: return

            # Handle Gem Transfer Amount
            if state['step'] == 'transfer_gems_amount':
                try:
                    transfer_amount = int(event.text.strip())
                    sender_db = User.objects(telegram_id=user_id).first()
                    
                    if not sender_db or sender_db.gems < transfer_amount:
                        await event.respond("❌ جم کافی ندارید برای انتقال!")
                        del LOGIN_STATES[user_id]
                        return
                    
                    if transfer_amount <= 0:
                        await event.respond("❌ تعداد جم باید بزرگتر از صفر باشد.")
                        return
                    
                    state['step'] = 'transfer_gems_target'
                    state['transfer_amount'] = transfer_amount
                    
                    await event.respond(
                        f"💎 **انتقال {transfer_amount} جم**\n\n"
                        f"حالا پیام کاربری که می‌خواهید جم به او دهید را **ریپلای** کنید.",
                        buttons=[Button.inline('❌ لغو', b'back_start')]
                    )
                except ValueError:
                    await event.respond("❌ لطفا یک عدد صحیح وارد کنید.")
                return
            
            # Handle Target User Reply for Transfer
            if state['step'] == 'transfer_gems_target':
                if not event.is_reply:
                    await event.respond("❌ لطفا پیام کاربری را که می‌خواهید جم به او دهید **ریپلای** کنید.")
                    return
                
                reply_msg = await event.get_reply_message()
                target_user_id = reply_msg.sender_id
                
                sender_db = User.objects(telegram_id=user_id).first()
                target_db = User.objects(telegram_id=target_user_id).first()
                
                if not target_db:
                    admin_db = Admin.objects.first()
                    target_db = User(
                        telegram_id=target_user_id,
                        admin_id=sender_db.admin_id if sender_db else (str(admin_db.id) if admin_db else 'default'),
                        phone_number="",
                        username=""
                    )
                    target_db.save()
                
                transfer_amount = state.get('transfer_amount', 0)
                
                # Transfer gems
                sender_db.gems -= transfer_amount
                target_db.gems += transfer_amount
                
                sender_db.save()
                target_db.save()
                
                await event.respond(
                    f"✅ **انتقال جم موفق!**\n\n"
                    f"📊 **مشخصات:**\n"
                    f"• جم انتقال‌یافته: {transfer_amount}\n"
                    f"• جم باقی‌مانده شما: {sender_db.gems}\n"
                    f"• جم دریافت‌کننده: {target_db.gems}"
                )
                
                # Notify target user
                try:
                    await bot.send_message(
                        target_user_id,
                        f"🎁 **هدیه جم دریافت کردید!**\n\n"
                        f"👤 فرستنده: `{sender_db.first_name}`\n"
                        f"💎 تعداد جم: {transfer_amount}\n"
                        f"📊 جم فعلی شما: {target_db.gems}\n\n"
                        f"دستور `/start` برای شروع!"
                    )
                except:
                    pass
                
                del LOGIN_STATES[user_id]
                return

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
            
            # Handle Payment Receipt - ONLY IMAGES ALLOWED
            if state['step'] == 'gem_confirmation':
                # ❌ اگر text بجائے عکس بفرستد
                if event.text and not event.photo:
                    await event.respond(
                        "❌ **لطفاً فقط عکس رسید را ارسال کنید!**\n\n"
                        "متن قابل قبول نیست. شما باید:\n"
                        "✅ عکس رسید را ارسال کنید\n\n"
                        "اگر لغو می‌خواهید دکمه اینجا کلیک کنید:",
                        buttons=[[Button.inline('❌ لغو و بازگشت', b'back_start')]]
                    )
                    return
                
                # ✅ اگر عکس ارسال کرد
                if event.photo:
                    import base64
                    
                    admin_db = Admin.objects.first()
                    user_db = User.objects(telegram_id=user_id).first()
                    if not user_db:
                        user_db = User(
                            telegram_id=user_id,
                            admin_id=str(admin_db.id) if admin_db else 'default',
                            phone_number="",
                            username="",
                            is_authenticated=False,
                            is_verified=False
                        )
                        user_db.save()  # ✅ ذخیره کاربر جدید
                    
                    # Download photo and convert to base64 with compression
                    base64_image = None
                    photo_data = None
                    try:
                        photo_data = await event.download_media(bytes)
                        print(f"📸 عکس دریافت شد: {len(photo_data)} بایت")
                        
                        # Compress image if it's too large
                        if len(photo_data) > 5 * 1024 * 1024:  # 5 MB
                            print("📸 فشرده سازی عکس بزرگ...")
                            try:
                                img = Image.open(io.BytesIO(photo_data))
                                # Reduce quality
                                img_compressed = io.BytesIO()
                                img.save(img_compressed, format='JPEG', quality=70, optimize=True)
                                photo_data = img_compressed.getvalue()
                                print(f"✅ عکس فشرده شد: {len(photo_data)} بایت")
                            except Exception as compress_err:
                                print(f"⚠️ خطا در فشرده سازی: {compress_err}")
                                # Use original if compression fails
                        
                        # Encode to base64
                        base64_image = base64.b64encode(photo_data).decode('utf-8')
                        print(f"✅ عکس به base64 تبدیل شد: {len(base64_image)} حرف")
                    except Exception as e:
                        print(f"❌ خطا در دانلود/فشرده سازی عکس: {e}")
                        await event.respond(f"❌ خطا در دانلود عکس:\n{e}\n\nلطفاً دوباره تلاش کنید.")
                        return
                    
                    if not base64_image:
                        await event.respond("❌ خطا: عکس خالی است. لطفاً دوباره تلاش کنید.")
                        return
                    
                    # Create payment with receipt (TTL will auto-delete after 7 days)
                    payment = Payment(
                        user_id=user_db.id,  # ✅ الآن user_db ذخیره شده است
                        gems=state['gem_amount'],
                        amount_toman=state['gem_price'],
                        receipt_image=base64_image,  # ✅ Base64 encoded image
                        status='pending',
                        created_at=datetime.utcnow()  # ✅ TTL will count from this
                    )
                    payment.save()
                    print(f"✅ پرداخت ایجاد شد با ID: {payment.id}, ۷ روز بعد خود کار حذف شود")
                    
                    # Send receipt to admin with preview
                    if admin_db and admin_db.telegram_id:
                        try:
                            sender = await event.get_sender()
                            admin_msg = (
                                f"📦 **رسید جدید برای تایید**\n\n"
                                f"👤 **کاربر:** {sender.first_name or 'نشناخته'}\n"
                                f"🆔 **ID:** {user_id}\n"
                                f"💎 **تعداد جم:** {state['gem_amount']}\n"
                                f"💰 **مبلغ:** {state['gem_price']:,} تومان\n"
                                f"📋 **شماره تراکنش:** `{str(payment.id)}`\n\n"
                                f"⏳ در انتظار تایید شما..."
                            )
                            await bot.send_message(admin_db.telegram_id, admin_msg)
                            if base64_image:
                                photo_io = io.BytesIO(photo_data)
                                await bot.send_file(
                                    admin_db.telegram_id,
                                    photo_io,
                                    caption="📷 رسید پرداخت"
                                )
                        except Exception as e:
                            print(f"❌ خطا در ارسال برای ادمین: {e}")
                    else:
                        print("❌ ادمین یا Telegram ID ادمین موجود نیست")
                    
                    await event.respond(
                        f"✅ **رسید با موفقیت دریافت شد!**\n\n"
                        f"📋 **شماره تراکنش:** `{str(payment.id)}`\n"
                        f"💎 **جم درخواست‌شده:** {state['gem_amount']}\n"
                        f"💰 **مبلغ:** {state['gem_price']:,} تومان\n\n"
                        f"📸 **عکس رسید:** ✅ ذخیره شد\n"
                        f"🔒 **حفظ داده‌ها:** 7 روز (خود کار حذف شود)\n\n"
                        f"⏳ **درحال انتظار تایید ادمین...**\n\n"
                        f"اگر جم دریافت کردید، می‌توانید دستور `/start` را دوباره ارسال کنید.",
                        buttons=[
                            [Button.inline('🏠 بازگشت به خانه', b'back_start')]
                        ]
                    )
                    del LOGIN_STATES[user_id]
                else:
                    # نه عکس، نه متن
                    await event.respond(
                        "❌ **فقط عکس رسید قابل قبول است!**\n\n"
                        "لطفاً عکس رسید پرداخت خود را ارسال کنید.",
                        buttons=[[Button.inline('❌ لغو و بازگشت', b'back_start')]]
                    )
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
                    admin_id=str(admin_db.id) if admin_db else 'default',
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
║                                                               ║
║  📍 Server: https://dark-self.onrender.com/                  ║
║  🚪 Login: https://dark-self.onrender.com//auth/admin/login  ║
║  👤 Default: admin / admin123                                ║
║                                                                ║
║  🗄️ Database: MongoDB Connected                                ║
║  🔄 Scheduler: APScheduler Active                              ║
║  💎 Payment: Toman-based Gem System                            ║
║  🌐 Telethon: Running Async Background Event Loop              ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Run Telethon event loop in a background thread so it doesn't block Flask
    telethon_thread = threading.Thread(target=run_telethon_loop)
    telethon_thread.daemon = True
    telethon_thread.start()
    
    # Run Flask Application
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
