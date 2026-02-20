# 🌟 DARK SELF BOT

## ربات خودکار تلگرام با قابلیت‌های پیشرفته

This is a comprehensive Telegram self-bot framework with an admin control panel for managing users, payments, and bot features.

---

## 📋 Features

### Status & Actions
- ⏰ Typing indicator
- 🎮 Playing status
- 🎙 Voice recording indicator
- 📸 Photo upload status
- 🎬 Video upload status
- 👁 Choose contact indicator

### Text Formatting
- **Bold**, *Italic*, <u>Underline</u>, ~~Strikethrough~~
- Monospace/Code formatting
- Spoiler text
- Reverse text (معکوس)
- Progressive display

### Auto-Translation
- 🇬🇧 English translation
- 🇨🇳 Chinese translation
- 🇷🇺 Russian translation
- 🇸🇦 Arabic translation

### Media Locks (in private messages)
- GIF lock, Photo lock, Video lock
- Voice lock, Sticker lock, File lock
- Audio lock, Video note lock
- Contact lock, Location lock
- Emoji filter, Text message lock

### Time Features
- ⏰ Real-time display in profile name
- Multiple font styles
- 📅 Gregorian and Jalali calendar support
- Time and date in bio

### Message Management
- 🗑️ Delete messages (bulk)
- 💾 Save to favorites (timed)
- 🔒 Secret save (with reaction)
- 🔁 Message repeat
- 🔄 Auto-repeat intervals

### User Lists
- 💀 Enemy list with auto-responses
- 💚 Friend list with special replies
- 💕 Crush list with custom messages
- 🧹 Bulk list management

### Comments & Secretary
- 💬 Auto-comment on forwarded messages
- 📢 Secretary/Auto-reply system
- 🤖 AI-powered auto-replies
- 🔐 Anti-login protection

### Advanced Features
- 🏷️ Mention all (@channel members)
- 🔄 Auto-reactions with emojis
- 🎭 Animation effects (heart, snow, star, clock)
- 🧠 AI learning from conversations
- 👤 Profile copy prevention
- 🔒 Private message lock

### Admin Panel
- Dashboard with statistics
- User management
- Payment approval system
- Gem pricing management
- Settings configuration

---

## 🚀 Installation & Setup

### 1. Clone or Extract the Project

```bash
cd c:\Users\msi\Desktop\selfpython
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

**Edit `.env` and add your values:**

```env
# Telegram API (Get from https://my.telegram.org)
API_ID=123456789
API_HASH=abcdefghijklmnopqrstuvwxyz

# Bot Token (Get from @BotFather)
BOT_TOKEN=123456789:ABCdefGHIjklmnoPQRstuvWXYZ

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password

# Bank Details (for payment verification)
BANK_CARD_NUMBER=1234567890123456
BANK_ACCOUNT_NAME=Your Name

# Other Settings
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
```

### 4. Get Telegram API Credentials

1. Visit https://my.telegram.org
2. Sign in with your phone number
3. Click "API development tools"
4. Create an app and get `API_ID` and `API_HASH`
5. Add these to your `.env`

### 5. Create Database (First Run)

```bash
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
>>>     db.create_all()
>>> exit()
```

---

## ▶️ Running the Application

### Start the Flask Web Server

```bash
python app.py
```

The application will start on: **http://localhost:5000**

### Access Admin Panel

1. Open browser: http://localhost:5000/auth/admin/login
2. Default credentials:
   - **Username:** `admin`
   - **Password:** `admin123` (Change this in `.env`!)

3. You can now:
   - Approve/reject user payments
   - Manage users and their gems
   - View statistics and analytics
   - Configure bot settings

---

## 📱 User Registration & Login Flow

### 1. User Phone Registration
```
POST /auth/user/register
{
  "phone_number": "+989123456789"
}
```

### 2. Verify SMS Code
```
POST /auth/user/verify-code
{
  "code": "12345"
}
```

### 3. Create Session
After verification, user receives session access to manage features.

---

## 💎 Gem System

### Payment Process
1. User requests gems: `POST /payment/buy-gems`
2. Gets bank details for transfer
3. Uploads receipt image: `POST /payment/{id}/upload-receipt`
4. Admin approves in dashboard
5. Gems added to account

### Gem Deduction
- Gems consumed per hour when self-bot is active
- Configurable in admin settings
- Automatically stops when gems run out

---

## 🎮 API Endpoints

### Authentication
```
POST /auth/admin/login           - Admin login
POST /auth/user/register         - User registration
POST /auth/user/verify-code      - Verify SMS code
POST /auth/admin/logout          - Admin logout
```

### Admin
```
GET  /admin/dashboard            - View dashboard
GET  /admin/users                - List all users
GET  /admin/payments             - List pending payments
POST /admin/payment/{id}/approve - Approve payment
POST /admin/payment/{id}/reject  - Reject payment
POST /admin/user/{id}/gems       - Add gems to user
GET  /admin/settings             - Get admin settings
POST /admin/settings             - Update admin settings
```

### User Features
```
POST /user/{id}/text-format      - Toggle text formatting
POST /user/{id}/media-lock       - Toggle media lock
POST /user/{id}/status-action    - Toggle status display
POST /user/{id}/translation      - Toggle auto-translation
POST /user/{id}/comment          - Set comment text
POST /user/{id}/secretary        - Set auto-reply
POST /user/{id}/anti-login       - Toggle anti-login
POST /user/{id}/auto-reaction    - Set auto-reaction emoji
POST /user/{id}/pv-lock          - Toggle PV lock
POST /user/{id}/copy-profile     - Toggle profile copy protection
POST /user/{id}/animations       - Toggle animation presets
```

### Lists Management
```
GET  /user/{id}/enemy-list       - Get enemy list
POST /user/{id}/enemy-list       - Add/update enemy
DELETE /user/{id}/enemy-list     - Remove enemy

