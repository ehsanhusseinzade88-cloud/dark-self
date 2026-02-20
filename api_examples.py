"""
Dark Self Bot - API Usage Examples
These examples show how to interact with the bot API
"""

import requests
import json

# Base URL
BASE_URL = "http://localhost:5000"

# ============= INITIALIZATION =============
print("""
╔═══════════════════════════════════════════════╗
║  🌟 Dark Self Bot - API Usage Examples 🌟   ║
╚═══════════════════════════════════════════════╝
""")

# ============= ADMIN LOGIN =============
print("\n1️⃣ Admin Login\n")

admin_login_response = requests.post(
    f"{BASE_URL}/auth/admin/login",
    json={
        "username": "admin",
        "password": "admin123"
    }
)

print(f"Status: {admin_login_response.status_code}")
print(f"Response: {admin_login_response.json()}")
print("💡 Tip: Set your session cookie from the response")

# ============= USER REGISTRATION =============
print("\n2️⃣ User Registration\n")

user_reg_response = requests.post(
    f"{BASE_URL}/auth/user/register",
    json={
        "phone_number": "+989123456789"
    }
)

print(f"Status: {user_reg_response.status_code}")
user_data = user_reg_response.json()
print(f"Response: {user_data}")

if user_data.get('status') == 'success':
    user_id = user_data.get('user_id')
    print(f"✅ User ID: {user_id}")
else:
    user_id = 1  # Use default for examples

# ============= TEXT FORMATTING =============
print(f"\n3️⃣ Toggle Text Formatting (User {user_id})\n")

text_format_response = requests.post(
    f"{BASE_URL}/user/{user_id}/text-format",
    json={
        "format_type": "bold",
        "enabled": True
    }
)

print(f"Status: {text_format_response.status_code}")
print(f"Response: {text_format_response.json()}")

# Format types available: bold, italic, underline, strikethrough, monospace, spoiler

# ============= AUTO REACTION =============
print(f"\n4️⃣ Set Auto Reaction Emoji (User {user_id})\n")

reaction_response = requests.post(
    f"{BASE_URL}/user/{user_id}/auto-reaction",
    json={
        "emoji": "❤️",
        "enabled": True
    }
)

print(f"Status: {reaction_response.status_code}")
print(f"Response: {reaction_response.json()}")

# ============= MEDIA LOCK =============
print(f"\n5️⃣ Toggle Media Lock (User {user_id})\n")

media_lock_response = requests.post(
    f"{BASE_URL}/user/{user_id}/media-lock",
    json={
        "media_type": "gif",
        "enabled": True
    }
)

print(f"Status: {media_lock_response.status_code}")
print(f"Response: {media_lock_response.json()}")

# Media types: gif, photo, video, voice, sticker, document, audio, video_note, contact, location, emoji, text

# ============= STATUS ACTION =============
print(f"\n6️⃣ Toggle Status Action (User {user_id})\n")

status_response = requests.post(
    f"{BASE_URL}/user/{user_id}/status-action",
    json={
        "action_type": "typing",
        "enabled": True
    }
)

print(f"Status: {status_response.status_code}")
print(f"Response: {status_response.json()}")

# Action types: typing, playing, recording_voice, uploading_photo, uploading_video, choosing_contact

# ============= AUTO TRANSLATION =============
print(f"\n7️⃣ Toggle Translation (User {user_id})\n")

translation_response = requests.post(
    f"{BASE_URL}/user/{user_id}/translation",
    json={
        "language": "english",
        "enabled": True
    }
)

print(f"Status: {translation_response.status_code}")
print(f"Response: {translation_response.json()}")

# Languages: english, chinese, russian, arabic, spanish

# ============= SET COMMENT =============
print(f"\n8️⃣ Set Comment Text (User {user_id})\n")

comment_response = requests.post(
    f"{BASE_URL}/user/{user_id}/comment",
    json={
        "comment_text": "Thanks for forwarding! 🙏",
        "enabled": True
    }
)

print(f"Status: {comment_response.status_code}")
print(f"Response: {comment_response.json()}")

# ============= SET SECRETARY =============
print(f"\n9️⃣ Set Secretary Auto-Reply (User {user_id})\n")

secretary_response = requests.post(
    f"{BASE_URL}/user/{user_id}/secretary",
    json={
        "reply_text": "I'm currently busy, will reply later. 🤖",
        "enabled": True,
        "use_ai": False
    }
)

print(f"Status: {secretary_response.status_code}")
print(f"Response: {secretary_response.json()}")

# ============= MANAGE ENEMY LIST =============
print(f"\n🔟 Manage Enemy List (User {user_id})\n")

