"""
Dark Self Bot - Core handler for Telegram user account automation
Handles all self-bot features like formatting, reactions, auto-replies, etc.
"""

from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeFilename
import asyncio
import logging
from datetime import datetime
from models import (
    db, User, UserSession, UserTextFormat, UserMediaLock, UserStatusAction,
    UserTranslation, UserComment, UserSecretary, UserAntiLogin, UserAutoReaction,
    UserLearning, UserBlock, UserMute, UserAnimationPreset, EnemyList, FriendList, CrushList
)
from utils import (
    format_iran_time, get_jalali_date, get_gregorian_date, CHAR_MAP,
    apply_text_format, reverse_text, FONTS
)
from google.cloud import translate_v2
import os
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SelfBotHandler:
    """Main handler for all self-bot features"""
    
    def __init__(self, user_id, session_string, api_id, api_hash):
        self.user_id = user_id
        self.session_string = session_string
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.user = None
        
    async def initialize(self):
        """Initialize the client"""
        try:
            self.client = TelegramClient(
                f'session_{self.user_id}',
                self.api_id,
                self.api_hash
            )
            await self.client.connect()
            self.user = User.query.get(self.user_id)
            
            # Register message handler
            self.client.add_event_handler(
                self.handle_message,
                events.NewMessage(outgoing=True)
            )
            logger.info(f"SelfBot initialized for user {self.user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize SelfBot: {str(e)}")
            return False
    
    async def handle_message(self, event):
        """Handle outgoing messages"""
        try:
            message = event.message
            
            # Apply text formatting
            await self.apply_formatting(message)
            
            # Add auto-reactions
            await self.add_auto_reaction(message)
            
            # Send comments on forwarded messages
            await self.send_comment(message)
            
            # Process animation presets
            await self.process_animations(message)
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def apply_formatting(self, message):
        """Apply selected text formatting to messages"""
        if not message.text:
            return
            
        try:
            text = message.text
            
            # Get all enabled formats
            formats = UserTextFormat.query.filter_by(
                user_id=self.user_id,
                is_enabled=True
            ).all()
            
            for fmt in formats:
                text = apply_text_format(text, fmt.format_type)
            
            # Update message if formatting was applied
            if text != message.text:
                await message.edit(text)
                
        except Exception as e:
            logger.error(f"Error applying formatting: {str(e)}")
    
    async def add_auto_reaction(self, message):
        """Add auto-reaction emoji to messages"""
        try:
            reaction = UserAutoReaction.query.filter_by(
                user_id=self.user_id,
                is_enabled=True
            ).first()
            
            if reaction:
                await message.react(reaction.emoji)
                
        except Exception as e:
            logger.error(f"Error adding reaction: {str(e)}")
    
    async def send_comment(self, message):
        """Send comment/reply on forwarded messages"""
        try:
            if message.fwd_from:
                comment = UserComment.query.filter_by(
                    user_id=self.user_id,
                    is_enabled=True
                ).first()
                
                if comment and comment.comment_text:
                    await self.client.send_message(
                        message.chat_id,
                        comment.comment_text
                    )
                    
        except Exception as e:
            logger.error(f"Error sending comment: {str(e)}")
    
    async def process_animations(self, message):
        """Process animation presets in messages"""
        try:
            text = message.text or ""
            
            # Check for animation triggers
            animations = {
                'heart': ['💖', 'قلب', 'heart'],
                'love': ['🎭', 'فان love', 'fun love'],
                'oclock': ['🕐', 'فان oclock', 'fun oclock'],
                'star': ['⭐', 'فان star', 'fun star'],
                'snow': ['❄', 'فان snow', 'fun snow']
            }
            
            for anim_type, triggers in animations.items():
                for trigger in triggers:
                    if trigger in text.lower():
                        preset = UserAnimationPreset.query.filter_by(
                            user_id=self.user_id,
                            preset_name=anim_type,
                            is_enabled=True
                        ).first()
                        
                        if preset:
                            # Add animation effects
                            await self.apply_animation(message, anim_type)
                            
        except Exception as e:
            logger.error(f"Error processing animations: {str(e)}")
    
    async def apply_animation(self, message, anim_type):
        """Apply animation effects to message"""
        try:
            # This would integrate with Telegram's animation capabilities
            pass
        except Exception as e:
            logger.error(f"Error applying animation: {str(e)}")
    
    async def enable_status_action(self, action_type):
        """Enable status action like 'typing', 'playing', etc."""
        try:
            # action_type: typing, playing, recording_voice, uploading_photo, etc
            action_map = {
                'typing': 'typing',
                'playing': 'game',
                'recording_voice': 'record-voice',
                'uploading_photo': 'upload-photo',
                'uploading_video': 'upload-video',
                'choosing_contact': 'choose-contact'
            }
            
            if action_type in action_map:
                # Set action status
                await self.client.send_action(
                    self.user_id,
                    action_map[action_type]
                )
                
        except Exception as e:
            logger.error(f"Error setting status action: {str(e)}")
    
    async def translate_text(self, text, target_language):
        """Translate text to target language"""
        try:
            translate_client = translate_v2.Client()
            result = translate_client.translate_text(
                text,
                target_language=target_language
            )
            return result['translatedText']
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return text
    
    async def block_user(self, user_id):
        """Block a user"""
        try:
            await self.client(BlockUserRequest(id=user_id))
            
            # Save to database
            block = UserBlock(
                user_id=self.user_id,
                target_id=user_id,
                is_enabled=True
            )
            db.session.add(block)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error blocking user: {str(e)}")
    
    async def mute_user(self, user_id):
        """Mute a user"""
        try:
            mute = UserMute(
                user_id=self.user_id,
                target_id=user_id,
                is_enabled=True
            )
            db.session.add(mute)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error muting user: {str(e)}")
    
    async def delete_messages(self, chat_id, message_ids):
        """Delete multiple messages"""
        try:
            await self.client.delete_messages(chat_id, message_ids)
        except Exception as e:
            logger.error(f"Error deleting messages: {str(e)}")
    
    async def save_message(self, message_id, secret=False):
        """Save message to saved messages"""
        try:
            # Get message
            message = await self.client.get_messages('me', ids=message_id)
            
            if secret:
                # Save with reaction instead of forwarding
                await message.react('💾')
            else:
                # Forward to saved messages
                await self.client.forward_messages('me', [message_id], 'me')
                
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
    
    async def repeat_message(self, message_id, count=1, interval=1):
        """Repeat a message multiple times"""
        try:
            message = await self.client.get_messages('me', ids=message_id)
            
            for _ in range(count):
                await self.client.send_message(
                    message.chat_id,
                    message.text or message
                )
                await asyncio.sleep(interval)
                
        except Exception as e:
            logger.error(f"Error repeating message: {str(e)}")
    
    async def manage_enemy_list(self, action, target_id, responses=None):
        """Manage enemy list"""
        try:
            if action == 'add':
                enemy = EnemyList(
                    user_id=self.user_id,
                    target_id=target_id,
                    is_enabled=True,
                    responses=responses or {}
                )
                db.session.add(enemy)
            
            elif action == 'remove':
                EnemyList.query.filter_by(
                    user_id=self.user_id,
                    target_id=target_id
                ).delete()
            
            elif action == 'toggle':
                enemy = EnemyList.query.filter_by(
                    user_id=self.user_id,
                    target_id=target_id
                ).first()
                if enemy:
                    enemy.is_enabled = not enemy.is_enabled
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error managing enemy list: {str(e)}")
    
    async def manage_friend_list(self, action, target_id, responses=None):
        """Manage friend list"""
        try:
            if action == 'add':
                friend = FriendList(
                    user_id=self.user_id,
                    target_id=target_id,
                    is_enabled=True,
                    responses=responses or {}
                )
                db.session.add(friend)
            
            elif action == 'remove':
                FriendList.query.filter_by(
                    user_id=self.user_id,
                    target_id=target_id
                ).delete()
            
            elif action == 'toggle':
                friend = FriendList.query.filter_by(
                    user_id=self.user_id,
                    target_id=target_id
                ).first()
                if friend:
                    friend.is_enabled = not friend.is_enabled
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error managing friend list: {str(e)}")
    
    async def manage_crush_list(self, action, target_id, messages=None):
        """Manage crush list"""
        try:
            if action == 'add':
                crush = CrushList(
                    user_id=self.user_id,
                    target_id=target_id,
                    is_enabled=True,
                    messages=messages or {}
                )
                db.session.add(crush)
            
            elif action == 'remove':
                CrushList.query.filter_by(
                    user_id=self.user_id,
                    target_id=target_id
                ).delete()
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error managing crush list: {str(e)}")
    
    async def enable_time_display(self, location='name', font_id=0):
        """Enable time display in profile or bio"""
        try:
            if location == 'name':
                self.user.time_enabled = True
                self.user.time_font = font_id
            elif location == 'bio':
                self.user.bio_time_enabled = True
                self.user.bio_time_font = font_id
            
            db.session.commit()
            
            # Start updating time in loop
            await self.update_time_loop(location, font_id)
            
        except Exception as e:
            logger.error(f"Error enabling time display: {str(e)}")
    
    async def update_time_loop(self, location, font_id):
        """Continuously update time in profile"""
        try:
            while True:
                time_str = format_iran_time(font_id=font_id)
                
                if location == 'name':
                    # Update first name with time
                    await self.client(EditProfileRequest(
                        first_name=time_str[:64]  # Name limit
                    ))
                elif location == 'bio':
                    # Update bio with time
                    await self.client(EditProfileRequest(
                        about=time_str[:140]  # Bio limit
                    ))
                
                await asyncio.sleep(1)  # Update every second
                
        except Exception as e:
            logger.error(f"Error updating time: {str(e)}")
    
    async def enable_date_display(self, location='bio', date_type='jalali', font_id=0):
        """Enable date display in bio"""
        try:
            self.user.bio_date_enabled = True
            self.user.date_type = date_type
            self.user.bio_time_font = font_id
            db.session.commit()
            
            await self.update_date_loop(date_type, font_id)
            
        except Exception as e:
            logger.error(f"Error enabling date display: {str(e)}")
    
    async def update_date_loop(self, date_type, font_id):
        """Continuously update date in bio"""
        try:
            while True:
                if date_type == 'jalali':
                    date_str = get_jalali_date()
                else:
                    date_str = get_gregorian_date()
                
                # Apply font if needed
                if font_id in CHAR_MAP:
                    char_map = CHAR_MAP[font_id]
                    date_str = ''.join(
                        char_map.get(c, c) for c in date_str
                    )
                
                # Update bio
                await self.client(EditProfileRequest(
                    about=date_str[:140]
                ))
                
                await asyncio.sleep(60)  # Update every minute
                
        except Exception as e:
            logger.error(f"Error updating date: {str(e)}")
    
    async def disconnect(self):
        """Disconnect the client"""
        try:
            if self.client:
                await self.client.disconnect()
                logger.info(f"SelfBot disconnected for user {self.user_id}")
        except Exception as e:
            logger.error(f"Error disconnecting: {str(e)}")


# Global instances dictionary
active_bots = {}


async def start_self_bot(user_id, api_id, api_hash):
    """Start a self-bot for a user"""
    try:
        session = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).first()
        
        if not session:
            logger.error(f"No session found for user {user_id}")
            return False
        
        # Create and initialize handler
        handler = SelfBotHandler(user_id, session.session_string, api_id, api_hash)
        if await handler.initialize():
            active_bots[user_id] = handler
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error starting self-bot: {str(e)}")
        return False


async def stop_self_bot(user_id):
    """Stop a self-bot for a user"""
    try:
        if user_id in active_bots:
            handler = active_bots[user_id]
            await handler.disconnect()
            del active_bots[user_id]
            return True
        return False
    except Exception as e:
        logger.error(f"Error stopping self-bot: {str(e)}")
        return False