GET  /user/{id}/friend-list      - Get friend list
POST /user/{id}/friend-list      - Add/update friend
DELETE /user/{id}/friend-list    - Remove friend

GET  /user/{id}/crush-list       - Get crush list
POST /user/{id}/crush-list       - Add/update crush
DELETE /user/{id}/crush-list     - Remove crush
```

### Payment
```
POST /payment/buy-gems           - Create payment request
POST /payment/{id}/upload-receipt - Upload receipt image
GET  /payment/{id}/status        - Get payment status
```

---

## 🏗️ Project Structure

```
selfpython/
├── app.py                    # Flask application factory
├── config.py                # Configuration settings
├── models.py                # Database models
├── routes.py                # API routes and endpoints
├── payment_handler.py        # Payment and gem management
├── self.py                  # Self-bot handler
├── telegram_auth.py         # Telegram authentication
├── utils.py                 # Utility functions
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── templates/
│   ├── admin_login.html     # Admin login page
│   └── admin_dashboard.html # Admin dashboard
└── README.md               # This file
```

---

## 🔧 Configuration

### Gem Settings
```env
GEM_PRICE_TOMAN=40              # Price per gem in Toman
MINIMUM_GEMS=80                 # Minimum gems to activate self
GEMS_PER_HOUR=2                 # Gems consumed per hour
```

### Subscription Requirements
```env
REQUIRE_CHANNEL_SUBSCRIBE=true
SUBSCRIPTION_CHANNEL=@your_channel
```

### Security
```env
SESSION_COOKIE_SECURE=false     # Set to true in production
SESSION_COOKIE_HTTPONLY=true    # Always true for security
```

---

## 🛡️ Security Notes

⚠️ **Important for Production:**

1. Change `ADMIN_PASSWORD` in `.env`
2. Change `SECRET_KEY` to a secure random string
3. Set `SESSION_COOKIE_SECURE=true` (requires HTTPS)
4. Use environment variables for sensitive data
5. Never commit `.env` file to git
6. Use a proper database (PostgreSQL) instead of SQLite
7. Enable CORS properly with trusted origins only

---

## 🐛 Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### "Database is locked"
- Other instance of app running
- Close and restart: `python app.py`

### Telegram API errors
- Verify `API_ID` and `API_HASH` are correct
- Check internet connection
- Ensure account is not restricted

### Port already in use
```bash
# Change port in app.py last line:
app.run(debug=True, host='0.0.0.0', port=5001)  # or another port
```

---

## 📞 Support

For issues and suggestions:
- Check logs in terminal for error messages
- Verify all `.env` variables are set correctly
- Ensure database file has write permissions

---

## 📄 License

This project is created for Telegram self-account automation.

---

## ✨ Version

**DARK SELF BOT v1.0.0**

Made with ❤️

---

**Last Updated:** February 20, 2026
