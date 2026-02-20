from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import os
from dotenv import load_dotenv

load_dotenv()

# API credentials
API_ID = int(os.getenv('API_ID', '9536480'))
API_HASH = os.getenv('API_HASH', '4e52f6f12c47a0da918009260b6e3d44')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8294693574:AAHFBuO6qlrBkAEEo0zFq0ViN26GfLuIEUU')

class TelegramAuth:
    def __init__(self, phone_number, session_name='user_session'):
        self.phone_number = phone_number
        self.session_name = session_name
        self.client = None
    
    async def start_login(self):
        """Start the login process"""
        self.client = TelegramClient(self.session_name, API_ID, API_HASH)
        await self.client.connect()
        
        if not await self.client.is_user_authorized():
            phone_code_hash = await self.client.send_code_request(self.phone_number)
            return {
                'status': 'code_required',
                'phone_code_hash': phone_code_hash,
                'phone_number': self.phone_number
            }
        else:
            return {
                'status': 'already_authorized',
                'message': 'User is already authorized'
            }
    
    async def verify_code(self, code, phone_code_hash):
        """Verify the code sent to phone"""
        try:
            await self.client.sign_in(self.phone_number, code, phone_hash=phone_code_hash)
            return {
                'status': 'success',
                'message': 'Code verified successfully'
            }
        except SessionPasswordNeededError:
            return {
                'status': 'password_required',
                'message': '2FA password is required'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def verify_password(self, password):
        """Verify the 2FA password"""
        try:
            await self.client.sign_in(password=password)
            return {
                'status': 'success',
                'message': 'Password verified successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    async def get_session_string(self):
        """Get the session string for future use"""
        if self.client and await self.client.is_user_authorized():
            return str(self.client.session)
        return None
    
    async def disconnect(self):
        """Disconnect the client"""
        if self.client:
            await self.client.disconnect()


class UserSessionManager:
    """Manage user Telegram sessions"""
    
    def __init__(self):
        self.active_sessions = {}
    
    async def create_session(self, user_id, session_string):
        """Create a new session from stored session string"""
        try:
            client = TelegramClient(f'session_{user_id}', API_ID, API_HASH)
            # Load session from string
            if session_string:
                # Implement session loading logic
                pass
            
            await client.connect()
            self.active_sessions[user_id] = client
            return client
        except Exception as e:
            raise Exception(f"Failed to create session: {str(e)}")
    
    async def get_session(self, user_id):
        """Get active session for user"""
        return self.active_sessions.get(user_id)
    
    async def remove_session(self, user_id):
        """Remove session for user"""
        if user_id in self.active_sessions:
            client = self.active_sessions[user_id]
            await client.disconnect()
            del self.active_sessions[user_id]
    
    async def is_session_active(self, user_id):
        """Check if session is active"""
        return user_id in self.active_sessions
