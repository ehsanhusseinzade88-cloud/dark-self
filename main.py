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
    import time
    if user_id in _user_cache:
        cached_data, timestamp = _user_cache[user_id]
        if time.time() - timestamp < _cache_timeout:
            return cached_data
    user = User.objects(telegram_id=user_id).first()
    if user:
        _user_cache[user_id] = (user, __import__('time').time())
    return user

def invalidate_user_cache(user_id):
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
    if formats_dict.get('reverse'): text = text[::-1]
    if formats_dict.get('bold'): text = f'**{text}**'
    if formats_dict.get('italic'): text = f'__{text}__'
    if formats_dict.get('underline'): text = f'__<u>{text}</u>__'
    if formats_dict.get('strikethrough'): text = f'~~{text}~~'
    if formats_dict.get('monospace'): text = f'`{text}`'
    if formats_dict.get('spoiler'): text = f'||{text}||'
    if formats_dict.get('quote'): text = f'❝ {text} ❞'
    return text

def translate_text(text, target_lang='fa'):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_lang}&dt=t&q={text}"
        response = requests.get(url)
        if response.status_code == 200:
            return ''.join([sentence[0] for sentence in response.json()[0]])
    except Exception as e:
        print(f"Translation error: {e}")
    return text

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
    meta = {'collection': 'admins', 'indexes': ['username', 'telegram_id']}
    username = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    telegram_id = IntField(unique=True, sparse=True)
    is_active = BooleanField(default=True)
    settings = EmbeddedDocumentField(AdminSettings, default=AdminSettings)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class User(Document):
    meta = {'collection': 'users', 'indexes': ['telegram_id', 'phone_number', 'admin_id']}
    admin_id = StringField(default='default')
    telegram_id = IntField(unique=True, required=True)
    phone_number = StringField(default='')
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
    profile_backup = DictField(default={})
    forward_messages = DictField(default={})
    language = StringField(default='fa')
    language_selected = BooleanField(default=False)
    enemy_messages = ListField(StringField(), default=[])
    crush_messages = ListField(StringField(), default=[])
    friend_messages = ListField(StringField(), default=[])
    anti_login_enabled = BooleanField(default=False)
    enemy_list_enabled = BooleanField(default=False)
    friend_list_enabled = BooleanField(default=False)
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
            {'fields': [('created_at', 1)], 'expireAfterSeconds': 604800}
        ]
    }
    user_id = IntField(required=True)
    gems = IntField(required=True)
    amount_toman = IntField(required=True)
    receipt_image = StringField()
    receipt_image_url = StringField()
    approved_image = StringField()
    auto_delete_at = DateTimeField()
    status = StringField(default='pending')
    approved_by_admin = IntField()
    approval_note = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    approved_at = DateTimeField()
    is_permanent = BooleanField(default=False)

class DiscountCode(Document):
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

class UserBlock(Document):
    meta = {'collection': 'user_blocks', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)