enemy_response = requests.post(
    f"{BASE_URL}/user/{user_id}/enemy-list",
    json={
        "target_id": 123456789,
        "target_username": "enemy_user",
    }
)

print(f"Status: {enemy_response.status_code}")
print(f"Response: {enemy_response.json()}")

# ============= MANAGE FRIEND LIST =============
print(f"\n1️⃣1️⃣ Manage Friend List (User {user_id})\n")

friend_response = requests.post(
    f"{BASE_URL}/user/{user_id}/friend-list",
    json={
        "target_id": 987654321,
        "target_username": "friend_user"
    }
)

print(f"Status: {friend_response.status_code}")
print(f"Response: {friend_response.json()}")

# ============= MANAGE CRUSH LIST =============
print(f"\n1️⃣2️⃣ Manage Crush List (User {user_id})\n")

crush_response = requests.post(
    f"{BASE_URL}/user/{user_id}/crush-list",
    json={
        "target_id": 111111111,
        "target_username": "crush_user"
    }
)

print(f"Status: {crush_response.status_code}")
print(f"Response: {crush_response.json()}")

# ============= ANTI LOGIN =============
print(f"\n1️⃣3️⃣ Toggle Anti-Login Protection (User {user_id})\n")

antilogin_response = requests.post(
    f"{BASE_URL}/user/{user_id}/anti-login",
    json={
        "enabled": True
    }
)

print(f"Status: {antilogin_response.status_code}")
print(f"Response: {antilogin_response.json()}")

# ============= ACTIVATE SELF =============
print(f"\n1️⃣4️⃣ Activate Self-Bot (User {user_id})\n")

# First, add some gems to user
# This would normally be done by approving a payment
print("Note: User must have minimum gems to activate self-bot")

# ============= TIME DISPLAY =============
print(f"\n1️⃣5️⃣ Set Time Font (User {user_id})\n")

time_font_response = requests.post(
    f"{BASE_URL}/user/{user_id}/time-font",
    json={
        "font_id": 0  # 0-5 for different font styles
    }
)

print(f"Status: {time_font_response.status_code}")
print(f"Response: {time_font_response.json()}")

# ============= ANIMATION PRESETS =============
print(f"\n1️⃣6️⃣ Toggle Animation Preset (User {user_id})\n")

animation_response = requests.post(
    f"{BASE_URL}/user/{user_id}/animations",
    json={
        "preset_name": "heart",  # heart, love, oclock, star, snow
        "enabled": True
    }
)

print(f"Status: {animation_response.status_code}")
print(f"Response: {animation_response.json()}")

# ============= PAYMENT SYSTEM =============
print(f"\n1️⃣7️⃣ Buy Gems (User {user_id})\n")

buy_gems_response = requests.post(
    f"{BASE_URL}/payment/buy-gems",
    json={
        "user_id": user_id,
        "gem_amount": 100
    }
)

print(f"Status: {buy_gems_response.status_code}")
payment_data = buy_gems_response.json()
print(f"Response: {payment_data}")

if payment_data.get('status') == 'success':
    payment_id = payment_data.get('payment_id')
    print(f"✅ Payment ID: {payment_id}")
    print(f"💳 Amount: {payment_data.get('amount_toman')} Toman")
    print(f"💎 Gems: {payment_data.get('gems')}")

# ============= GET USER PROFILE =============
print(f"\n1️⃣8️⃣ Get User Profile (User {user_id})\n")

profile_response = requests.get(
    f"{BASE_URL}/user/{user_id}/profile"
)

print(f"Status: {profile_response.status_code}")
print(f"Response: {json.dumps(profile_response.json(), indent=2)}")

# ============= GET ALL USERS (ADMIN) =============
print(f"\n1️⃣9️⃣ Get All Users (Admin Only)\n")

users_response = requests.get(
    f"{BASE_URL}/admin/users"
)

print(f"Status: {users_response.status_code}")
users_data = users_response.json()
print(f"Total users: {len(users_data.get('users', []))}")
if users_data.get('users'):
    print(f"First user: {users_data['users'][0]}")

# ============= GET PENDING PAYMENTS (ADMIN) =============
print(f"\n2️⃣0️⃣ Get Pending Payments (Admin Only)\n")

payments_response = requests.get(
    f"{BASE_URL}/admin/payments"
)

print(f"Status: {payments_response.status_code}")
payments_data = payments_response.json()
print(f"Pending payments: {len(payments_data.get('payments', []))}")

print("""
╔═══════════════════════════════════════════════╗
║         ✅ Test Completed Successfully       ║
╚═══════════════════════════════════════════════╝

📖 For more examples and documentation, see README.md

🚀 API is ready to use!
""")