class EnemyList(Document):
    meta = {'collection': 'enemy_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    custom_messages = ListField(StringField(), default=[])
    created_at = DateTimeField(default=datetime.utcnow)

class FriendList(Document):
    meta = {'collection': 'friend_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    custom_messages = ListField(StringField(), default=[])
    created_at = DateTimeField(default=datetime.utcnow)

class CrushList(Document):
    meta = {'collection': 'crush_lists', 'indexes': ['user_id', 'target_id']}
    user_id = IntField(required=True)
    target_id = IntField(required=True)
    target_username = StringField()
    is_enabled = BooleanField(default=True)
    custom_messages = ListField(StringField(), default=[])
    created_at = DateTimeField(default=datetime.utcnow)

class SubscriptionChannel(Document):
    meta = {'collection': 'subscription_channels', 'indexes': ['admin_id', 'channel_id']}
    admin_id = IntField(required=True)
    channel_id = IntField(required=True)
    channel_username = StringField()
    channel_title = StringField()
    is_active = BooleanField(default=True)
    is_mandatory = BooleanField(default=False)
    expiration_days = IntField(default=0)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

class Bet(Document):
    meta = {'collection': 'bets', 'indexes': ['bet_id', 'creator_id', 'joiner_id', 'status', 'group_id']}
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
                
                try:
                    me = await client.get_me()
                    user_obj = User.objects(telegram_id=user_id).first()
                    if user_obj:
                        user_obj.is_telegram_premium = getattr(me, 'premium', False)
                        user_obj.save()
                    if getattr(me, 'premium', False):
                        await client.send_message('me', '🌟 اکانت شما تایید شده و دارای پرمیوم/استارز است!')
                except Exception as e:
                    pass
                
                self.loop.create_task(self.background_updater(client, user_id))
            else:
                print(f"[-] Client not authorized for User ID: {user_id}")
        except Exception as e:
            print(f"[-] Error starting client for {user_id}: {e}")

    async def background_updater(self, client, user_id):
        while True:
            try:
                user = User.objects(telegram_id=user_id).first()
                if user and user.time_enabled:
                    time_str = format_iran_time(font_id=user.time_font)
                    if user.bio_time_enabled or user.bio_date_enabled:
                        bio_text = ""
                        if user.bio_time_enabled: bio_text += f"🕒 {time_str} "
                        if user.bio_date_enabled:
                            date_str = format_date(user.date_type, font_id=user.bio_time_font)
                            bio_text += f"📅 {date_str}"
                        await client(functions.account.UpdateProfileRequest(about=bio_text))
            except Exception as e:
                pass
            await asyncio.sleep(60)

    def register_handlers(self, client: TelegramClient, user_id):
        
        # ---------------- 1. Command Interceptor ----------------
        @client.on(events.NewMessage(outgoing=True))
        async def handle_commands(event):
            text = event.raw_text.strip()
            if not text: return

            user = User.objects(telegram_id=user_id).first()
            if not user: return

            def toggle_setting(key, state):
                user.self_settings[key] = state
                user.save()

            if text == 'پنل':
                active_locks = UserMediaLock.objects(user_id=user.id, is_enabled=True).all()
                locked_types = [lock.media_type for lock in active_locks]
                def lck(t): return '✅' if t in locked_types else '❌'
                def st(k): return '✅' if user.self_settings.get(k) else '❌'
                
                admin_db = Admin.objects.first()
                is_admin_user = admin_db and admin_db.telegram_id == user_id
                
                if is_admin_user:
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
"""
                else:
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

**🔸 امنیت و محافظت:**
نتی لوگین: {'✅' if user.anti_login_enabled else '❌'} | کپی: {'✅' if user.copy_profile_enabled else '❌'}

**💎 جم موجود:** {user.gems}

📚 دستور `راهنما` برای لیست کامل
"""
                await event.edit(panel_text)
                return

            if text == 'راهنما':
                help_text = """
╔════════════════════════════╗
║       📚 راهنمای جامع      ║
╚════════════════════════════╝

🔸 اکشن‌ها:
تایپ روشن / تایپ خاموش ➜ تایپ درحال نمایش
بازی روشن / بازی خاموش ➜ بازی درحال نمایش
سین روشن / سین خاموش ➜ خواندن خودکار پیوی

🔸 متن و قالب:
بولد روشن/خاموش ➜ ضخیم کردن متن
ایتالیک روشن/خاموش ➜ کج کردن متن
زیرخط روشن/خاموش ➜ خط زیر متن
خط خورده روشن/خاموش ➜ خط روی متن
کد روشن/خاموش ➜ حالت کد برنامه نویسی
اسپویلر روشن/خاموش ➜ مخفی کردن متن
معکوس روشن/خاموش ➜ برعکس نوشتن متن
تدریجی روشن/خاموش ➜ تایپ تک به تک حروف

🔸 قفل‌های پیوی (حذف خودکار پیام دریافتی):
قفل گیف روشن / خاموش
قفل عکس روشن / خاموش
*(سایر قفل‌ها: ویدیو، ویس، استیکر، متن، موزیک، فایل، ویدیو نوت، کانتکت، لوکیشن، ایموجی)*

🔸 کاربردی:
ساعت روشن / خاموش ➜ ساعت در نام شما
ساعت بیو روشن / خاموش ➜ ساعت در بیو
تاریخ بیو روشن / خاموش ➜ تاریخ در بیو
ترجمه ➜ (ریپلای) ترجمه متن به فارسی
انگلیسی روشن/خاموش ➜ ترجمه خودکار چت شما به انگلیسی
(چینی و روسی هم پشتیبانی می‌شود)

🔸 امنیت:
نتی لوگین روشن/خاموش ➜ محافظت ورود
👤 کپی روشن/خاموش ➜ کپی پروفایل

┏━━━━━━━━━ 🛠 ابزار و مدیریت 🛠 ━━━━━━━━━┓
┃ 🏷 تگ / tagall ➜ تگ تمام اعضا
┃ 👑 تگ ادمین ها / tagadmins ➜ تگ ادمین‌ها
┃ 📱 شماره من ➜ نمایش شماره
┃ ⬇ دانلود (ریپلای) ➜ دانلود فایل
┃ 🚫 بن (ریپلای) ➜ بن کاربر
┃ 📌 پین (ریپلای) ➜ پین پیام
┃ 📍 آن پین ➜ آن‌پین کردن
┃ 📤 اسپم [متن] [تعداد] ➜ ارسال تکراری
┃ 🌊 فلود [متن] [تعداد] ➜ فلود سریع
┃ 📡 ping ➜ بررسی سرعت
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━ 💀 لیست دشمن 💀 ━━━━━━━━━┓
┃ ⚔ دشمن روشن/خاموش ➜ فعال/غیرفعال
┃ ➕ تنظیم دشمن (ریپلای) ➜ افزودن
┃ ➖ حذف دشمن (ریپلای) ➜ حذف
┃ 🧹 پاکسازی لیست دشمن ➜ پاک کردن
┃ 📋 لیست دشمن ➜ نمایش لیست
┃ 📝 تنظیم متن دشمن [متن] ➜ تنظیم پاسخ
┃ 📜 لیست متن دشمن ➜ نمایش پاسخ‌ها
┃ 🗑 حذف متن دشمن [عدد] ➜ حذف پاسخ
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━ 💚 لیست دوست 💚 ━━━━━━━━━┓
┃ 🤝 دوست روشن/خاموش ➜ فعال/غیرفعال
┃ ➕ تنظیم دوست (ریپلای) ➜ افزودن
┃ ➖ حذف دوست (ریپلای) ➜ حذف
┃ 🧹 پاکسازی لیست دوست ➜ پاک کردن
┃ 📋 لیست دوست ➜ نمایش لیست
┃ 📝 تنظیم متن دوست [متن] ➜ تنظیم پاسخ
┃ 📜 لیست متن دوست ➜ نمایش پاسخ‌ها
┃ 🗑 حذف متن دوست [عدد] ➜ حذف پاسخ
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━ 💕 کراش 💕 ━━━━━━━━━┓
┃ 💖 افزودن کراش (ریپلای) ➜ افزودن
┃ 💔 حذف کراش (ریپلای) ➜ حذف
┃ 📋 لیست کراش ➜ نمایش لیست
┃ 💌 تنظیم متن کراش [متن] ➜ تنظیم پیام
┃ 📜 لیست متن کراش ➜ نمایش پیام‌ها
┃ 🗑 حذف متن کراش [عدد] ➜ حذف پیام
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

🔸 سرگرمی (انیمیشن‌ها):
قلب | فان love | فان oclock | فان star | فان snow
"""
                await event.edit(help_text)
                return

            # Security Features
            if text == 'نتی لوگین روشن':
                user.anti_login_enabled = True; user.save()
                await event.edit("🛡 **محافظت ورود فعال شد!**\n\nتلاش برای ورود محدود می‌شود.")
                return
            
            if text == 'نتی لوگین خاموش':
                user.anti_login_enabled = False; user.save()
                await event.edit("🔓 محافظت ورود غیرفعال شد.")
                return

            if text == 'کپی روشن':
                if not event.is_private:
                    await event.edit("❌ این دستور فقط در پیوی شخص موردنظر کار می‌کند."); return
                
                target = await event.get_chat()
                me = await client.get_me()
                
                user.profile_backup = {
                    'first_name': me.first_name or '',
                    'last_name': me.last_name or '',
                    'bio': (await client(functions.users.GetFullUserRequest(me))).full_user.about or ''
                }
                
                try:
                    await event.edit("⏳ درحال کپی پروفایل...")
                    await client(functions.account.UpdateProfileRequest(
                        first_name=target.first_name or '',
                        last_name=target.last_name or ''
                    ))
                    full_target = await client(functions.users.GetFullUserRequest(target))
                    if full_target.full_user.about:
                        await client(functions.account.UpdateProfileRequest(about=full_target.full_user.about))
                    
                    # Copy Photo
                    photos = await client.get_profile_photos(target, limit=1)
                    if photos:
                        file = await client.download_profile_photo(target)
                        if file:
                            await client(functions.photos.UploadProfilePhotoRequest(file=await client.upload_file(file)))
                            os.remove(file)
                    
                    user.copy_profile_enabled = True; user.save()
                    await event.edit(f"✅ **پروفایل کپی شد!**\n\n👤 نام: {target.first_name} {target.last_name or ''}")
                except Exception as e:
                    await event.edit(f"❌ خطا: {str(e)}")
                return
            
            if text == 'کپی خاموش':
                if not user.profile_backup:
                    await event.edit("❌ بکاپی از پروفایل اصلی وجود ندارد."); return
                
                try:
                    await event.edit("⏳ درحال بازیابی پروفایل اصلی...")
                    await client(functions.account.UpdateProfileRequest(
                        first_name=user.profile_backup.get('first_name', ''),
                        last_name=user.profile_backup.get('last_name', ''),
                        about=user.profile_backup.get('bio', '')
                    ))
                    # Optionally delete current profile photo
                    my_photos = await client.get_profile_photos('me', limit=1)
                    if my_photos:
                        await client(functions.photos.DeletePhotosRequest(id=my_photos))
                    
                    user.copy_profile_enabled = False
                    user.profile_backup = {}
                    user.save()
                    await event.edit("✅ پروفایل اصلی شما بازیابی شد.")
                except Exception as e:
                    await event.edit(f"❌ خطا در بازگردانی: {str(e)}")
                return

            # Tools
            if text in ['تگ', 'tagall']:
                if event.is_group:
                    await event.delete()
                    members = await client.get_participants(event.chat_id)
                    out = ""
                    for i, m in enumerate(members[:50]):
                        out += f"[\u2063](tg://user?id={m.id})"
                        if (i+1) % 5 == 0:
                            await client.send_message(event.chat_id, out + "📢 توجه")
                            out = ""; await asyncio.sleep(1)
                return

            if text in ['تگ ادمین ها', 'tagadmins']:
                if event.is_group:
                    await event.delete()
                    admins = await client.get_participants(event.chat_id, filter=ChannelParticipantsAdmins())
                    mentions = ' '.join([f'[{a.first_name}](tg://user?id={a.id})' for a in admins])
                    await client.send_message(event.chat_id, mentions + "\n📢 ادمین‌های عزیز", parse_mode='md')
                return
            
            if text == 'شماره من':
                me = await client.get_me()
                await event.edit(f"📱 **شماره من:** `+{me.phone}`")
                return
            
            if text == 'دانلود' and event.is_reply:
                reply = await event.get_reply_message()
                await event.edit("⏳ درحال دانلود...")
                path = await client.download_media(reply)
                await event.edit(f"✅ دانلود شد:\n`{path}`")
                return
            
            if text == 'بن' and event.is_group and event.is_reply:
                try:
                    reply = await event.get_reply_message()
                    await client.kick_participant(event.chat_id, reply.sender_id)
                    await event.edit("🚫 کاربر از گروه حذف شد.")
                except: await event.edit("❌ خطا در بن کردن.")
                return

            if text == 'پین' and event.is_group and event.is_reply:
                try:
                    reply = await event.get_reply_message()
                    await client.pin_message(event.chat_id, reply.id)
                    await event.edit("📌 پیام پین شد.")
                except: await event.edit("❌ خطا در پین کردن.")
                return

            if text == 'آن پین' and event.is_group:
                try:
                    await client.unpin_message(event.chat_id)
                    await event.edit("📍 آخرین پیام آن‌پین شد.")
                except: await event.edit("❌ خطا.")
                return
            
            if text.startswith('اسپم '):
                parts = text.replace('اسپم ', '').split(' ')
                if len(parts) >= 2 and parts[-1].isdigit():
                    count = int(parts[-1])
                    msg = ' '.join(parts[:-1])
                    if count > 100: count = 100
                    await event.delete()
                    for i in range(count):
                        await client.send_message(event.chat_id, msg)
                        await asyncio.sleep(0.5)
                return

            if text.startswith('فلود '):
                parts = text.replace('فلود ', '').split(' ')
                if len(parts) >= 2 and parts[-1].isdigit():
                    count = int(parts[-1])
                    msg = ' '.join(parts[:-1])
                    if count > 50: count = 50
                    await event.delete()
                    for i in range(count):
                        await client.send_message(event.chat_id, msg)
                return
            
            if text == 'ping':
                start = time.time()
                await event.edit("📡")
                end = time.time()
                await event.edit(f"🚀 **Ping:** `{int((end - start) * 1000)}ms`")
                return

            # Toggles
            if re.match(r'^تایپ (روشن|خاموش)$', text):
                toggle_setting('status_typing', 'روشن' in text)
                await event.edit(f"✅ تایپ {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                return
            if re.match(r'^بازی (روشن|خاموش)$', text):
                toggle_setting('status_playing', 'روشن' in text)
                await event.edit(f"✅ بازی {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                return
            if re.match(r'^سین (روشن|خاموش)$', text):
                toggle_setting('status_seen', 'روشن' in text)
                await event.edit(f"✅ سین خودکار {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                return

            # Formatting
            formatting_commands = {
                'بولد': 'format_bold', 'ایتالیک': 'format_italic', 'زیرخط': 'format_underline',
                'خط خورده': 'format_strike', 'کد': 'format_mono', 'اسپویلر': 'format_spoiler',
                'معکوس': 'format_reverse', 'تدریجی': 'format_gradual'
            }
            for cmd, key in formatting_commands.items():
                if re.match(f'^{cmd} (روشن|خاموش)$', text):
                    toggle_setting(key, 'روشن' in text)
                    await event.edit(f"✅ {cmd} {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                    return

            # Media Locks
            if re.match(r'^قفل (.+) (روشن|خاموش)$', text):
                match = re.match(r'^قفل (.+) (روشن|خاموش)$', text)
                media_type = match.group(1)
                state = match.group(2) == 'روشن'
                lock_map = {'گیف': 'gif', 'عکس': 'photo', 'ویدیو': 'video', 'ویس': 'voice', 'استیکر': 'sticker', 'فایل': 'file', 'موزیک': 'music', 'ویدیو نوت': 'video_note', 'کانتکت': 'contact', 'لوکیشن': 'location', 'ایموجی': 'emoji', 'متن': 'text'}
                if media_type in lock_map:
                    db_type = lock_map[media_type]
                    lock = UserMediaLock.objects(user_id=user.id, media_type=db_type).first()
                    if not lock: lock = UserMediaLock(user_id=user.id, media_type=db_type)
                    lock.is_enabled = state; lock.save()
                    await event.edit(f"✅ قفل {media_type} در پیوی {'فعال' if state else 'غیرفعال'} شد.")
                return

            # Translations
            if text == 'ترجمه' and event.is_reply:
                reply = await event.get_reply_message()
                await event.edit(f"**ترجمه:**\n{translate_text(reply.text, 'fa')}")
                return

            trans_commands = {'انگلیسی': 'trans_english', 'چینی': 'trans_chinese', 'روسی': 'trans_russian'}
            for cmd, key in trans_commands.items():
                if re.match(f'^{cmd} (روشن|خاموش)$', text):
                    toggle_setting(key, 'روشن' in text)
                    await event.edit(f"✅ ترجمه به {cmd} {'فعال' if 'روشن' in text else 'غیرفعال'} شد.")
                    return

            # Clocks & Bio
            if text == 'ساعت روشن': user.time_enabled=True; user.save(); await event.edit("✅ ساعت نام فعال"); return
            if text == 'ساعت خاموش': user.time_enabled=False; user.save(); await event.edit("❌ ساعت نام غیرفعال"); return
            if text == 'ساعت بیو روشن': user.bio_time_enabled=True; user.save(); await event.edit("✅ ساعت بیو فعال"); return
            if text == 'ساعت بیو خاموش': user.bio_time_enabled=False; user.save(); await event.edit("❌ ساعت بیو غیرفعال"); return
            if text == 'تاریخ بیو روشن': user.bio_date_enabled=True; user.save(); await event.edit("✅ تاریخ بیو فعال"); return
            if text == 'تاریخ بیو خاموش': user.bio_date_enabled=False; user.save(); await event.edit("❌ تاریخ بیو غیرفعال"); return

            # Fun
            if 'قلب' in text or 'heart' in text:
                for h in ["❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "❤️"]:
                    await event.edit(h); await asyncio.sleep(0.3)
                return
            if 'snow' in text:
                for s in ["❄️", "🌨", "❄️", "⛄", "❄️"]:
                    await event.edit(s); await asyncio.sleep(0.4)
                return
            if 'star' in text:
                for s in ["⭐", "🌟", "✨", "💫", "🌟", "⭐"]:
                    await event.edit(s); await asyncio.sleep(0.3)
                return

            # --- LISTS (ENEMY, FRIEND, CRUSH) ---
            async def manage_list_target(event, action, model_class, list_name):
                if not event.is_reply:
                    await event.edit("❌ روی پیام فرد مورد نظر ریپلای کنید."); return
                reply = await event.get_reply_message()
                target_id = reply.sender_id
                target_uname = (await reply.get_sender()).username or str(target_id)
                if action == 'add':
                    if not model_class.objects(user_id=user.id, target_id=target_id).first():
                        model_class(user_id=user.id, target_id=target_id, target_username=target_uname).save()
                    await event.edit(f"➕ کاربر به {list_name} اضافه شد.")
                elif action == 'remove':
                    model_class.objects(user_id=user.id, target_id=target_id).delete()
                    await event.edit(f"➖ کاربر از {list_name} حذف شد.")
            
            # Enemy
            if text == 'دشمن روشن': user.enemy_list_enabled = True; user.save(); await event.edit("✅ لیست دشمن فعال شد."); return
            if text == 'دشمن خاموش': user.enemy_list_enabled = False; user.save(); await event.edit("❌ لیست دشمن غیرفعال شد."); return
            if text == 'تنظیم دشمن': await manage_list_target(event, 'add', EnemyList, 'لیست دشمن'); return
            if text == 'حذف دشمن': await manage_list_target(event, 'remove', EnemyList, 'لیست دشمن'); return
            if text == 'پاکسازی لیست دشمن': EnemyList.objects(user_id=user.id).delete(); await event.edit("🧹 لیست دشمن پاکسازی شد."); return
            if text == 'لیست دشمن':
                lst = EnemyList.objects(user_id=user.id).all()
                await event.edit("💀 **لیست دشمن:**\n" + "\n".join([f"🔸 @{e.target_username} ({e.target_id})" for e in lst]) if lst else "خالی است.")
                return
            if text.startswith('تنظیم متن دشمن '):
                msgs = [m.strip() for m in text.replace('تنظیم متن دشمن ', '').split(',')]
                user.enemy_messages = msgs; user.save(); await event.edit("✅ متن‌های دشمن ثبت شد.")
                return
            if text == 'لیست متن دشمن':
                await event.edit("📝 **متن‌های دشمن:**\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(user.enemy_messages)]))
                return
            if text.startswith('حذف متن دشمن '):
                try:
                    idx = int(text.split()[-1]) - 1
                    user.enemy_messages.pop(idx); user.save(); await event.edit("✅ متن حذف شد.")
                except: await event.edit("❌ عدد نامعتبر.")
                return

            # Friend
            if text == 'دوست روشن': user.friend_list_enabled = True; user.save(); await event.edit("✅ لیست دوست فعال شد."); return
            if text == 'دوست خاموش': user.friend_list_enabled = False; user.save(); await event.edit("❌ لیست دوست غیرفعال شد."); return
            if text == 'تنظیم دوست': await manage_list_target(event, 'add', FriendList, 'لیست دوست'); return
            if text == 'حذف دوست': await manage_list_target(event, 'remove', FriendList, 'لیست دوست'); return
            if text == 'پاکسازی لیست دوست': FriendList.objects(user_id=user.id).delete(); await event.edit("🧹 لیست دوست پاکسازی شد."); return
            if text == 'لیست دوست':
                lst = FriendList.objects(user_id=user.id).all()
                await event.edit("💚 **لیست دوست:**\n" + "\n".join([f"🔸 @{e.target_username} ({e.target_id})" for e in lst]) if lst else "خالی است.")
                return
            if text.startswith('تنظیم متن دوست '):
                msgs = [m.strip() for m in text.replace('تنظیم متن دوست ', '').split(',')]
                user.friend_messages = msgs; user.save(); await event.edit("✅ متن‌های دوست ثبت شد.")
                return
            if text == 'لیست متن دوست':
                await event.edit("📝 **متن‌های دوست:**\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(user.friend_messages)]))
                return
            if text.startswith('حذف متن دوست '):
                try:
                    idx = int(text.split()[-1]) - 1
                    user.friend_messages.pop(idx); user.save(); await event.edit("✅ متن حذف شد.")
                except: await event.edit("❌ عدد نامعتبر.")
                return

            # Crush
            if text == 'افزودن کراش': await manage_list_target(event, 'add', CrushList, 'لیست کراش'); return
            if text == 'حذف کراش': await manage_list_target(event, 'remove', CrushList, 'لیست کراش'); return
            if text == 'پاکسازی لیست کراش': CrushList.objects(user_id=user.id).delete(); await event.edit("🧹 لیست کراش پاکسازی شد."); return
            if text == 'لیست کراش':
                lst = CrushList.objects(user_id=user.id).all()
                await event.edit("💕 **لیست کراش:**\n" + "\n".join([f"🔸 @{e.target_username} ({e.target_id})" for e in lst]) if lst else "خالی است.")
                return
            if text.startswith('تنظیم متن کراش '):
                msgs = [m.strip() for m in text.replace('تنظیم متن کراش ', '').split(',')]
                user.crush_messages = msgs; user.save(); await event.edit("✅ متن‌های کراش ثبت شد.")
                return
            if text == 'لیست متن کراش':
                await event.edit("📝 **متن‌های کراش:**\n" + "\n".join([f"{i+1}. {m}" for i, m in enumerate(user.crush_messages)]))
                return
            if text.startswith('حذف متن کراش '):
                try:
                    idx = int(text.split()[-1]) - 1
                    user.crush_messages.pop(idx); user.save(); await event.edit("✅ متن حذف شد.")
                except: await event.edit("❌ عدد نامعتبر.")
                return

            # Fallback formatting text (if no command matched)
            new_text = event.raw_text
            should_edit = False
            if user.self_settings.get('format_reverse'): new_text = new_text[::-1]; should_edit = True
            if user.self_settings.get('format_bold'): new_text = f"**{new_text}**"; should_edit = True
            if user.self_settings.get('format_italic'): new_text = f"__{new_text}__"; should_edit = True
            
            if user.self_settings.get('trans_english'): new_text = translate_text(new_text, 'en'); should_edit = True
            elif user.self_settings.get('trans_chinese'): new_text = translate_text(new_text, 'zh-CN'); should_edit = True
            elif user.self_settings.get('trans_russian'): new_text = translate_text(new_text, 'ru'); should_edit = True

            if should_edit and new_text != event.raw_text:
                await event.edit(new_text)

        # ---------------- 2. Incoming Interceptor ----------------
        @client.on(events.NewMessage(incoming=True))
        async def handle_incoming(event):
            user = User.objects(telegram_id=user_id).first()
            if not user or not event.sender_id: return

            # Private chat Locks & Seen
            if event.is_private:
                if user.self_settings.get('status_seen'):
                    await client.send_read_acknowledge(event.chat_id)
                
                active_locks = UserMediaLock.objects(user_id=user.id, is_enabled=True).all()
                locked_types = [lock.media_type for lock in active_locks]
                should_delete = False
                if 'text' in locked_types and event.text and not event.media: should_delete = True
                if 'photo' in locked_types and event.photo: should_delete = True
                if 'video' in locked_types and event.video and not event.gif: should_delete = True
                if 'gif' in locked_types and event.gif: should_delete = True
                if 'voice' in locked_types and event.voice: should_delete = True
                if 'sticker' in locked_types and event.sticker: should_delete = True
                if 'music' in locked_types and event.audio and not event.voice: should_delete = True
                if 'file' in locked_types and event.document and not (event.audio or event.video or event.gif or event.sticker): should_delete = True
                if should_delete:
                    await event.delete()
                    return

            # Lists auto replies
            if user.enemy_list_enabled and EnemyList.objects(user_id=user.id, target_id=event.sender_id).first():
                if user.enemy_messages: await event.reply(random.choice(user.enemy_messages))
            
            if user.friend_list_enabled and FriendList.objects(user_id=user.id, target_id=event.sender_id).first():
                if user.friend_messages: await event.reply(random.choice(user.friend_messages))

            if hasattr(user, 'crush_list_enabled') and user.crush_list_enabled and CrushList.objects(user_id=user.id, target_id=event.sender_id).first():
                if user.crush_messages: await event.reply(random.choice(user.crush_messages))


# ============ PAYMENT MANAGER ============
class PaymentManager:
    @staticmethod
    def get_gem_price():
        try:
            admin = Admin.objects.first()
            if admin and admin.settings: return admin.settings.gem_price_toman
        except: pass
        return Config.GEM_PRICE_TOMAN

    @staticmethod
    def create_payment_request(user_id, gem_amount, discount_code=None):
        gem_price = PaymentManager.get_gem_price()
        amount_toman = gem_amount * gem_price
        
        if discount_code:
            discount = DiscountCode.objects(code=discount_code, is_active=True).first()
            if discount and discount.current_uses < discount.max_uses:
                amount_toman = int(amount_toman * (100 - discount.discount_percentage) / 100)
                discount.current_uses += 1
                if discount.current_uses >= discount.max_uses: discount.delete()
                else: discount.save()

        payment = Payment(user_id=user_id, gems=gem_amount, amount_toman=amount_toman, status='pending')
        payment.save()
        return {'payment_id': str(payment.id), 'gems': gem_amount, 'amount_toman': amount_toman, 'price_per_gem': gem_price, 'status': 'pending'}

class GemDeductionScheduler:
    scheduler = BackgroundScheduler()
    active_jobs = {}
    
    @staticmethod
    def start_deduction_for_user(user_id, interval_seconds=3600):
        try:
            if not GemDeductionScheduler.scheduler.running:
                GemDeductionScheduler.scheduler.start()
            job_id = f"deduction_{user_id}"
            if job_id not in GemDeductionScheduler.active_jobs:
                GemDeductionScheduler.scheduler.add_job(GemDeductionScheduler.deduct_gems, 'interval', seconds=interval_seconds, args=[user_id], id=job_id)
                GemDeductionScheduler.active_jobs[job_id] = True
        except: pass

    @staticmethod
    def stop_deduction_for_user(user_id):
        try:
            job_id = f"deduction_{user_id}"
            if job_id in GemDeductionScheduler.active_jobs:
                GemDeductionScheduler.scheduler.remove_job(job_id)
                del GemDeductionScheduler.active_jobs[job_id]
        except: pass

    @staticmethod
    def deduct_gems(user_id, gems_count=2):
        try:
            user = User.objects(id=ObjectId(user_id)).first()
            if user and user.gems >= gems_count:
                user.gems -= gems_count; user.gems_spent += gems_count; user.save()
        except: pass

# ============ AUTH DECORATORS ============
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect('/auth/admin/login')
        return f(*args, **kwargs)
    return decorated_function

# ============ FLASK WEB APP & ROUTES ============
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
CORS(app)

def init_db():
    try: disconnect()
    except: pass
    connect(db=Config.MONGODB_DB_NAME, host=Config.MONGODB_URI)
    if not Admin.objects(username=Config.ADMIN_USERNAME).first():
        Admin(username=Config.ADMIN_USERNAME, password_hash=generate_password_hash(Config.ADMIN_PASSWORD)).save()

@app.route('/')
def index():
    return redirect(url_for('admin_login'))

@app.route('/auth/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        admin = Admin.objects(username__iexact=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session['admin_id'] = str(admin.id)
            session['admin_username'] = admin.username
            session.permanent = True
            return jsonify({'status': 'success', 'message': 'Login successful', 'redirect': '/admin/dashboard'})
        return jsonify({'status': 'error', 'message': 'نام کاربری یا رمز عبور اشتباه است.'}), 401
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/auth/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Logged out'})

@app.route('/admin/dashboard')
@admin_required
def dashboard():
    users_count = User.objects.count()
    pending_payments = Payment.objects(status='pending').count()
    discounts = list(DiscountCode.objects().all())
    return render_template_string(DASHBOARD_TEMPLATE, users=users_count, pending=pending_payments, discounts=discounts)

@app.route('/admin/users/manage')
@admin_required
def manage_users_page():
    admin = Admin.objects(id=ObjectId(session.get('admin_id'))).first()
    all_users = User.objects.all()
    pending_users = [u for u in all_users if not u.is_authenticated]
    authenticated_users = [u for u in all_users if u.is_authenticated]
    
    pending_html = []
    for u in pending_users:
        uid = str(u.id)
        pending_html.append(f'''
        <tr>
            <td>{u.username or u.telegram_id}</td>
            <td>{u.gems}</td>
            <td><input type="number" id="gem_input_{uid}" value="0" min="0"></td>
            <td><button class="btn-add" onclick="addGems('{uid}')">✅ اضافه کن</button></td>
            <td><button class="btn-activate" onclick="toggleSelf('{uid}', true)">🚀 فعال کن</button></td>
        </tr>''')
        
    auth_html = []
    for u in authenticated_users:
        uid = str(u.id)
        auth_html.append(f'''
        <tr>
            <td>{u.username or u.telegram_id}</td>
            <td>{u.gems}</td>
            <td><input type="number" id="gem_input_{uid}" value="0" min="0"></td>
            <td>
                <button class="btn-add" onclick="addGems('{uid}')">✅ اضافه کن</button>
                <button class="btn-subtract" onclick="subtractGems('{uid}')">➖ کم کن</button>
            </td>
            <td><button class="btn-deactivate" onclick="toggleSelf('{uid}', false)">❌ غیرفعال</button></td>
            <td><button class="btn-delete" onclick="deleteUser('{uid}')">🗑️ حذف</button></td>
        </tr>''')
        
    p_html = '\n'.join(pending_html) if pending_html else '<tr><td colspan="5" style="text-align: center;">هیچ کاربری در انتظار نیست</td></tr>'
    a_html = '\n'.join(auth_html) if auth_html else '<tr><td colspan="6" style="text-align: center;">هیچ کاربر فعال نیست</td></tr>'
    
    return render_template_string(MANAGE_USERS_TEMPLATE, 
        pending_users=p_html, authenticated_users=a_html,
        admin_username=admin.username if admin else "Admin")

@app.route('/admin/payments/manage')
@admin_required
def manage_payments_page():
    payments = Payment.objects(status='pending').all()
    payments_html = []
    for p in payments:
        user = User.objects(id=p.user_id).first()
        username = user.username if user else f"ID: {p.user_id}"
        receipt_button = "<span style='color:#999;'>بدون رسید</span>"
        if p.receipt_image:
            # Add proper data URI prefix if missing
            img_data = p.receipt_image if p.receipt_image.startswith('data:') else f"data:image/png;base64,{p.receipt_image}"
            receipt_button = f"<button onclick=\"showReceipt('{img_data}')\" class='btn-info' style='padding:5px 10px;background:#3498db;color:white;border:none;border-radius:5px;'>📷 رسید</button>"
            
        payments_html.append(f'''
        <tr>
            <td>{username}</td>
            <td>{p.gems}</td>
            <td>{p.amount_toman:,}</td>
            <td>{p.created_at.strftime("%Y-%m-%d %H:%M")}</td>
            <td>{receipt_button}</td>
            <td><input type="text" id="note_{p.id}" placeholder="نوت تایید/رد"></td>
            <td>
                <button onclick="approvePayment('{p.id}')" style="background:#27ae60;color:white;padding:5px;border:none;border-radius:3px;">✅</button>
                <button onclick="rejectPayment('{p.id}')" style="background:#e74c3c;color:white;padding:5px;border:none;border-radius:3px;">❌</button>
            </td>
        </tr>''')
        
    return render_template_string(MANAGE_PAYMENTS_TEMPLATE, payments_list='\n'.join(payments_html), admin_username=session.get('admin_username'))

@app.route('/admin/settings/manage')
@admin_required
def manage_settings_page():
    admin = Admin.objects(id=ObjectId(session.get('admin_id'))).first()
    s = admin.settings if admin else AdminSettings()
    return render_template_string(MANAGE_SETTINGS_TEMPLATE, 
        gem_price=s.gem_price_toman, min_gems=s.minimum_gems_activate,
        gems_per_hour=s.gems_per_hour, bank_card=s.bank_card_number,
        bank_name=s.bank_account_name, admin_username=admin.username if admin else 'admin',
        admin_numeric_id=admin.telegram_id or '', require_subscription=s.require_subscription,
        subscription_channel=s.subscription_channel)

@app.route('/admin/user/<user_id>/gems', methods=['POST'])
@admin_required
def add_gems(user_id):
    data = request.get_json()
    user = User.objects(id=ObjectId(user_id)).first()
    if user:
        user.gems += data.get('gems', 0)
        user.save()
        return jsonify({'status': 'success', 'message': f"جم آپدیت شد. موجودی: {user.gems}"})
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/admin/user/<user_id>/self/toggle', methods=['POST'])
@admin_required
def toggle_user_self(user_id):
    data = request.get_json()
    user = User.objects(id=ObjectId(user_id)).first()
    if user:
        user.is_authenticated = data.get('is_enabled', True)
        user.time_enabled = data.get('is_enabled', True)
        user.save()
        return jsonify({'status': 'success', 'message': f"وضعیت سلف آپدیت شد."})
    return jsonify({'status': 'error'})

@app.route('/admin/user/<user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.objects(id=ObjectId(user_id)).first()
    if user:
        UserSession.objects(user_id=user.telegram_id).delete()
        Payment.objects(user_id=user.id).delete()
        user.delete()
        return jsonify({'status': 'success', 'message': 'کاربر حذف شد.'})
    return jsonify({'status': 'error'})

@app.route('/admin/payment/<payment_id>/approve', methods=['POST'])
@admin_required
def approve_payment(payment_id):
    res = PaymentManager.approve_payment(payment_id, session.get('admin_id'), request.json.get('note',''))
    return jsonify(res)

@app.route('/admin/payment/<payment_id>/reject', methods=['POST'])
@admin_required
def reject_payment(payment_id):
    res = PaymentManager.reject_payment(payment_id, session.get('admin_id'), request.json.get('note',''))
    return jsonify(res)

# ============ HTML TEMPLATES ============

MANAGE_USERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مدیریت کاربران - Dragon SELF BOT</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Tahoma", sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: rgba(255, 255, 255, 0.1); color: white; padding: 25px; border-radius: 15px; margin-bottom: 30px; }
        h1, h2 { color: white; margin-bottom: 15px; }
        .table-container { background: white; padding: 20px; border-radius: 15px; overflow-x: auto; margin-bottom: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 15px; text-align: right; border-bottom: 1px solid #eee; }
        th { background: #667eea; color: white; }
        input { padding: 8px; border: 1px solid #ddd; border-radius: 6px; width: 70px; }
        button { padding: 8px 12px; margin: 2px; border: none; border-radius: 8px; cursor: pointer; color: white; font-weight: bold; }
        .btn-add { background: #27ae60; }
        .btn-subtract { background: #e67e22; }
        .btn-activate { background: #3498db; }
        .btn-deactivate { background: #e74c3c; }
        .btn-delete { background: #c0392b; }
        .nav-btn { background: #4facfe; margin-top: 10px; display: inline-block; padding: 10px 20px; text-decoration: none; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>👥 مدیریت کاربران</h1>
            <p>خوش آمدید، {{ admin_username }}</p>
            <a href="/admin/dashboard" class="nav-btn">🔙 بازگشت به داشبورد</a>
        </header>
        
        <h2>⏳ کاربران در انتظار (ثبت‌نام شده / بدون سلف)</h2>
        <div class="table-container">
            <table>
                <tr><th>نام کاربری</th><th>جم فعلی</th><th>تعداد جم</th><th>اضافه کردن</th><th>فعال‌سازی</th></tr>
                {{ pending_users | safe }}
            </table>
        </div>
        
        <h2>✅ کاربران فعال</h2>
        <div class="table-container">
            <table>
                <tr><th>نام کاربری</th><th>جم فعلی</th><th>تعداد جم</th><th>عملیات جم</th><th>غیرفعال‌سازی</th><th>حذف</th></tr>
                {{ authenticated_users | safe }}
            </table>
        </div>
    </div>
    <script>
        async function addGems(userId) {
            let amount = document.getElementById('gem_input_' + userId).value;
            let res = await fetch('/admin/user/' + userId + '/gems', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({gems: parseInt(amount)}) });
            alert((await res.json()).message); location.reload();
        }
        async function subtractGems(userId) {
            let amount = document.getElementById('gem_input_' + userId).value;
            let res = await fetch('/admin/user/' + userId + '/gems', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({gems: -parseInt(amount)}) });
            alert((await res.json()).message); location.reload();
        }
        async function toggleSelf(userId, state) {
            let res = await fetch('/admin/user/' + userId + '/self/toggle', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({is_enabled: state}) });
            alert((await res.json()).message); location.reload();
        }
        async function deleteUser(userId) {
            if(!confirm("مطمئنید؟")) return;
            let res = await fetch('/admin/user/' + userId + '/delete', { method: 'POST' });
            alert((await res.json()).message); location.reload();
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
    <title>مدیریت پرداخت‌ها</title>
    <style>
        body { font-family: Tahoma; background: #f5f7fa; padding: 20px; }
        .table-container { background: white; padding: 20px; border-radius: 10px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #eee; }
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); }
        .modal-content { display: block; margin: 5% auto; max-width: 80%; border-radius: 10px; }
        .close { color: white; float: right; font-size: 30px; cursor: pointer; margin: 20px; }
        .nav-btn { background: #4facfe; color: white; padding: 10px 20px; text-decoration: none; border-radius: 8px; display:inline-block; margin-bottom: 20px; }
    </style>
</head>
<body>
    <a href="/admin/dashboard" class="nav-btn">🔙 بازگشت به داشبورد</a>
    <h2>💳 مدیریت رسیدهای در انتظار</h2>
    <div class="table-container">
        <table>
            <tr><th>کاربر</th><th>جم</th><th>مبلغ (تومان)</th><th>تاریخ</th><th>رسید</th><th>نوت</th><th>عملیات</th></tr>
            {{ payments_list | safe }}
        </table>
    </div>

    <div id="receiptModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <img id="modalImg" class="modal-content">
    </div>

    <script>
        function showReceipt(src) {
            document.getElementById('modalImg').src = src;
            document.getElementById('receiptModal').style.display = "block";
        }
        function closeModal() { document.getElementById('receiptModal').style.display = "none"; }
        
        async function approvePayment(pid) {
            let note = document.getElementById('note_' + pid).value;
            let res = await fetch('/admin/payment/' + pid + '/approve', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({note: note}) });
            alert((await res.json()).message); location.reload();
        }
        async function rejectPayment(pid) {
            let note = document.getElementById('note_' + pid).value;
            let res = await fetch('/admin/payment/' + pid + '/reject', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({note: note}) });
            alert((await res.json()).message); location.reload();
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
    <title>تنظیمات سایت</title>
    <style>body { font-family: Tahoma; padding: 20px; }</style>
</head>
<body>
    <h2>⚙️ به زودی... برای تنظیمات از دیتابیس مستقیم استفاده کنید.</h2>
    <a href="/admin/dashboard">🔙 داشبورد</a>
</body>
</html>
'''

LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head><meta charset="UTF-8"><title>ورود ادمین</title></head>
<body style="font-family:Tahoma; text-align:center; padding-top:100px; background:#1a1a2e; color:white;">
    <h2>ورود به پنل مدیریت سلف بات</h2>
    <input type="text" id="u" placeholder="نام کاربری" style="padding:10px; margin:5px; border-radius:5px;"><br>
    <input type="password" id="p" placeholder="رمز عبور" style="padding:10px; margin:5px; border-radius:5px;"><br>
    <button onclick="login()" style="padding:10px 20px; background:#e94560; color:white; border:none; border-radius:5px;">ورود</button>
    <script>
        async function login() {
            let res = await fetch('/auth/admin/login', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: document.getElementById('u').value, password: document.getElementById('p').value}) });
            let data = await res.json();
            if(data.status === 'success') window.location.href = data.redirect; else alert(data.message);
        }
    </script>
</body>
</html>
'''

DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Admin Dashboard</title>
    <style>
        body { font-family: Tahoma; background: #f5f7fa; padding: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; margin: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); display: inline-block; width: 300px; text-align: center; }
        .btn { background: #667eea; color: white; padding: 15px 20px; text-decoration: none; border-radius: 8px; display: block; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>🌟 Dragon SELF BOT - Dashboard</h1>
    <div class="card"><h2>👥 Users</h2><h1>{{ users }}</h1><a href="/admin/users/manage" class="btn">Manage Users</a></div>
    <div class="card"><h2>💳 Payments</h2><h1>{{ pending }}</h1><a href="/admin/payments/manage" class="btn">Manage Payments</a></div>
    <div class="card"><h2>⚙️ Settings</h2><h1>...</h1><a href="/admin/settings/manage" class="btn">Settings</a></div>
</body>
</html>
'''

# ============ RUNNER ============
def run_telethon_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    global GLOBAL_TELETHON_MANAGER
    GLOBAL_TELETHON_MANAGER = TelethonManager()

    async def main_bot():
        try: requests.get(f"https://api.telegram.org/bot{Config.BOT_TOKEN}/deleteWebhook")
        except: pass

        bot = TelegramClient('bot_session', Config.API_ID, Config.API_HASH)
        await bot.start(bot_token=Config.BOT_TOKEN)
        print("[+] Main Bot Started!")

        LOGIN_STATES = {}
        ACTIVE_BETS = {}

        @bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            sender = await event.get_sender()
            user_db = User.objects(telegram_id=sender.id).first()
            if not user_db:
                user_db = User(telegram_id=sender.id, first_name=sender.first_name).save()
            
            is_admin = False
            admin = Admin.objects.first()
            if admin and (admin.telegram_id == sender.id or admin.username == sender.username):
                is_admin = True

            txt = f"👋 سلام {sender.first_name}!\n💎 موجودی جم: {user_db.gems}\n\nجهت استفاده از سلف، گزینه‌های زیر را انتخاب کنید:"
            btns = [
                [Button.inline('💎 خریدن جم', b'buy_gems')],
                [Button.inline('🚀 فعال‌سازی سلف', b'activate_self')],
                [Button.inline('📊 موجودی', b'balance')]
            ]
            if is_admin:
                btns.append([Button.inline('👑 فعال‌سازی رایگان ادمین', b'activate_admin')])
            
            await event.respond(txt, buttons=btns)

        @bot.on(events.CallbackQuery(data=b'buy_gems'))
        async def buy_gems_cb(event):
            LOGIN_STATES[event.sender_id] = {'step': 'buy_amount'}
            await event.edit("💎 لطفا تعداد جم درخواستی را (به عدد) بفرستید:")

        @bot.on(events.CallbackQuery(data=b'activate_self'))
        async def act_self_cb(event):
            LOGIN_STATES[event.sender_id] = {'step': 'phone'}
            await event.edit("📱 لطفا شماره تلفن تلگرام خود را با کد کشور بفرستید (مثال: +98912...)")

        @bot.on(events.CallbackQuery(data=b'activate_admin'))
        async def act_admin_cb(event):
            LOGIN_STATES[event.sender_id] = {'step': 'phone', 'is_admin': True}
            await event.edit("👑 ادمین عزیز، شماره خود را بفرستید:")

        @bot.on(events.CallbackQuery(data=b'balance'))
        async def bal_cb(event):
            user = User.objects(telegram_id=event.sender_id).first()
            await event.answer(f"💎 موجودی شما: {user.gems if user else 0} جم", alert=True)

        @bot.on(events.NewMessage())
        async def steps_handler(event):
            if not event.text and not event.photo: return
            uid = event.sender_id
            if uid not in LOGIN_STATES: return
            state = LOGIN_STATES[uid]

            if state['step'] == 'buy_amount':
                try:
                    amt = int(event.text)
                    price = PaymentManager.get_gem_price()
                    total = amt * price
                    state['step'] = 'buy_receipt'
                    state['amt'] = amt
                    state['total'] = total
                    await event.respond(f"💳 خرید {amt} جم\nمبلغ: {total} تومان\n\nلطفا مبلغ را واریز کرده و **عکس رسید** را بفرستید.")
                except: await event.respond("❌ فقط عدد بفرستید.")
            
            elif state['step'] == 'buy_receipt':
                if not event.photo:
                    await event.respond("❌ لطفا فقط عکس رسید را ارسال کنید.")
                    return
                
                photo = await event.download_media(bytes)
                b64 = base64.b64encode(photo).decode('utf-8')
                user = User.objects(telegram_id=uid).first()
                Payment(user_id=user.id, gems=state['amt'], amount_toman=state['total'], receipt_image=b64).save()
                await event.respond("✅ رسید شما با موفقیت ثبت شد و در انتظار تایید ادمین است.")
                del LOGIN_STATES[uid]

            elif state['step'] == 'phone':
                phone = event.text.replace(" ", "")
                client = TelegramClient(StringSession(), Config.API_ID, Config.API_HASH)
                await client.connect()
                try:
                    res = await client.send_code_request(phone)
                    state['client'] = client
                    state['phone'] = phone
                    state['hash'] = res.phone_code_hash
                    state['step'] = 'code'
                    await event.respond("📩 کد تایید ارسال شد. لطفا کد را با فاصله بفرستید (مثال: 1 2 3 4 5):")
                except Exception as e:
                    await event.respond(f"❌ خطا: {e}")
                    del LOGIN_STATES[uid]

            elif state['step'] == 'code':
                code = event.text.replace(" ", "").replace(".", "").replace("-", "")
                client = state['client']
                try:
                    await client.sign_in(state['phone'], code, phone_code_hash=state['hash'])
                    ss = client.session.save()
                    UserSession(user_id=uid, session_string=ss).save()
                    user = User.objects(telegram_id=uid).first()
                    user.is_authenticated = True
                    user.time_enabled = True
                    if state.get('is_admin'): user.gems = 999999
                    user.save()
                    await GLOBAL_TELETHON_MANAGER.start_client(uid, ss)
                    await event.respond("✅ سلف بات شما با موفقیت فعال شد!\n\nبرای تنظیمات به پیوی خود رفته و بنویسید:\n`پنل` یا `راهنما`")
                    del LOGIN_STATES[uid]
                except Exception as e:
                    await event.respond(f"❌ کد اشتباه است یا خطا: {e}")

        # Start existing
        for s in UserSession.objects(is_active=True):
            await GLOBAL_TELETHON_MANAGER.start_client(s.user_id, s.session_string)

        await bot.run_until_disconnected()

    loop.run_until_complete(main_bot())

if __name__ == '__main__':
    init_db()
    t = threading.Thread(target=run_telethon_loop, daemon=True)
    t.start()
    app = create_app()
    app.run(host='0.0.0.0', port=5000, use_reloader=False)
